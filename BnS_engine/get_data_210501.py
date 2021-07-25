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

# version info
# 21.04.16: time sampling 1sec --> 0.25sec (need to make a correction for delay_excess),  save file format csv --> pckl(binary)
#           --> request server response limited within 10/sec  --> need to integrate the part of (t < selection coin)
# 21.04.18: integrate DAQ and tracing parts --> coin_main_210418.py

home_path = "C:\\Users\\Jk-home1\\Desktop\\python\\Coin_trade"
data_path ="C:\\Users\\Jk-home1\\Desktop\\python\\Coin_trade\\data"
os.chdir(data_path)
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
################
# Acount login #
################

# ip = '175.212.237.191' #jk home
# access_key = "dmkD7jxQJ7KnYqV0scl3yN7A0u0gMNm4DzLfskaa"
# secret_key ="ZEFpIHcnrl4xkoI3ArruA0dZljLiUDRSA247rbVH"

# my_login = ub.Upbit(access=access_key, secret=secret_key)

# initial_gold = m.floor(my_login.get_balance() )
# print(initial_gold)

#################
# get coin data #
#################

# initialize
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
        
# stage-1 data acquisition
total_time = np.array([0])
t_sampling = 0.25
select_time = 10
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
        df_price = pd.DataFrame( [current_price.values()], columns=current_price.keys() )
        # print(current_time)
        # print(df_price)
        df_rate = get_current_rate(df_price)
        # print(df_rate)
    else:
        df_price = df_price.append( pd.DataFrame([current_price.values()], columns=current_price.keys())   )
        df_price = df_price.reset_index(drop=True)
        df_price.index = total_time
        # print(current_time)
        # print(df_price)
        temp_rate = get_current_rate(df_price)
        df_rate = df_rate.append( temp_rate )
        df_rate = df_rate.reset_index(drop=True)
        df_rate.index = total_time
        # print(df_rate.loc[sec].idxmax(axis=1))
        if sec >= select_time:
            t_sampling = 1

     
    delay_time = time.time() - current_timestamp
    if t_sampling - delay_time <= 0:
        # print(delay_time)
        delay_excess = delay_time-t_sampling
        # time.sleep(delay_time-delay_excess)
        delay_excess_accum.append( (delay_excess,current_time) )
    else:
        # print(delay_time)
        delay_excess = 0
        time.sleep(t_sampling - delay_time)
        
        
    if sec > 60*30:
        df_price.to_pickle(f"total_price_Data_{str_date}_{sec}.pckl")
        # df_rate.to_csv(f"total_rate_Data_{str_date}_{sec}.csv")
        print(current_time)
        break
    
    sec += t_sampling + round(delay_excess,2)
    total_time = np.append(total_time, sec)
        
print(delay_excess_accum)
        
        
        

# df = ub.get_ohlcv(selected_coin, interval="minute1", count=20 ,to=20210318)
# print(df)
# print(df.shape[0])