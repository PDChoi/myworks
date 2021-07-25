import numpy as np
import math as m
import pandas as pd
import os, sys, time, requests, glob
import pyupbit as ub
from matplotlib import pyplot as plt
from matplotlib import animation as anim
from datetime import datetime, date, timedelta
import hashlib
import time
from urllib.parse import urlencode
import jwt
import requests
import uuid
from coin_func import *
# 추가 할 사항(4/8): GM=LM 감지 순간에서 팔지 말고, totlerance_LM 기준으로 판단
# 추가: LM 상황에서 totlerance_LM 기준으로 다음으로 넘어갈 때, LM_stack 값으로 감소하는 상황 FLAG 세우고
#      --> local_max = rt[-1-LM_stack] 이므로, 이 값 기준으로 totlerance_GM 이내까지는 PASS, 이상이면 즉시 탈출
# 추가 할 사항(4/10): 4/7 기준 데이터, select_time 재선택 필요!! --> select coin mechanism에 추가 해야함.


# path
home_path = "C:\\Users\\Jk-home1\\Desktop\\python\\Coin_trade"
data_path ="C:\\Users\\Jk-home1\\Desktop\\python\\Coin_trade\\data"
os.chdir(home_path)
os.chdir(data_path)
date_list = [411, 410, 49,48,47, 46,45,44,43,42,41,331,330,329,328,325,324,323,322,321,320]
date_list = [ 411 ]
total_gain = {}
total_gain_avg = {}
total_additive_gain = 0
total_multiplicative_gain = 1
for date in date_list:
    date_str = str(date)
    # date = 44 # --> select date
    data_file = glob.glob(f'total_price_Data_{date}*'); data_file=data_file[0] # --> training data file
    print('Data file = {data_file}')
    data_price = pd.read_csv(data_file)
    data_price = data_price.drop(['Unnamed: 0'],axis=1)
    # print(data_price)
    #################
    # get coin data #
    #################
    time_limit = len( data_price['KRW-BTC']) - 1
    select_time = 10
    gain_day=[]
    for idx in range(5):
        sec = 0
        coin_idx = idx
        while 1:
            # print(sec)
            if sec == 0:
                tp_dict = dict(data_price.loc[sec])
                df_price = pd.DataFrame( [tp_dict.values()], columns=tp_dict.keys() )
                df_rt = get_current_rate(df_price, sec)

            elif sec < select_time:
                tp_dict = dict(data_price.loc[sec])
                df_price = df_price.append( pd.DataFrame( [tp_dict.values()], columns=tp_dict.keys() )   )
                df_price = df_price.reset_index(drop=True)
                
                temp_rate = get_current_rate(df_price, sec)
                df_rt = df_rt.append( temp_rate )
                df_rt = df_rt.reset_index(drop=True)
                # print(sec)
            elif sec >= select_time:
                # print(sec)
                tp_dict = dict(data_price.loc[sec])
                df_price = df_price.append( pd.DataFrame( [tp_dict.values()], columns=tp_dict.keys() )   )
                df_price = df_price.reset_index(drop=True)
                
                temp_rate = get_current_rate(df_price, sec)
                df_rt = df_rt.append( temp_rate )
                df_rt = df_rt.reset_index(drop=True)
                # print(df_price)
                # print(df_rt)
                if sec == select_time:
                    '''
                    Here, select coin and trace it
                    ########################
                    # parameter definition #
                    ########################
                    rt: real-time price (normalized)
                    rt_dt1: d/dt(rt) --> first derivative of rt (applied to averge filter with win_size = filter window size)
                    rt_dt2: d/dt(dr/dt) --> second derivative of rt_dt1 (applied to averge filter)
                    r0 : purchase price
                    rmax : global maximum of rt,  tmax: time at rmax
                    r_lower : loss limit
                    '''
                    argmax_list = []
                    r0_list = []
                    win_avgfilter = 3
                    coin_dict = {}
                    # print(df_rt)
                    df_tp = df_rt
                    # search and select good coin
                    for n in range(5):
                        argmax_tp = df_tp.loc[sec].idxmax(axis=1)
                        test_rt = np.array(df_rt[argmax_tp])*100
                        score = selection_coin_v2(argmax_tp,test_rt)
                        coin_dict[argmax_tp] = score
                        df_tp = df_tp.drop(argmax_tp, axis=1)

                    coin_dict = sorted(coin_dict.items(),key=(lambda x:x[1]), reverse=True)
                    # print(coin_dict)
                    for n in range(5):
                        key = coin_dict[n][0]
                        # print(key)
                        argmax_list.append(key)
                        r0_tp = round(df_rt[key].loc[sec]*100,2)
                        r0_list.append(r0_tp)
                        
                    print(argmax_list,r0_list)
                    # ---> 여기서 coin selection 과정 한번 더 거쳐서 5개중의 최선의 3개를 선택
                    # coin_idx = 1

                    selected_coin = argmax_list[coin_idx] ; r0 = r0_list[coin_idx] # r0 = 구매 가격 ==> 이 시점에서 코인 구매
                    print('selected coin: ',selected_coin, r0)
                    rt_raw = np.array(df_rt[selected_coin])*100
                    rt = moving_average( rt_raw, win_avgfilter)  # need to adjust filter window size
                    rmax = np.max(rt)
                    tmax = sec
                    HighGain = 15
                    MiddleGain= 10
                    LowGain = 5
                    
                    r_upper = r0 + 10
                    r_lower = r0 - 2.5
                    win_linfit = 3
                    rt_dt1 = np.array([0])
                    rt_dt2 = np.array([0])
                    tolerance_RapidDrop_inHighGain = 2.5
                    tolerance_RapidDrop_inMiddleGain = 2
                    tolerance_RapidDrop_inLowGain = 1.5
                    tolerance_dt1 = 5
                    tolerance_dt2 = 0.5
                    rapid_dropStack = 0
                    LM_stack = 0
                    instant_Lmax = np.array([])
                    instant_Lmax_time = np.array([])
                    # for n in range(2,len(rt)+1):
                    #     tp = get_current_linfit( rt[0:n],win_linfit)
                    #     rt_dt1 = np.append(rt_dt1,tp)
                    # for n in range(2,len(rt_dt1)+1):
                    #     tp = get_current_linfit( rt_dt1[0:n],win_linfit)
                    #     rt_dt2 = np.append(rt_dt2, tp)
                        
                    rt_dt1 = np.append(rt_dt1, np.diff(rt)  )
                    rt_dt2 = np.append(rt_dt2, np.diff(rt_dt1)  )
                    # break
                elif sec >select_time:
                    # print('trace coin data')
                    # update data
                    init_time = time.time()
                    rt_raw = np.array(df_rt[selected_coin])*100
                    rt = np.append( rt, np.sum(rt_raw[-win_avgfilter:])/win_avgfilter  ) 
                    # rt_dt1 = np.append( rt_dt1, get_current_linfit(rt,win_linfit) )
                    # rt_dt2 = np.append( rt_dt2, get_current_linfit(rt_dt1,win_linfit) )
                    

                    rt_dt1 = np.append( rt_dt1, np.diff(rt)[-1] )
                    rt_dt2 = np.append( rt_dt2, np.diff(rt_dt1)[-1]  )
                    '''
                    fundamental principle
                    1. when rt reaches r_lower, then immediately sell the coin --> minimize loss
                    2. when rmax is renewed, then just pass to next loop 
                    3. when rmax is not renewed, make a dicision (pass or stop) --> main part in this code
                                                                                --> how to find local max and local min
                    '''

                    
                    tp_rmax = rt[-1]
                    
            
                    # fundamental principle 2
                    if tp_rmax >= rmax:
                        rmax = tp_rmax
                        tmax = sec
                        # print(f'renewed Global Max at {sec}sec')
                        
                    if rt_dt1[-1] > 0:
                        LM_stack = 0 # initialize LM_stack 
                        rapid_dropStack = 0 # initialize rapid_stack 
                        pass
                    
                    else:
                        # 여기서부터 기본적으로 rate <= 0 인 상황
                        current_gain = rt_raw[-1] - r0
                        tolerance_GM = 1.5
                        tolerance_LM = 0.5
                        
                        # intant local max check
                        range_Instant_Lmax = 3
                        if ( (len(np.where(rt_dt1[-range_Instant_Lmax:-1] >=0)[0]) ==range_Instant_Lmax-1)  and (rt_dt2[-1] <0) ):
                            instant_Lmax = np.append(instant_Lmax, rt[-2])
                            instant_Lmax_time = np.append(instant_Lmax_time, sec-1)
                            # print("instant local max")
                            # print(instant_Lmax,instant_Lmax_time)
                        
                        ##############################################
                        #            Range in Low Gain               #
                        ##############################################
                        if current_gain < LowGain:
                            # steady state local max check
                            tolerance_LM = max(0.5, rt[-1]/10   )
                            range_Steady_Lmax = 6
                            range_convergence_time = 20
                            convergend_limit = LowGain/10
                            tolerance_gain = 3
                            if sec > select_time +4:
                                if( (len(np.where(rt_dt1[-range_Steady_Lmax:-1] >=0)[0]) ==range_Steady_Lmax-1)  and (rt_dt2[-1] <0) ): 
                                    print(f'sec= {sec}  steady state Local Max')

                                    # convergence test at steady state Local Max
                                    t_range = np.round(np.linspace(max(sec-range_convergence_time,0),sec,sec-max(sec-range_convergence_time,0)+1))
                                    t_intersect = np.intersect1d(t_range,instant_Lmax_time) 
                                    if len(t_intersect) >= 2:
                                        mean_Lmax = np.mean( instant_Lmax[ max(-len(t_intersect)-1, -len(instant_Lmax) ) :-1] )
                                        rt_recently = rt[max(sec-range_convergence_time,0):]
                                        mean_rt_recently = np.mean(rt_recently)
                                        if ( (abs(mean_Lmax-rt[-2]) < convergend_limit) and ( len(np.where( abs(rt_recently-rt[-1]) > convergend_limit )[0]) < int(range_convergence_time/10) ) ):
                                            print(f'sec= {sec} ---> converge in steady state Local Max')
                                            print("instant local max: ",instant_Lmax[ max(-len(t_intersect)-1, -len(instant_Lmax) ) :],instant_Lmax_time[ max(-len(t_intersect)-1, -len(instant_Lmax) ) :])
                                            sec_stop = sec
                                            print(f'stop tracing and sell coin: {sec}sec')
                                            print('case: convergence in Low Gain')
                                            break
                                    # check local max point: go or stop
                                    if rt[-2] - rt[-1] < tolerance_LM:
                                        print('pass : lower than tolerance LM in Low Gain ---> tolerance_LM= ',tolerance_LM)
                                        LM_stack += 1
                                        
                                    elif rt[-2] - rt[-1] >= tolerance_LM:
                                        sec_stop = sec
                                        print(f'stop tracing and sell coin: {sec}sec')
                                        print('case: larger than tolerance LM in Low Gain  ---> tolerance_LM= ',tolerance_LM)
                                        break
                            
                            if LM_stack >= 1:
                                LM_stack += 1
                                if rt[-LM_stack-1] - rt[-1] > tolerance_LM*2:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: tolerance_LM over in Low Gain')
                                    print(rt[-LM_stack-1],rt[-1],tolerance_LM*2)
                                    break
                                
                            # convergence test at instant state Local Max
                            t_range = np.round(np.linspace(max(sec-range_convergence_time,0),sec,sec-max(sec-range_convergence_time,0)+1))
                            t_intersect = np.intersect1d(t_range,instant_Lmax_time) 
                            if len(t_intersect) >= 2:
                                # print('check convergence')
                                mean_Lmax = np.mean( instant_Lmax[ max(-len(t_intersect)-1, -len(instant_Lmax) ) :-1] )
                                rt_recently = rt[max(sec-range_convergence_time,0):]
                                mean_rt_recently = np.mean(rt_recently)
                                if ( (abs(mean_Lmax - instant_Lmax[-1]) < convergend_limit) and ( len(np.where( abs(rt_recently-rt[-1]) > convergend_limit )[0]) < int(range_convergence_time/10) )  ):
                                    print(f'sec= {sec} ---> converge in instant Local Max')
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: convergence in Low Gain')
                                    break
                            
                            
                            # # decreasing rate check: in Low Gain, just check continuous decresing
                            # tp_toler1 = 5
                            # # tp_toler2 = 0.1
                            # if len( np.where( rt_dt1[-tp_toler1:] < 0  )[0]  ) >=tp_toler1:
                            #     print(f'sec= {sec}  tp_toler1 --> ', rt_dt1[-tp_toler1:]  )
                            #     sec_stop = sec
                            #     print(f'stop tracing and sell coin: {sec}sec')
                            #     print('case: tolerance dt1 over in LowGain')
                            #     break

                            # raw value rapid change check
                            elif rt_raw[-1] - rt_raw[-2] < -tolerance_RapidDrop_inLowGain:
                                rapid_dropStack += 1
                                print(f'{sec}sec: rapid stack +1, rapid stack={rapid_dropStack}')
                                if rapid_dropStack >= 2:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: rapid stack=2 in Low Gain')
                                    break
                            elif rapid_dropStack == 1:
                                if rt_raw[-1] - rt_raw[-2] > tolerance_RapidDrop_inLowGain:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: rapid drop and pop in Low Gain')
                                    break
                                elif len(np.where(rt_dt1[-2:] <= 0)[0]) == 2:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: rapid stack=1 in Low Gain')
                                    break
                                else:
                                    rapid_dropStack = 0
                            
                            tolerance_GM = max(1, rt[-1]/10)
                            if sec < 25:
                                tolerance_GM = tolerance_GM*2
                            # Global max tolerance in Low Gain ==> need to be very sensitive
                            if rmax - rt[-1] > tolerance_GM:
                                if rapid_dropStack == 0:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: tolerance_GM over in Low Gain')
                                    print([rmax,tmax], [rt[-1], sec], tolerance_GM)
                                    break
                            
                        ##############################################
                        #         Range in Low < Gain < Middle       #
                        ##############################################
                        elif ((current_gain >= LowGain) and (current_gain < MiddleGain)):
                            tolerance_LM = max(1, rt[-1]/20  )
                            range_Steady_Lmax = 6
                            range_convergence_time = 25
                            convergend_limit = LowGain/10
                            if( (len(np.where(rt_dt1[-range_Steady_Lmax:-1] >=0)[0]) ==range_Steady_Lmax-1)  and (rt_dt2[-1] <0) ): 
                                print(f'sec= {sec}  steady state Local Max')

                                t_range = np.round(np.linspace(max(sec-range_convergence_time,0),sec,sec-max(sec-range_convergence_time,0)+1))
                                t_intersect = np.intersect1d(t_range,instant_Lmax_time) 
                                if len(t_intersect) >= 2:
                                    mean_Lmax = np.mean( instant_Lmax[ max(-len(t_intersect)-1, -len(instant_Lmax) ) :-1] )
                                    if mean_Lmax < convergend_limit:
                                        print(f'sec= {sec} ---> converge in steady state Local Max')
                                        print("instant local max: ",instant_Lmax[ max(-len(t_intersect)-1, -len(instant_Lmax) ) :],instant_Lmax_time[ max(-len(t_intersect)-1, -len(instant_Lmax) ) :])
                                        sec_stop = sec
                                        print(f'stop tracing and sell coin: {sec}sec')
                                        print('case: convergence in (Low, Middle) Gain')
                                        break
                                
                                
                                if rt[-2] - rt[-1] < tolerance_LM:
                                        print('pass : lower than tolerance LM in (Low, Middle) Gain')
                                        LM_stack += 1
                                        
                                elif rt[-2] - rt[-1] >= tolerance_LM:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: larger than tolerance LM in (Low, Middle) Gain ---> tolerance_LM= ',tolerance_LM)
                                    break
                            
                            if LM_stack >= 1:
                                LM_stack += 1
                                if rt[-LM_stack-1] - rt[-1] > tolerance_LM*2:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: tolerance_LM over in (Low, Middle) Gain')
                                    print(rt[-LM_stack-1],rt[-1],tolerance_LM*2)
                                    break

                            tp_toler1 = 3
                            tp_toler2 = 0.1
                            if len( np.where( rt_dt1[-tp_toler1:] < -tp_toler2  )[0]  ) >=tp_toler1:
                                if get_current_linfit(rt_dt2[-tp_toler1:], tp_toler1) < 0:
                                    print(f'sec= {sec}  tp_toler1 --> ', rt_dt1[-tp_toler1:]  )
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: tolerance dt1 over in (Low, Middle) Gain')
                                    break

                            elif rt_raw[-1] - rt_raw[-2] < -tolerance_RapidDrop_inMiddleGain:
                                rapid_dropStack += 1
                                print(f'{sec}sec: rapid stack +1')
                                if rapid_dropStack >= 2:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: rapid stack=2 in (Low, Middle) Gain')
                                    break
                            elif rapid_dropStack == 1:
                                if rt_raw[-1] - rt_raw[-2] > tolerance_RapidDrop_inMiddleGain:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: rapid drop and pop in (Low, Middle) Gain')
                                    break
                                elif len(np.where(rt_dt1[-2:] < 0)[0]) == 2:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: rapid stack=1 in (Low, Middle) Gain')
                                    break
                                else:
                                    rapid_dropStack = 0
                            
                            tolerance_GM = max(1.5, rt[-1]/20)
                            # Global max tolerance 
                            if rmax - rt[-1] > tolerance_GM:
                                sec_stop = sec
                                print(f'stop tracing and sell coin: {sec}sec')
                                print('case: tolerance_GM over in (Low, Middle) Gain')
                                print([rmax,tmax], [rt[-1], sec], tolerance_GM)
                                break
                                    
                        ##############################################
                        #        Range in Middle < Gain < High       #
                        ##############################################
                        elif ((current_gain >= MiddleGain) and (current_gain < HighGain)) :
                            # find convergence
                            tolerance_LM = max(1, rt[-1]/20  )
                            range_Steady_Lmax = 6
                            range_convergence_time = 25
                            convergend_limit = MiddleGain/10
                            if( (len(np.where(rt_dt1[-range_Steady_Lmax:-1] >=0)[0]) ==range_Steady_Lmax-1)  and (rt_dt2[-1] <0) ): 
                                print(f'sec= {sec}  steady state Local Max')
                                t_range = np.linspace(sec-3,sec,4)
                                print(tmax, rt[tmax] ,current_gain)
                                t_range = np.round(np.linspace(max(sec-range_convergence_time,0),sec,sec-max(sec-range_convergence_time,0)+1))
                                t_intersect = np.intersect1d(t_range,instant_Lmax_time) 
                                if len(t_intersect) >= 2:
                                    mean_Lmax = np.mean( instant_Lmax[ max(-len(t_intersect)-1, -len(instant_Lmax) ) :-1] )
                                    if mean_Lmax < convergend_limit:
                                        print(f'sec= {sec} converge --> steady state Local Max')
                                        print("instant local max: ",instant_Lmax[ max(-len(t_intersect)-1, -len(instant_Lmax) ) :],instant_Lmax_time[ max(-len(t_intersect)-1, -len(instant_Lmax) ) :])
                                        sec_stop = sec
                                        print(f'stop tracing and sell coin: {sec}sec')
                                        print('case: convergence in (Middle, High) Gain')
                                        break
                                if rt[-2] - rt[-1] < tolerance_LM:
                                        print('pass : lower than tolerance LM in (Middle, High) Gain')
                                        LM_stack += 1
                                        pass
                                elif rt[-2] - rt[-1] >= tolerance_LM:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: larger than tolerance LM in (Middle, High) Gain ---> tolerance_LM= ',tolerance_LM)
                                    break
                            
                            if LM_stack >= 1:
                                LM_stack += 1
                                if rt[-LM_stack-1] - rt[-1] > tolerance_LM*2:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: tolerance_LM over in (Middle, High) Gain')
                                    print(rt[-LM_stack-1],rt[-1],tolerance_LM*2)
                                    break
                                
                            tp_toler1 = tolerance_dt1-1
                            tp_toler2 = 0.4
                            if len( np.where( rt_dt1[-tp_toler1:] < -tp_toler2  )[0]  ) >=tp_toler1:
                                if get_current_linfit(rt_dt2[-tp_toler1:], tp_toler1) < 0:
                                    print(f'sec= {sec}  tp_toler1 --> ', rt_dt1[-tp_toler1:]  )
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: tolerance dt1 over in (Middle, High) Gain')
                                    break

                            
                            elif rt_raw[-1] - rt_raw[-2] < -tolerance_RapidDrop_inHighGain:
                                rapid_dropStack += 1
                                print(f'{sec}sec: rapid stack +1')
                                if rapid_dropStack >= 2:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: rapid stack=2 in (Middle, High) Gain')
                                    break
                            elif rapid_dropStack == 1:
                                if rt_raw[-1] - rt_raw[-2] > tolerance_RapidDrop_inHighGain:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: rapid drop and pop in (Middle, High) Gain')
                                    break
                                elif len(np.where(rt_dt1[-2:] < 0)[0]) == 2:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: rapid stack=1 in (Middle, High) Gain')
                                    break
                                else:
                                    rapid_dropStack = 0
                            
                            tolerance_GM = max(1.5, rt[-1]/20)
                            # Global max tolerance 
                            if rmax - rt[-1] > tolerance_GM:
                                sec_stop = sec
                                print(f'stop tracing and sell coin: {sec}sec')
                                print('case: tolerance_GM over in (Middle, High) Gain')
                                print([rmax,tmax], [rt[-1], sec], tolerance_GM)
                                break

                        ##############################################
                        #           Range in High Gain               #
                        ##############################################
                        elif current_gain >= HighGain :
                            tolerance_LM = max(1, rt[-1]/20  )
                            range_Steady_Lmax = 6
                            range_convergence_time = 25
                            convergend_limit = HighGain/10
                            if( (len(np.where(rt_dt1[-range_Steady_Lmax:-1] >=0)[0]) ==range_Steady_Lmax-1)  and (rt_dt2[-1] <0) ): 
                                print(f'sec= {sec}  steady state Local Max')
                                t_range = np.linspace(sec-3,sec,4)
                                print(tmax, rt[tmax] ,current_gain)
                                t_range = np.round(np.linspace(max(sec-range_convergence_time,0),sec,sec-max(sec-range_convergence_time,0)+1))
                                t_intersect = np.intersect1d(t_range,instant_Lmax_time) 
                                if len(t_intersect) >= 2:
                                    mean_Lmax = np.mean( instant_Lmax[ max(-len(t_intersect)-1, -len(instant_Lmax) ) :-1] )
                                    if mean_Lmax < convergend_limit:
                                        print(f'sec= {sec} ---> converge in steady state Local Max')
                                        print("instant local max: ",instant_Lmax[ max(-len(t_intersect)-1, -len(instant_Lmax) ) :],instant_Lmax_time[ max(-len(t_intersect)-1, -len(instant_Lmax) ) :])
                                        sec_stop = sec
                                        print(f'stop tracing and sell coin: {sec}sec')
                                        print('case: convergence in High Gain')
                                        break
                                if rt[-2] - rt[-1] < tolerance_LM:
                                        print('pass : lower than tolerance LM in High Gain')
                                        LM_stack += 1
                                        pass
                                elif rt[-2] - rt[-1] >= tolerance_LM:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: larger than tolerance LM in High Gain ---> tolerance_LM= ',tolerance_LM)
                                    break
                            
                            if LM_stack >= 1:
                                LM_stack += 1
                                if rt[-LM_stack-1] - rt[-1] > tolerance_LM*2:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: tolerance_LM over in High Gain')
                                    print(rt[-LM_stack-1],rt[-1],tolerance_LM*2)
                                    break
                                    
                            elif rt_raw[-1] - rt_raw[-2] < -tolerance_RapidDrop_inHighGain:
                                rapid_dropStack += 1
                                print(f'{sec}sec: rapid stack +1')
                                if rapid_dropStack >= 2:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: rapid stack=2 in High Gain')
                                    break
                            elif rapid_dropStack == 1:
                                if rt_raw[-1] - rt_raw[-2] > tolerance_RapidDrop_inHighGain:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: rapid drop and pop in High Gain')
                                    break
                                elif len(np.where(rt_dt1[-2:] < 0)[0]) == 2:
                                    # if (rt_raw[-1] - rt_raw[-2]) < 0:
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: rapid stack=1 in High Gain')
                                    break
                                else:
                                    rapid_dropStack = 0
                            
                            tolerance_GM = max(2, rt[-1]/15)
                            # Global max tolerance in High Gain
                            if rmax - rt[-1] > tolerance_GM:
                                sec_stop = sec
                                print(f'stop tracing and sell coin: {sec}sec')
                                print('case: tolerance_GM over in High Gain')
                                print([rmax,tmax], [rt[-1], sec], tolerance_GM)
                                break
                                    
                        
                        
                    # fundamental principle 1: minimize loss
                    if sec > select_time +4:  # ==> 사고나서 4초정도는 지켜보기
                        if rt[-1] <= r_lower:
                            sec_stop = sec
                            print(f'stop tracing and sell coin: {sec}sec')
                            print('case: lower limit')
                            break
                        
                    if sec == time_limit :  #data time limit
                        sec_stop = sec
                        print(f'time limit')
                        break
            # need to apply delay time for 1sec tracing
            sec += 1
        end_time = time.time()
        print('End: ', round(end_time-init_time,3), ' sec')
        gain = rt_raw[-1] - r0
        gain_day.append(gain)
        # select coin from argmax_list
        # normalize coin data
        # trace coin data
        # make a dicision every sec 
        
        fig = plt.figure(num=1)
        mngr = plt.get_current_fig_manager()
        mngr.window.setGeometry(800,50,1100, 1050)
        ax1 = fig.add_subplot(3,1,1)
        ax1.clear()
        ax1.plot(rt, 'k*-')
        ax1.plot([select_time], [r0], 'ro')
        ax1.plot([sec_stop], [rt_raw[-1]], 'bo'); ax1.grid()
        ax1.set_title(f"rt-{selected_coin} : {sec} sec")
        ax2 = fig.add_subplot(3,1,2); ax2.grid()
        ax2.plot(rt_dt1, 'k*-')
        ax2.set_title(f'rt/dt')
        ax3 = fig.add_subplot(3,1,3); ax3.grid()
        ax3.plot(rt_dt2, 'k*-')
        ax3.set_title(f'd/dt(rt/dt)')
        
        print(f'gain : {gain}')
        total_price = np.array(data_price[selected_coin])
        total_rt = (total_price-total_price[0])/total_price[0]*100
        total_rt_ma = moving_average(total_rt,3)
        
        fig, ax = plt.subplots(nrows=2, ncols=1)
        ax[0].plot(total_rt, 'k*-')
        ax[0].plot([select_time], [r0], 'ro')
        ax[0].plot([sec_stop], [rt_raw[-1]], 'bo'); ax[0].grid()
        ax[0].set_title(f'{date}   raw data, selected coin: {selected_coin}')
        ax[1].plot(total_rt_ma, 'k*-')
        ax[1].plot([select_time], [r0], 'ro')
        ax[1].plot([sec_stop], [rt_raw[-1]], 'bo'); ax[1].grid()

        plt.show()
        
    total_gain_avg[date_str] = np.mean(gain_day)
    total_additive_gain += np.mean(gain_day)
    total_multiplicative_gain *= (1+np.mean(gain_day)/100)
    total_gain[date_str] = gain_day
    
gain_sum = np.sum(list(total_gain_avg.values()))
avg_gain_day = gain_sum/len(date_list)
print('##############')
print('Total gain')
print(total_gain)
print( gain_sum )
print('##############')
print(f'avg day gain ~ {avg_gain_day}')

total_additive_gain = 1 + total_additive_gain/100
print(f'total gain(additive): {total_additive_gain}')
print(f'total gain(multiplicative): {total_multiplicative_gain}')
