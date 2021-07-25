import numpy as np
import math as m
import pandas as pd
import os, sys, time, requests, glob
import pyupbit as ub
from datetime import datetime, date, timedelta
import hashlib
import time
from urllib.parse import urlencode
import jwt
import requests
import uuid
from coin_func import *
home_path = "C:\\Users\\Jk-home1\\Desktop\\python\\Coin_trade"
data_path ="C:\\Users\\Jk-home1\\Desktop\\python\\Coin_trade\\data"
os.chdir(data_path)
##############
# time setup #

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
# print(coin_list)
# print(len(coin_list))
add_list = []
ub_list = list(dict(ub.get_current_price(coin_list) ).keys())
# print(ub_list)
for coin in coin_list:
    if coin in ub_list:
        pass
    else:
        add_list.append(coin)
        print(coin)



while 1:
    time.sleep(1)
    current_timestamp=time.time()
    current_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

    if current_timestamp > base_timestamp:
        print(current_time)
        print("coin bot start")
        break

    else:
        print(current_time)
        print("wait for today market")

# stage-1 data acquisition
sec = 0
while 1:
    current_timestamp=time.time()
    current_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    current_price = dict(ub.get_current_price(coin_list) )
    add_price = dict(ub.get_current_price(add_list) )
    for key_name in list(add_price.keys()) :
        # print(key_name)
        value = add_price[key_name]
        current_price[key_name] = value
        # print(current_price[key_name])
    
    # print(  len(current_price.keys()) )
    if sec == 0:
        df_price = pd.DataFrame( [current_price.values()], columns=current_price.keys() )
        print(current_time)
        # print(df_price)
        df_rate = get_current_rate(df_price, sec)
        # print(df_rate)
    else:
        df_price = df_price.append( pd.DataFrame([current_price.values()], columns=current_price.keys())   )
        df_price = df_price.reset_index(drop=True)
        print(current_time)
        # print(df_price)
        temp_rate = get_current_rate(df_price, sec)
        df_rate = df_rate.append( temp_rate )
        df_rate = df_rate.reset_index(drop=True)
        # print(df_rate.loc[sec].idxmax(axis=1))

        
        
        

    time.sleep(1)
    sec += 1
    
    if sec == 20:
        try:
            print(current_time)
            print('max rate coin =  ',df_rate.loc[sec-1].idxmax(axis=1))
        except:
            print('error')

        
    elif sec == 60:
        try:
            print(current_time)
            print('max rate coin =  ',df_rate.loc[sec-1].idxmax(axis=1))
        except:
            print('error')
        
    elif sec ==120:
        try:
            print(current_time)
            print('max rate coin =  ',df_rate.loc[sec-1].idxmax(axis=1))
        except:
            print('error')
    elif sec ==180:
        try:
            print(current_time)
            print('max rate coin =  ',df_rate.loc[sec-1].idxmax(axis=1))
        except:
            print('error')
        
        
    elif sec > 60*15:
        df_price.to_csv(f"total_price_Data_{str_date}_{sec}.csv")
        df_rate.to_csv(f"total_rate_Data_{str_date}_{sec}.csv")
        break
        
            
        
        
        

# df = ub.get_ohlcv(selected_coin, interval="minute1", count=20 ,to=20210318)
# print(df)
# print(df.shape[0])