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
# path
home_path = "C:\\Users\\Jk-home1\\Desktop\\python\\Coin_trade"
data_path ="C:\\Users\\Jk-home1\\Desktop\\python\\Coin_trade\\data"
os.chdir(home_path)
os.chdir(data_path)
date_list = [45,44,43,42,41,331,330,329,328,325,324,323,322,321,320]
# date_list = [ 44 ]
total_gain = {}

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
    time_limit = len( data_price['KRW-BTC'])
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
                    rmax : global maximum of rt
                    r_upper : gain limit,   r_lower : loss limit
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
                    rt = average_filter( rt_raw, win_avgfilter)  # need to adjust filter window size
                    rmax = np.max(rt)
                    HighGain = 20
                    MiddleGain= 10
                    LowGain = 5
                    r_upper = r0 + 10
                    r_lower = r0 - 2
                    win_linfit = 3
                    rt_dt1 = np.array([0])
                    rt_dt2 = np.array([0])
                    tolerance_RapidDrop_inHighGain = 4
                    tolerance_RapidDrop_inMiddleGain = 3.5
                    tolerance_RapidDrop_inLowGain = 2
                    tolerance_dt1 = 5
                    tolerance_dt2 = 0.5
                    
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
                    rt_raw = np.array(df_rt[selected_coin])*100
                    rt = np.append( rt, rt[-1]+(rt_raw[-1]-rt[-win_avgfilter])/win_avgfilter  ) 
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
                    if sec == 20:
                        print( get_current_linfit(rt,win_linfit))
                    
                    tp_max = np.max(rt)
                    # fundamental principle 1
                    if rt[-1] <= r_lower:
                        sec_stop = sec
                        print(f'stop tracing and sell coin: {sec}sec')
                        print('case: lower limit')
                        break
                    # fundamental principle 2
                    if tp_max >= rmax:
                        rmax = tp_max
                        if rt_raw[-1] - rt_raw[-2] > 0:
                            pass
                    
                    if rt_dt1[-1] >= 0:
                        pass
                    
                    else:
                        
                        current_gain = rt_raw[-1] - r0
                        if current_gain < LowGain:
                            tp_toler1 = tolerance_dt1-2
                            tp_toler2 = 0.1
                            converge_toler = 0.05
                            converge_len = 6
                            if len( np.where( abs(rt_dt1[-converge_len:]) < converge_toler  )[0]  ) >= converge_len:
                                if rt_dt2[-1] < 0:
                                    print(f'sec= {sec}  converge --> local max'  )
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: local maximum in (Middle, High) Gain')
                                    break
                            if len( np.where( rt_dt1[-tp_toler1:] < -tp_toler2  )[0]  ) >=tp_toler1:
                                if get_current_linfit(rt_dt2[-tp_toler1:], tp_toler1) < 0:
                                    print(f'sec= {sec}  tp_toler1 --> ', rt_dt1[-tp_toler1:]  )
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: tolerance dt1 over in LowGain')
                                    break
                            elif len( np.where( rt_dt2[-tp_toler1:] < -tp_toler2 )[0]  ) >=tp_toler1:
                                # print(f'sec= {sec}  tp_toler1 --> ', rt_dt1[-tp_toler1:]  )
                                print(f'sec= {sec}  tp_toler2 --> ', rt_dt2[-tp_toler1:]  )
                                sec_stop = sec
                                print(f'stop tracing and sell coin: {sec}sec')
                                print('case: tolerance dt1 over in LowGain')
                                break
                            
                            elif rt_raw[-1] - rt_raw[-2] < -tolerance_RapidDrop_inLowGain:
                                sec_stop = sec
                                print(f'stop tracing and sell coin: {sec}sec')
                                print('case: rapid drop in Low Gain')
                                break
                        
                        elif ((current_gain >= LowGain) and (current_gain < MiddleGain)):
                            tp_toler1 = tolerance_dt1-1
                            tp_toler2 = 0.5
                            if len( np.where( rt_dt1[-tp_toler1:] < -tp_toler2  )[0]  ) >=tp_toler1:
                                if get_current_linfit(rt_dt2[-tp_toler1:], tp_toler1) < 0:
                                    print(f'sec= {sec}  tp_toler1 --> ', rt_dt1[-tp_toler1:]  )
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: tolerance dt1 over in (Low, Middle) Gain')
                                    break
                            elif len( np.where( rt_dt2[-tp_toler1:] < -tp_toler2 )[0]  ) >=tp_toler1:
                                # print(f'sec= {sec}  tp_toler1 --> ', rt_dt1[-tp_toler1:]  )
                                print(f'sec= {sec}  tp_toler2 --> ', rt_dt2[-tp_toler1:]  )
                                sec_stop = sec
                                print(f'stop tracing and sell coin: {sec}sec')
                                print('case: tolerance dt1 over in (Low, Middle) Gain')
                                break
                            
                            elif rt_raw[-1] - rt_raw[-2] < -tolerance_RapidDrop_inMiddleGain:
                                sec_stop = sec
                                print(f'stop tracing and sell coin: {sec}sec')
                                print('case: rapid drop in (Low, Middle) Gain')
                                break
                                
                        elif ((current_gain >= MiddleGain) and (current_gain < HighGain)) :
                            # find convergence
                            tp_toler1 = tolerance_dt1-1
                            tp_toler2 = 0.5
                            converge_toler = 0.2
                            if len( np.where( abs(rt_dt1[-tp_toler1:]) < converge_toler  )[0]  ) >= tp_toler1:
                                if rt_dt2[-1] < 0:
                                    print(f'sec= {sec}  converge --> local max'  )
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: local maximum in (Middle, High) Gain')
                                    break
                                    
                            
                            if len( np.where( rt_dt1[-tp_toler1:] < -tp_toler2  )[0]  ) >=tp_toler1:
                                if get_current_linfit(rt_dt2[-tp_toler1:], tp_toler1) < 0:
                                    print(f'sec= {sec}  tp_toler1 --> ', rt_dt1[-tp_toler1:]  )
                                    sec_stop = sec
                                    print(f'stop tracing and sell coin: {sec}sec')
                                    print('case: tolerance dt1 over in (Low, Middle) Gain')
                                    break
                            elif len( np.where( rt_dt2[-tp_toler1:] < -tp_toler2 )[0]  ) >=tp_toler1:
                                # print(f'sec= {sec}  tp_toler1 --> ', rt_dt1[-tp_toler1:]  )
                                print(f'sec= {sec}  tp_toler2 --> ', rt_dt2[-tp_toler1:]  )
                                sec_stop = sec
                                print(f'stop tracing and sell coin: {sec}sec')
                                print('case: tolerance dt1 over in (Low, Middle) Gain')
                                break
                            
                            elif rt_raw[-1] - rt_raw[-2] < -tolerance_RapidDrop_inHighGain:
                                sec_stop = sec
                                print(f'stop tracing and sell coin: {sec}sec')
                                print('case: rapid drop in (Middle, High) Gain')
                                break
                            tp_toler1 = tolerance_dt1+2
                            if len( np.where( rt_dt1[-tp_toler1:] < 0  )[0]  ) >=tp_toler1:
                                if rt_dt2[-1] < 0:
                                    if get_current_linfit(rt_dt2[-tp_toler1:], tp_toler1) < 0:
                                        print(f'sec= {sec}  tp_toler2 --> ', rt_dt1[-tp_toler1:]  )
                                        sec_stop = sec
                                        print(f'stop tracing and sell coin: {sec}sec')
                                        print('case: tolerance dt1 over')
                                        break
                        
                        # elif current_gain >= HighGain :
                            
                                    
                        
                        
                        
                        # 2nd derivative part --> rt_dt2 control
                        if rt_dt2[-1] < -tolerance_dt2:

                            if len( np.where( rt_dt2[-4:] < -tolerance_dt2  )[0] ) >= 3:
                                sec_stop = sec
                                print(f'sec = {sec}  tolerance_dt2 -->',rt_dt2[-4:] )
                                print(f'stop tracing and sell coin: {sec}sec')
                                print('case: tolerance dt2 over')
                                break
                            else:
                                pass
                        else:
                            pass
                    if sec == time_limit -1:  #time limit
                        sec_stop = sec
                        print(f'time limit')
                        break
            sec += 1
        gain = rt_raw[-1] - r0
        gain_day.append(gain)
        # select coin from argmax_list
        # normalize coin data
        # trace coin data
        # make a dicision every sec 
        fig = plt.figure(num=1)
        mngr = plt.get_current_fig_manager()
        # to put it into the upper left corner for example:
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



        fig2 = plt.figure(num=2)
        total_price = np.array(data_price[selected_coin])

        plt.plot((total_price-total_price[0])/total_price[0]*100, 'k*-')
        plt.plot([select_time], [r0], 'ro')
        plt.plot([sec_stop], [rt_raw[-1]], 'bo')
        plt.grid()
        plt.title(f'{date}   raw data, selected coin: {selected_coin}')
        plt.show()
    
    total_gain[date_str] = np.mean(gain_day)
    
gain_sum = np.sum(list(total_gain.values()))
avg_gain_day = gain_sum/len(date_list)
print('##############')
print('Total gain')
print(total_gain)
print( gain_sum )
print('##############')
print(f'avg day gain ~ {avg_gain_day}')
    
