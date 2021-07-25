import numpy as np
import math as m
import pandas as pd
import os, sys, time, requests, glob, pickle
import pyupbit as ub
from datetime import datetime, date, timedelta
import hashlib
import time
from urllib.parse import urlencode
import jwt
import requests
import uuid
from coin_func import *
from coin_trace import coin_manager

# version info
# 21.04.16: time sampling 1sec --> 0.25sec (need to make a correction for delay_excess),  save file format csv --> pckl(binary)
#           --> request server response limited within 10/sec  --> need to integrate the part of (t < selection coin)

home_path = "C:\\Users\\Jk-home1\\Desktop\\python\\Coin_trade"
data_path ="C:\\Users\\Jk-home1\\Desktop\\python\\Coin_trade\\data"
report_path = "C:\\Users\\Jk-home1\\Desktop\\python\\Coin_trade\\report"
plot_path = home_path+'\\plot'
os.chdir(home_path)
##############
# time setup #
##############
x=datetime.now()
today_year = x.year
today_month = x.month
today_day = x.day
today_hr = x.hour
today_m = x.minute
today_s = x.second
base_dt = datetime(today_year,today_month,today_day,9,0,0)
print(base_dt)
base_timestamp = time.mktime(datetime.strptime(str(base_dt),'%Y-%m-%d %H:%M:%S').timetuple() )
str_date = str(today_month)+str(today_day)

time_limit = 60*30
################
# Acount login #
################

# ip = '175.212.237.191' # allowed ip(jk home)
access_key = "dmkD7jxQJ7KnYqV0scl3yN7A0u0gMNm4DzLfskaa"
secret_key ="ZEFpIHcnrl4xkoI3ArruA0dZljLiUDRSA247rbVH"

my_login = ub.Upbit(access=access_key, secret=secret_key)

initial_gold = m.floor(my_login.get_balance() )
print(initial_gold)
# initialize
coin_1 = coin_manager(access_key,secret_key)



#################
# get coin data #
#################


KRW_market = get_KRW_market()

coin_list = [ KRW_market[n]['market'] for n in range(len(KRW_market) ) ]
print(f'coin_list: coin_list', len(coin_list))
# print(len(coin_list))
add_list = []
ub_list = list(dict(ub.get_current_price(coin_list) ).keys())
print(len(ub_list))
if len(coin_list) != len(ub_list):
    for coin in coin_list:
        if coin in ub_list:
            pass
        else:
            add_list.append(coin)
            print(coin)
N_coinAll = len(add_list)+len(ub_list)
print(f"total the number of coins: {N_coinAll} (",len(add_list),len(ub_list), ")")

while 1:
    current_timestamp=time.time()
    current_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')
    if current_timestamp >= base_timestamp:
        print(current_time)
        print("coin bot start")
        break
    elif (current_timestamp >= base_timestamp-5) and (current_timestamp < base_timestamp):
        time.sleep(0.04)
    else:
        print(current_time)
        print("wait for today market")
        time.sleep(1)
        
# 
delay_time_accumul =[0]
delay_time_excess = [0]

select_time = 8
selection_mark = 0
gain_day=[]
coin_idx = 0

total_time = np.array([0])
t_sampling = 0.25
sec = 0
delay_excess = 0 
delay_excess_accum = []
while 1:
    current_timestamp=time.time()
    current_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')
    current_price = dict(ub.get_current_price(coin_list) )
    add_price = dict(ub.get_current_price(add_list) )
    for key_name in list(add_price.keys()) :
        value = add_price[key_name]
        current_price[key_name] = value

    if sec == 0:
        start_time = current_time
        df_price = pd.DataFrame( [current_price.values()], columns=current_price.keys() )
        df_rt = get_current_rate(df_price)

    else:
        df_price = df_price.append( pd.DataFrame([current_price.values()], columns=current_price.keys())   )
        df_price = df_price.reset_index(drop=True)
        df_price.index = total_time

        temp_rate = get_current_rate(df_price)
        df_rt = df_rt.append( temp_rate )
        df_rt = df_rt.reset_index(drop=True)
        df_rt.index = total_time
        
        if sec >= select_time:
            if selection_mark == 0:
                selection_coin_time = current_time
                print(total_time)
                t_sampling = 1
                print('select coin')
                
                argmax_list = []
                r0_list = []
                coin_dict = {}
                
                df_tp = df_rt
                # search and select good coin
                for n in range(5):
                    argmax_tp = df_tp.loc[total_time[-1*int(1/t_sampling)]:total_time[-1]].mean(axis=0).idxmax()
                    test_rt = np.array(df_rt[argmax_tp])*100
                    score = selection_coin_v2(argmax_tp,test_rt)
                    coin_dict[argmax_tp] = score
                    df_tp = df_tp.drop(argmax_tp, axis=1)

                coin_dict = sorted(coin_dict.items(),key=(lambda x:x[1]), reverse=True)
                for n in range(5):
                    key = coin_dict[n][0]
                    # print(key)
                    argmax_list.append(key)
                    r0_tp = round(df_rt[key].loc[sec]*100,2)
                    r0_list.append(r0_tp)
                print(argmax_list,r0_list)
                
                coin_1.select(df_price,df_rt,argmax_list[coin_idx], r0_list[coin_idx], sec, total_time, t_sampling)
                
                print('start coin tracing')
                selection_mark = 1 # ------> end coin selection
                
            else:  # selection_mark = 1 # ------> start coin tracing
                # coin state 1: tracing,  state 2: close
                coin1_state = coin_1.state
                if coin1_state == 1 :
                    sec_stop_coin1 = coin_1.trace( np.array(df_price[coin_1.selected_coin])[-1], np.array(df_rt[coin_1.selected_coin])[-1]*100, sec)
                    if sec_stop_coin1 > 0:
                        coin_1.close(sec)
                        coin_1.state = 2
                    
                
     
    delay_time = time.time() - current_timestamp
    if t_sampling - delay_time <= 0:
        # print(delay_time)
        delay_excess = delay_time-t_sampling
        print(f"server response delay_excess: {delay_excess}sec from {current_time}")
        # time.sleep(delay_time-delay_excess)
        delay_excess_accum.append(delay_excess)
    else:
        # print(delay_time)
        delay_excess = 0
        time.sleep(t_sampling - delay_time)
        
        
    if sec > time_limit:
        os.chdir(data_path)
        df_price.to_pickle(f"total_price_Data_{str_date}_{time_limit}.pckl")
        print('timeout')
        if coin1_state == 1:
            coin_1.close(sec)
            coin_1.case = 'timeout'
            coin_1.state = 2
        break
    
    sec += t_sampling + round(delay_excess,2)
    total_time = np.append(total_time, sec)
        
print(delay_excess_accum)

# save coin data: buy_price, sell_price, coin data to pckl, report, plot

coin_1.save(str_date, report_path, plot_path, coin_dict, start_time, selection_coin_time, total_time, np.array(df_rt[coin_1.selected_coin])*100)


        
