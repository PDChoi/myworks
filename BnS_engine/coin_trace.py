import numpy as np
import math as m
import pandas as pd
import os, sys, time, requests, glob, pickle
import pyupbit as ub
from datetime import datetime, date, timedelta
from matplotlib import pyplot as plt
import hashlib
import time
from urllib.parse import urlencode
import jwt
import requests
import uuid
from coin_func import *

class coin_manager:
    
    def __init__(self, access_key, secret_key, partition = 1, mode = 'trade'):
        self.myLogin = ub.Upbit(access=access_key, secret=secret_key)
        self.initial_gold = m.floor(self.myLogin.get_balance("KRW")/partition )
        self.my_coin_value = 0
        self.coin_time = np.array([])
        self.state = 0
        self.mode = mode
        
        
    def select(self, df_price, df_rt, selected_coin, r0, sec, coin_time_init, t_sampling):
        self.selected_coin = selected_coin
        self.r0 = r0
        self.select_time = sec
        self.coin_time = np.append(self.coin_time, coin_time_init)
        self.t_sampling = t_sampling
        init_time = time.time()
        # r0 = 구매 가격 ==> 이 시점에서 코인 구매
        print('selected coin: ',selected_coin, r0)
        if self.mode == 'trade':
            print(f"Buy coin {selected_coin} : {sec:.2f}sec")
            coin_buy = self.myLogin.buy_market_order(selected_coin, m.floor(self.initial_gold*(1-0.0006))  )
            print(f'Buy coin info= {coin_buy}')
            self.uuid_buy = coin_buy['uuid']
            self.coin_buy = coin_buy
            server_delay = time.time() - init_time
            print(f'server delay {sec}sec: {server_delay} sec ---> buy coin')
        
        self.price_raw = np.array(df_price[selected_coin], dtype='float')
        self.win_avgfilter = 3*int(1/t_sampling)
        self.rt_raw = np.array(df_rt[selected_coin])*100
        self.rt = moving_average( self.rt_raw, self.win_avgfilter)  # need to adjust filter window size
        self.rmax = self.rt[-1]
        self.tmax = self.coin_time[-1]
        self.HighGain = 15
        self.MiddleGain= 10
        self.LowGain = 5
        
        self.r_upper = r0 + 10
        self.r_lower = r0 - 2.5
        self.win_linfit = 3*int(1/t_sampling)
        self.rt_dt1 = np.array([0])
        self.rt_dt2 = np.array([0])
        self.tolerance_RapidDrop_inHighGain = 2.5
        self.tolerance_RapidDrop_inMiddleGain = 2
        self.tolerance_RapidDrop_inLowGain = 1.5

        self.rapid_dropStack = 0
        self.LM_stack = 0
        self.instant_Lmax = np.array([])
        self.instant_Lmax_time = np.array([])
        
        self.rt_dt1 = np.append(self.rt_dt1, np.diff(self.rt)  )
        self.rt_dt2 = np.append(self.rt_dt2, np.diff(self.rt_dt1)  )
        
        self.sec_stop = 0
        self.case = 'tracing'
        self.state = 1
        
        
        
    def trace(self, now_price, now_rt,sec):
        self.coin_time = np.append(self.coin_time, sec)
        self.price_raw = np.append(self.price_raw, now_price)
        self.rt_raw = np.append(self.rt_raw, now_rt)
        
        init_time = time.time()
        if ((self.my_coin_value == 0) and (self.mode == 'trade')):
            self.my_coin_value = self.myLogin.get_balance(ticker=self.selected_coin)
            print(f"current my coin amount [{self.selected_coin}]: ",self.my_coin_value)
            server_delay = time.time() - init_time
            print(f'server delay {sec}sec: {server_delay} sec ---> get my coin value')
            
        self.rt = np.append(self.rt, np.sum(self.rt_raw[-self.win_avgfilter:])/self.win_avgfilter ) 
        self.rt_dt1 = np.append( self.rt_dt1, np.diff(self.rt)[-1] )
        self.rt_dt2 = np.append( self.rt_dt2, np.diff(self.rt_dt1)[-1]  )
        '''
        fundamental principle
        1. when rt reaches r_lower, then immediately sell the coin --> minimize loss
        2. when rmax is renewed, then just pass to next loop 
        3. when rmax is not renewed, make a dicision (pass or stop) --> main part in this code
                                                                    --> how to find local max and local min
        '''
        tp_rmax = self.rt[-1]
        
        # fundamental principle 2
        if tp_rmax >= self.rmax:
            self.rmax = tp_rmax
            self.tmax = sec
            # print(f'renewed Global Max at {sec}sec')
            
        if self.rt_dt1[-1] > 0:
            self.LM_stack = 0 # initialize LM_stack 
            self.rapid_dropStack = 0 # initialize rapid_stack 
            return self.sec_stop
        
        else:
            # 여기서부터 기본적으로 rate <= 0 인 상황
            self.current_gain = self.rt_raw[-1] - self.r0
            self.tolerance_GM = 1.5
            self.tolerance_LM = 0.5
            
            # intant local max check
            range_Instant_Lmax = int(3/self.t_sampling)
            if ( (len(np.where(self.rt_dt1[-range_Instant_Lmax:-1] >=0)[0]) ==range_Instant_Lmax-1)  and (self.rt_dt2[-1] <0) ):
                self.instant_Lmax = np.append(self.instant_Lmax, self.rt[-2])
                self.instant_Lmax_time = np.append(self.instant_Lmax_time, self.coin_time[-2])

                
            ##############################################
            #                                            #
            #            Range in Low Gain               #
            #                                            #
            ##############################################
            if self.current_gain < self.LowGain:
                # steady state local max check
                tolerance_LM = max(0.5, self.rt[-1]/10   )
                range_Steady_Lmax = int(6/self.t_sampling)
                range_convergence_time = int(20/self.t_sampling)
                convergend_limit = self.LowGain/10
                if sec > self.select_time + 5: # select coin 시점부터 5초 지난 후부터 steady local max 판단
                    if( (len(np.where(self.rt_dt1[-range_Steady_Lmax:-1] >=0)[0]) ==range_Steady_Lmax-1)  and (self.rt_dt2[-1] <0) ): 
                        print(f'sec= {sec}  steady state Local Max')

                        # convergence test at steady state Local Max
                        t_range = self.coin_time[-1*range_convergence_time:]
                        t_intersect = np.intersect1d(t_range,self.instant_Lmax_time) 
                        if len(t_intersect) >= 2:
                            mean_Lmax = np.mean( self.instant_Lmax[ max(-len(t_intersect)-1, -len(self.instant_Lmax) ) :-1] )
                            rt_recently = self.rt[-range_convergence_time:]
                            mean_rt_recently = np.mean(rt_recently)
                            if ( (abs(mean_Lmax-self.rt[-2]) < convergend_limit) and ( len(np.where( abs(rt_recently-self.rt[-1]) > convergend_limit )[0]) < int(range_convergence_time/10) ) ):
                                print(f'sec= {sec} ---> converge in steady state Local Max')
                                print("instant local max: ",self.instant_Lmax[ max(-len(t_intersect)-1, -len(self.instant_Lmax) ) :],self.instant_Lmax_time[ max(-len(t_intersect)-1, -len(self.instant_Lmax) ) :])
                                self.sec_stop = sec
                                print(f'stop tracing and sell coin: {sec}sec')
                                print('case: convergence in Low Gain')
                                self.case = 'case: convergence in Low Gain'
                                return self.sec_stop
                                
                        # check local max point: go or stop
                        if self.rt[-2] - self.rt[-1] < tolerance_LM:
                            print('pass : lower than tolerance LM in Low Gain ---> tolerance_LM= ',tolerance_LM)
                            self.LM_stack += 1
                            
                        elif self.rt[-2] - self.rt[-1] >= tolerance_LM:
                            self.sec_stop = sec
                            print(f'stop tracing and sell coin: {sec}sec')
                            print('case: larger than tolerance LM in Low Gain  ---> tolerance_LM= ',tolerance_LM)
                            self.case = f'case: larger than tolerance LM in Low Gain  ---> tolerance_LM= {tolerance_LM}'
                            return self.sec_stop
                
                if self.LM_stack >= 1:
                    self.LM_stack += 1
                    if self.rt[-self.LM_stack-1] - self.rt[-1] > tolerance_LM*2:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: tolerance_LM over in Low Gain')
                        print(self.rt[-self.LM_stack-1],self.rt[-1],tolerance_LM*2)
                        self.case = 'case: tolerance_LM over in Low Gain'
                        return self.sec_stop
                    
                # convergence test at instant state Local Max
                t_range = self.coin_time[-1*range_convergence_time:]
                t_intersect = np.intersect1d(t_range,self.instant_Lmax_time) 
                if len(t_intersect) >= 2:
                    # print('check convergence')
                    mean_Lmax = np.mean( self.instant_Lmax[ max(-len(t_intersect)-1, -len(self.instant_Lmax) ) :-1] )
                    rt_recently = self.rt[-range_convergence_time:]
                    mean_rt_recently = np.mean(rt_recently)
                    if ( (abs(mean_Lmax - self.instant_Lmax[-1]) < convergend_limit) and ( len(np.where( abs(rt_recently-self.rt[-1]) > convergend_limit )[0]) < int(range_convergence_time/10) )  ):
                        print(f'sec= {sec} ---> converge in instant Local Max')
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: convergence in Low Gain')
                        self.case = 'case: convergence in Low Gain'
                        return self.sec_stop
                
                
                # # decreasing rate check: in Low Gain, just check continuous decresing
                tp_toler1 = int(3/self.t_sampling)
                tp_toler2 = tolerance_LM
                if len( np.where( self.rt_dt1[-tp_toler1:] < 0  )[0]  ) >=tp_toler1:
                    print(f'{sec}sec: ',self.rt_dt1[-tp_toler1:])
                    if np.sum(self.rt_dt1[-tp_toler1:]) < -tp_toler2:
                        print(f'sec= {sec}  tp_toler1 --> ', self.rt_dt1[-tp_toler1:]  )
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: tolerance dt1 over in Low Gain')
                        self.case = 'case: tolerance dt1 over in Low Gain'
                        return self.sec_stop

                # raw value rapid change check
                elif self.rt_raw[-1] - self.rt_raw[-2] < -self.tolerance_RapidDrop_inLowGain:
                    self.rapid_dropStack += 1
                    print(f'{sec}sec: rapid stack +1, rapid stack={self.rapid_dropStack}')
                    if self.rapid_dropStack >= 2:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: rapid stack=2 in Low Gain')
                        self.case = 'case: rapid stack=2 in Low Gain'
                        return self.sec_stop
                    
                elif self.rapid_dropStack == 1:
                    if self.rt_raw[-1] - self.rt_raw[-2] > self.tolerance_RapidDrop_inLowGain:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: rapid drop and pop in Low Gain')
                        self.case = 'case: rapid drop and pop in Low Gain'
                        return self.sec_stop
                        
                    elif len(np.where(self.rt_dt1[-2:] <= 0)[0]) == 2:
                        if sec <= self.select_time +5:
                            # rapid_dropStack = 0
                            print(f'pass: rapid stack=1 within {select_time}+5 sec in Low Gain')
                        else:
                            self.sec_stop = sec
                            print(f'stop tracing and sell coin: {sec}sec')
                            print('case: rapid stack=1 in Low Gain')
                            self.case = 'case: rapid stack=1 in Low Gain'
                            return self.sec_stop
                            
                    else:
                        self.rapid_dropStack = 0
                
                tolerance_GM = max(1.5, self.rt[-1]/10)
                if sec < self.select_time+15:
                    tolerance_GM = tolerance_GM*1.5
                # Global max tolerance in Low Gain ==> need to be very sensitive
                if self.rmax - self.rt[-1] > tolerance_GM:
                    if self.rapid_dropStack == 0:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: tolerance_GM over in Low Gain')
                        print([self.rmax,self.tmax], [self.rt[-1], sec], tolerance_GM)
                        self.case = 'case: tolerance_GM over in Low Gain'
                        return self.sec_stop
                        
            ##############################################
            #                                            #
            #         Range in Low < Gain < Middle       #
            #                                            #
            ##############################################
            elif ((self.current_gain >= self.LowGain) and (self.current_gain < self.MiddleGain)):
                # steady state local max check
                tolerance_LM = max(1, self.rt[-1]/20   )
                range_Steady_Lmax = int(6/self.t_sampling)
                range_convergence_time = int(25/self.t_sampling)
                convergend_limit = self.LowGain/10
                if( (len(np.where(self.rt_dt1[-range_Steady_Lmax:-1] >=0)[0]) ==range_Steady_Lmax-1)  and (self.rt_dt2[-1] <0) ): 
                    print(f'sec= {sec}  steady state Local Max')

                    # convergence test at steady state Local Max
                    t_range = self.coin_time[-1*range_convergence_time:]
                    t_intersect = np.intersect1d(t_range,self.instant_Lmax_time) 
                    if len(t_intersect) >= 2:
                        mean_Lmax = np.mean( self.instant_Lmax[ max(-len(t_intersect)-1, -len(self.instant_Lmax) ) :-1] )
                        rt_recently = self.rt[-range_convergence_time:]
                        mean_rt_recently = np.mean(rt_recently)
                        if ( (abs(mean_Lmax-self.rt[-2]) < convergend_limit) and ( len(np.where( abs(rt_recently-self.rt[-1]) > convergend_limit )[0]) < int(range_convergence_time/10) ) ):
                            print(f'sec= {sec} ---> converge in steady state Local Max')
                            print("instant local max: ",self.instant_Lmax[ max(-len(t_intersect)-1, -len(self.instant_Lmax) ) :],self.instant_Lmax_time[ max(-len(t_intersect)-1, -len(self.instant_Lmax) ) :])
                            self.sec_stop = sec
                            print(f'stop tracing and sell coin: {sec}sec')
                            print('case: convergence in (Low, Middle) Gain')
                            self.case = 'case: convergence in (Low, Middle) Gain'
                            
                    # check local max point: go or stop
                    if self.rt[-2] - self.rt[-1] < tolerance_LM:
                        print('pass : lower than tolerance LM in (Low, Middle) Gain ---> tolerance_LM= ',tolerance_LM)
                        self.LM_stack += 1
                        
                    elif self.rt[-2] - self.rt[-1] >= tolerance_LM:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: larger than tolerance LM in (Low, Middle) Gain  ---> tolerance_LM= ',tolerance_LM)
                        self.case = f'case: larger than tolerance LM in (Low, Middle) Gain  ---> tolerance_LM= {tolerance_LM}'
                        
                if self.LM_stack >= 1:
                    self.LM_stack += 1
                    if self.rt[-self.LM_stack-1] - self.rt[-1] > tolerance_LM*2:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: tolerance_LM over in (Low, Middle) Gain')
                        print(self.rt[-self.LM_stack-1],self.rt[-1],tolerance_LM*2)
                        self.case = 'case: tolerance_LM over in (Low, Middle) Gain'
                        return self.sec_stop
                    
                # convergence test at instant state Local Max
                t_range = self.coin_time[-1*range_convergence_time:]
                t_intersect = np.intersect1d(t_range,self.instant_Lmax_time) 
                if len(t_intersect) >= 2:
                    # print('check convergence')
                    mean_Lmax = np.mean( self.instant_Lmax[ max(-len(t_intersect)-1, -len(self.instant_Lmax) ) :-1] )
                    rt_recently = self.rt[-range_convergence_time:]
                    mean_rt_recently = np.mean(rt_recently)
                    if ( (abs(mean_Lmax - self.instant_Lmax[-1]) < convergend_limit) and ( len(np.where( abs(rt_recently-self.rt[-1]) > convergend_limit )[0]) < int(range_convergence_time/10) )  ):
                        print(f'sec= {sec} ---> converge in instant Local Max')
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: convergence in (Low, Middle) Gain')
                        self.case = 'case: convergence in (Low, Middle) Gain'
                        return self.sec_stop
                
                
                # # decreasing rate check: in (Low, Middle) Gain, just check continuous decresing
                tp_toler1 = int(3/self.t_sampling)
                tp_toler2 = tolerance_LM
                if len( np.where( self.rt_dt1[-tp_toler1:] < 0  )[0]  ) >=tp_toler1:
                    print(f'{sec}sec: ',self.rt_dt1[-tp_toler1:])
                    if np.sum(self.rt_dt1[-tp_toler1:]) < -tp_toler2:
                        print(f'sec= {sec}  tp_toler1 --> ', self.rt_dt1[-tp_toler1:]  )
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: tolerance dt1 over in (Low, Middle) Gain')
                        self.case = 'case: tolerance dt1 over in (Low, Middle) Gain'
                        return self.sec_stop

                # raw value rapid change check
                elif self.rt_raw[-1] - self.rt_raw[-2] < -self.tolerance_RapidDrop_inMiddleGain:
                    self.rapid_dropStack += 1
                    print(f'{sec}sec: rapid stack +1, rapid stack={self.rapid_dropStack}')
                    if self.rapid_dropStack >= 2:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: rapid stack=2 in (Low, Middle) Gain')
                        self.case = 'case: rapid stack=2 in (Low, Middle) Gain'
                        return self.sec_stop
                    
                elif self.rapid_dropStack == 1:
                    if self.rt_raw[-1] - self.rt_raw[-2] > self.tolerance_RapidDrop_inMiddleGain:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: rapid drop and pop in (Low, Middle) Gain')
                        self.case = 'case: rapid drop and pop in (Low, Middle) Gain'
                        return self.sec_stop
                        
                    elif len(np.where(self.rt_dt1[-2:] <= 0)[0]) == 2:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: rapid stack=1 in (Low, Middle) Gain')
                        self.case = 'case: rapid stack=1 in (Low, Middle) Gain'
                        return self.sec_stop
                            
                    else:
                        self.rapid_dropStack = 0
                
                tolerance_GM = max(1.5, self.rt[-1]/20)
                if sec < self.select_time+15:
                    tolerance_GM = tolerance_GM*1.5
                # Global max tolerance in Low Gain ==> need to be very sensitive
                if self.rmax - self.rt[-1] > tolerance_GM:
                    if self.rapid_dropStack == 0:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: tolerance_GM over in (Low, Middle) Gain')
                        print([self.rmax,self.tmax], [self.rt[-1], sec], tolerance_GM)
                        self.case = 'case: tolerance_GM over in (Low, Middle) Gain'
                        return self.sec_stop
                    
            #############################################
            #                                           #
            #       Range in Middle < Gain < High       #
            #                                           #
            #############################################
            elif ((self.current_gain >= self.MiddleGain) and (self.current_gain < self.HighGain)):
                # steady state local max check
                tolerance_LM = max(1, self.rt[-1]/20   )
                range_Steady_Lmax = int(6/self.t_sampling)
                range_convergence_time = int(25/self.t_sampling)
                convergend_limit = self.MiddleGain/10
                if( (len(np.where(self.rt_dt1[-range_Steady_Lmax:-1] >=0)[0]) ==range_Steady_Lmax-1)  and (self.rt_dt2[-1] <0) ): 
                    print(f'sec= {sec}  steady state Local Max')

                    # convergence test at steady state Local Max
                    t_range = self.coin_time[-1*range_convergence_time:]
                    t_intersect = np.intersect1d(t_range,self.instant_Lmax_time) 
                    if len(t_intersect) >= 2:
                        mean_Lmax = np.mean( self.instant_Lmax[ max(-len(t_intersect)-1, -len(self.instant_Lmax) ) :-1] )
                        rt_recently = self.rt[-range_convergence_time:]
                        mean_rt_recently = np.mean(rt_recently)
                        if ( (abs(mean_Lmax-self.rt[-2]) < convergend_limit) and ( len(np.where( abs(rt_recently-self.rt[-1]) > convergend_limit )[0]) < int(range_convergence_time/10) ) ):
                            print(f'sec= {sec} ---> converge in steady state Local Max')
                            print("instant local max: ",self.instant_Lmax[ max(-len(t_intersect)-1, -len(self.instant_Lmax) ) :],self.instant_Lmax_time[ max(-len(t_intersect)-1, -len(self.instant_Lmax) ) :])
                            self.sec_stop = sec
                            print(f'stop tracing and sell coin: {sec}sec')
                            print('case: convergence in (Middle, High) Gain')
                            self.case = 'case: convergence in (Middle, High) Gain'
                            
                    # check local max point: go or stop
                    if self.rt[-2] - self.rt[-1] < tolerance_LM:
                        print('pass : lower than tolerance LM in (Middle, High) Gain ---> tolerance_LM= ',tolerance_LM)
                        self.LM_stack += 1
                        
                    elif self.rt[-2] - self.rt[-1] >= tolerance_LM:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: larger than tolerance LM in (Middle, High) Gain  ---> tolerance_LM= ',tolerance_LM)
                        self.case = f'case: larger than tolerance LM in (Middle, High) Gain  ---> tolerance_LM= {tolerance_LM}'
                        
                if self.LM_stack >= 1:
                    self.LM_stack += 1
                    if self.rt[-self.LM_stack-1] - self.rt[-1] > tolerance_LM*2:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: tolerance_LM over in (Middle, High) Gain')
                        print(self.rt[-self.LM_stack-1],self.rt[-1],tolerance_LM*2)
                        self.case = 'case: tolerance_LM over in (Middle, High) Gain'
                        return self.sec_stop
                    
                # convergence test at instant state Local Max
                t_range = self.coin_time[-1*range_convergence_time:]
                t_intersect = np.intersect1d(t_range,self.instant_Lmax_time) 
                if len(t_intersect) >= 2:
                    # print('check convergence')
                    mean_Lmax = np.mean( self.instant_Lmax[ max(-len(t_intersect)-1, -len(self.instant_Lmax) ) :-1] )
                    rt_recently = self.rt[-range_convergence_time:]
                    mean_rt_recently = np.mean(rt_recently)
                    if ( (abs(mean_Lmax - self.instant_Lmax[-1]) < convergend_limit) and ( len(np.where( abs(rt_recently-self.rt[-1]) > convergend_limit )[0]) < int(range_convergence_time/10) )  ):
                        print(f'sec= {sec} ---> converge in instant Local Max')
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: convergence in (Middle, High) Gain')
                        self.case = 'case: convergence in (Middle, High) Gain'
                        return self.sec_stop
                
                
                # # decreasing rate check: in (Middle, High) Gain, just check continuous decresing
                tp_toler1 = int(3/self.t_sampling)
                tp_toler2 = tolerance_LM
                if len( np.where( self.rt_dt1[-tp_toler1:] < 0  )[0]  ) >=tp_toler1:
                    print(f'{sec}sec: ',self.rt_dt1[-tp_toler1:])
                    if np.sum(self.rt_dt1[-tp_toler1:]) < -tp_toler2:
                        print(f'sec= {sec}  tp_toler1 --> ', self.rt_dt1[-tp_toler1:]  )
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: tolerance dt1 over in (Middle, High) Gain')
                        self.case = 'case: tolerance dt1 over in (Middle, High) Gain'
                        return self.sec_stop

                # raw value rapid change check
                elif self.rt_raw[-1] - self.rt_raw[-2] < -self.tolerance_RapidDrop_inMiddleGain:
                    self.rapid_dropStack += 1
                    print(f'{sec}sec: rapid stack +1, rapid stack={self.rapid_dropStack}')
                    if self.rapid_dropStack >= 2:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: rapid stack=2 in (Middle, High) Gain')
                        self.case = 'case: rapid stack=2 in (Middle, High) Gain'
                        return self.sec_stop
                    
                elif self.rapid_dropStack == 1:
                    if self.rt_raw[-1] - self.rt_raw[-2] > self.tolerance_RapidDrop_inMiddleGain:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: rapid drop and pop in (Middle, High) Gain')
                        self.case = 'case: rapid drop and pop in (Middle, High) Gain'
                        return self.sec_stop
                        
                    elif len(np.where(self.rt_dt1[-2:] <= 0)[0]) == 2:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: rapid stack=1 in (Middle, High) Gain')
                        self.case = 'case: rapid stack=1 in (Middle, High) Gain'
                        return self.sec_stop
                            
                    else:
                        self.rapid_dropStack = 0
                
                tolerance_GM = max(1.5, self.rt[-1]/20)
                if sec < self.select_time+15:
                    tolerance_GM = tolerance_GM*1.5
                # Global max tolerance in Low Gain ==> need to be very sensitive
                if self.rmax - self.rt[-1] > tolerance_GM:
                    if self.rapid_dropStack == 0:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: tolerance_GM over in (Middle, High) Gain')
                        print([self.rmax,self.tmax], [self.rt[-1], sec], tolerance_GM)
                        self.case = 'case: tolerance_GM over in (Middle, High) Gain'
                        return self.sec_stop
                    
            ##############################################
            #                                            #
            #           Range in High Gain               #
            #                                            #
            ##############################################
            elif (self.current_gain >= self.HighGain):
                # steady state local max check
                tolerance_LM = max(1, self.rt[-1]/20   )
                range_Steady_Lmax = int(6/self.t_sampling)
                range_convergence_time = int(25/self.t_sampling)
                convergend_limit = self.MiddleGain/10
                if( (len(np.where(self.rt_dt1[-range_Steady_Lmax:-1] >=0)[0]) ==range_Steady_Lmax-1)  and (self.rt_dt2[-1] <0) ): 
                    print(f'sec= {sec}  steady state Local Max')

                    # convergence test at steady state Local Max
                    t_range = self.coin_time[-1*range_convergence_time:]
                    t_intersect = np.intersect1d(t_range,self.instant_Lmax_time) 
                    if len(t_intersect) >= 2:
                        mean_Lmax = np.mean( self.instant_Lmax[ max(-len(t_intersect)-1, -len(self.instant_Lmax) ) :-1] )
                        rt_recently = self.rt[-range_convergence_time:]
                        mean_rt_recently = np.mean(rt_recently)
                        if ( (abs(mean_Lmax-self.rt[-2]) < convergend_limit) and ( len(np.where( abs(rt_recently-self.rt[-1]) > convergend_limit )[0]) < int(range_convergence_time/10) ) ):
                            print(f'sec= {sec} ---> converge in steady state Local Max')
                            print("instant local max: ",self.instant_Lmax[ max(-len(t_intersect)-1, -len(self.instant_Lmax) ) :],self.instant_Lmax_time[ max(-len(t_intersect)-1, -len(self.instant_Lmax) ) :])
                            self.sec_stop = sec
                            print(f'stop tracing and sell coin: {sec}sec')
                            print('case: convergence in High Gain')
                            self.case = 'case: convergence in High Gain'
                            
                    # check local max point: go or stop
                    if self.rt[-2] - self.rt[-1] < tolerance_LM:
                        print('pass : lower than tolerance LM in High Gain ---> tolerance_LM= ',tolerance_LM)
                        self.LM_stack += 1
                        
                    elif self.rt[-2] - self.rt[-1] >= tolerance_LM:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: larger than tolerance LM in High Gain  ---> tolerance_LM= ',tolerance_LM)
                        self.case = f'case: larger than tolerance LM in High Gain  ---> tolerance_LM= {tolerance_LM}'
                        
                if self.LM_stack >= 1:
                    self.LM_stack += 1
                    if self.rt[-self.LM_stack-1] - self.rt[-1] > tolerance_LM*2:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: tolerance_LM over in High Gain')
                        print(self.rt[-self.LM_stack-1],self.rt[-1],tolerance_LM*2)
                        self.case = 'case: tolerance_LM over in High Gain'
                        return self.sec_stop
                    
                # convergence test at instant state Local Max
                t_range = self.coin_time[-1*range_convergence_time:]
                t_intersect = np.intersect1d(t_range,self.instant_Lmax_time) 
                if len(t_intersect) >= 2:
                    # print('check convergence')
                    mean_Lmax = np.mean( self.instant_Lmax[ max(-len(t_intersect)-1, -len(self.instant_Lmax) ) :-1] )
                    rt_recently = self.rt[-range_convergence_time:]
                    mean_rt_recently = np.mean(rt_recently)
                    if ( (abs(mean_Lmax - self.instant_Lmax[-1]) < convergend_limit) and ( len(np.where( abs(rt_recently-self.rt[-1]) > convergend_limit )[0]) < int(range_convergence_time/10) )  ):
                        print(f'sec= {sec} ---> converge in instant Local Max')
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: convergence in High Gain')
                        self.case = 'case: convergence in High Gain'
                        return self.sec_stop
                
                
                # # decreasing rate check: in (Middle, High) Gain, just check continuous decresing
                tp_toler1 = int(3/self.t_sampling)
                tp_toler2 = tolerance_LM
                if len( np.where( self.rt_dt1[-tp_toler1:] < 0  )[0]  ) >=tp_toler1:
                    print(f'{sec}sec: ',self.rt_dt1[-tp_toler1:])
                    if np.sum(self.rt_dt1[-tp_toler1:]) < -tp_toler2:
                        print(f'sec= {sec}  tp_toler1 --> ', self.rt_dt1[-tp_toler1:]  )
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: tolerance dt1 over in High Gain')
                        self.case = 'case: tolerance dt1 over in High Gain'
                        return self.sec_stop

                # raw value rapid change check
                elif self.rt_raw[-1] - self.rt_raw[-2] < -self.tolerance_RapidDrop_inMiddleGain:
                    self.rapid_dropStack += 1
                    print(f'{sec}sec: rapid stack +1, rapid stack={self.rapid_dropStack}')
                    if self.rapid_dropStack >= 2:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: rapid stack=2 in High Gain')
                        self.case = 'case: rapid stack=2 in High Gain'
                        return self.sec_stop
                    
                elif self.rapid_dropStack == 1:
                    if self.rt_raw[-1] - self.rt_raw[-2] > self.tolerance_RapidDrop_inMiddleGain:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: rapid drop and pop in High Gain')
                        self.case = 'case: rapid drop and pop in High Gain'
                        return self.sec_stop
                        
                    elif len(np.where(self.rt_dt1[-2:] <= 0)[0]) == 2:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: rapid stack=1 in High Gain')
                        self.case = 'case: rapid stack=1 in High Gain'
                        return self.sec_stop
                            
                    else:
                        self.rapid_dropStack = 0
                
                tolerance_GM = max(2, self.rt[-1]/15)
                if sec < self.select_time+15:
                    tolerance_GM = tolerance_GM*1.5
                # Global max tolerance in Low Gain ==> need to be very sensitive
                if self.rmax - self.rt[-1] > tolerance_GM:
                    if self.rapid_dropStack == 0:
                        self.sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: tolerance_GM over in High Gain')
                        print([self.rmax,self.tmax], [self.rt[-1], sec], tolerance_GM)
                        self.case = 'case: tolerance_GM over in High Gain'
                        return self.sec_stop
                    
                    
        # fundamental principle 1: minimize loss
        if sec > self.select_time +5:  # ==> 사고나서 4초정도는 지켜보기
            if self.rt[-1] <= self.r_lower:
                self.sec_stop = sec
                print(f'stop tracing and sell coin: {sec}sec')
                print('case: lower limit')
                self.case = 'case: lower limit'
                return self.sec_stop
        return 0
            
            
            
            
            
        
    def close(self,sec):
        if self.mode == 'trade':
            current_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            self.sell_time = current_time
            tp_time = time.time()
            coin_sell =  self.myLogin.sell_market_order(self.selected_coin,self.my_coin_value)
            time.sleep(time.time()-tp_time+0.1)
            print(f"Sell coin {self.selected_coin} at {current_time} : {coin_sell}")
            if len(coin_sell) == 1:
                while 1:
                    print('error: coin sell')
                    print(f"Sell coin {self.selected_coin} : {current_time}")
                    try:
                        tp_time = time.time()
                        coin_sell =  self.myLogin.sell_market_order(self.selected_coin,self.my_coin_value)
                        time.sleep(time.time()-tp_time+0.1)
                        print(coin_sell)
                    except:
                        print('error: coin sell')
                    if len(coin_sell) >= 2:
                        break
            print(coin_sell)
            self.coin_sell = coin_sell
            self.uuid_sell = coin_sell['uuid']
        
        self.rf = self.rt_raw[-1]
        self.gain = (self.rt_raw[-1] - self.r0)/(100+self.r0)*100
        print(f'{self.selected_coin} gain: {self.gain}')
        print(f'End coin trade: {sec}sec')

        
        
        
    def save(self,str_date, report_path, plot_path, coin_dict, start_time, select_time, total_time, total_rt):
        try:
            # get buy_price
            single_order_info = self.myLogin.get_single_order(self.uuid_buy)
            if len(single_order_info) == 1:
                print(f'error: server request delay')
                while 1:
                    try:
                        time.sleep(1)
                        single_order_info = self.myLogin.get_single_order(self.uuid_buy)
                    except:
                        print(f'error: server request delay')
                    if len(single_order_info) > 1:
                        break
            print(single_order_info)
            buy_price = float(single_order_info['trades'][0]['price'])
            print(f"{self.selected_coin} buy price: {buy_price}")
            # get sell_price
            single_order_info = self.myLogin.get_single_order(self.uuid_sell)
            if len(single_order_info) == 1:
                print(f'error: server request delay')
                while 1:
                    try:
                        time.sleep(1)
                        single_order_info = self.myLogin.get_single_order(self.uuid_sell)
                    except:
                        print(f'error: server request delay')
                    if len(single_order_info) > 1:
                        break
            print(single_order_info)
            sell_price = float(single_order_info['trades'][0]['price'])
            print(f"{self.selected_coin} sell_price: {sell_price}")
            
            r0_real = (float(buy_price)-self.price_raw[0])/self.price_raw[0]*100
            rf_real = (float(sell_price)-self.price_raw[0])/self.price_raw[0]*100
            gain_real = (sell_price-buy_price)/buy_price*100
            print(f'{self.selected_coin} Real Gain: {gain_real}')
            time.sleep(1)
            tp_time = time.time()
            final_gold = m.floor(self.myLogin.get_balance("KRW") )
            time.sleep(time.time() - tp_time + 0.1)
            print(f'{self.selected_coin} Final gold: {final_gold} KRW') 
            
            # save data
            total_data ={}
            total_data['initial_gold'] = self.initial_gold
            total_data['coin_time'] = self.coin_time
            total_data['price_raw'] = self.price_raw
            total_data['rt_raw'] = self.rt_raw
            total_data['rt'] = self.rt
            total_data['rt_dt1'] = self.rt_dt1
            total_data['rt_dt2'] = self.rt_dt2
            total_data['case'] = self.case
            total_data['buy_info'] = self.coin_buy
            total_data['sell_info'] = self.coin_sell
            total_data['coin_candidate'] = coin_dict
            
            os.chdir(report_path)
            data_name = f'Results_{self.selected_coin}_{str_date}'
            if os.path.isdir(data_name):
                os.chdir(report_path+f'\\{data_name}')
            else:
                os.mkdir(data_name)
            os.chdir(report_path+f'\\{data_name}')
            with open(f'{data_name}.pckl', 'wb') as d:
                pickle.dump(total_data,d)
            
            # write report 
            with open(f'report_{self.selected_coin}_{str_date}.txt' , 'w') as f:
                f.write(f'Coin: {self.selected_coin}\n')
                f.write(f'start_time: {start_time}\n')
                f.write(f'select_time: {select_time}\n')
                f.write(f'sell_time: {self.sell_time}\n')
                f.write(f'stop_sec: {self.sec_stop}\n')
                f.write(f'Initial gold: {self.initial_gold}\n')
                f.write(f'Final_gold: {final_gold}\n')
                f.write(f'Start price: {self.price_raw[0]}\n')
                f.write(f'Buy price: {buy_price}\n')
                f.write(f'Sell price: {sell_price}\n')
                f.write(f'r0: {self.r0}\n')
                f.write(f'r0_real: {r0_real}\n')
                f.write(f'rf: {self.rf}\n')
                f.write(f'rf_real: {rf_real}\n')
                f.write(f'Gain: {self.gain}\n')
                f.write(f'Gain(Real): {gain_real}\n')
                f.write(f'{self.case}\n')
                
            os.chdir(plot_path)
            plot_name = f'results_{self.selected_coin}_{str_date}.png'
            plot_name2 = f'total_{self.selected_coin}_{str_date}.png'
            
            fig = plt.figure(num=1)
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(800,50,1100, 1250)
            ax1 = fig.add_subplot(3,1,1)
            ax1.clear()
            ax1.plot(self.coin_time,self.rt, 'k*-')
            ax1.plot([self.select_time], [self.r0], 'ro')
            ax1.plot([self.sec_stop], [self.rt_raw[-1]], 'bo'); ax1.grid()
            ax1.set_title(f"rt-{self.selected_coin} : {self.select_time} sec")
            ax2 = fig.add_subplot(3,1,2); ax2.grid()
            ax2.plot(self.coin_time,self.rt_dt1, 'k*-')
            ax2.set_title(f'rt/dt')
            ax3 = fig.add_subplot(3,1,3); ax3.grid()
            ax3.plot(self.coin_time,self.rt_dt2, 'k*-')
            ax3.set_title(f'd/dt(rt/dt)')
            plt.tight_layout()
            plt.savefig(plot_name)
            plt.close()
            
            fig2 = plt.figure(num=2)
            plt.plot(total_time, total_rt, 'k*-')
            plt.plot([self.select_time], [self.r0], 'ro')
            plt.plot([self.sec_stop], [self.rt_raw[-1]], 'bo'); plt.grid()
            plt.title(f"total rt-{self.selected_coin}")
            plt.savefig(plot_name2)
            plt.close()
            
            
        except Exception as x:
            print(x.__class__.__name__)
            return None
            
            
        
        











