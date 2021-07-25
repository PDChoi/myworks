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
coin_1 = coin_manager(access_key,secret_key, 1, 'test')



#################
# get coin data #
#################
os.chdir(data_path)
# date_list = [416, 415, 414, 413, 412, 411, 410, 49,48,47, 46,45,44,43,42,41,331,330,329,328,325,324,323,322,321,320]
date_list = [51]
date = date_list[0]
data_file = glob.glob(f'total_price_Data_{date}*.pckl'); data_file=data_file[0] 

print(f'Data file = {data_file}')
data_price = pd.read_pickle(data_file)
t = data_price.index
# print(data_price)

delay_time_accumul =[0]
delay_time_excess = [0]
total_time = np.array([])
select_time = 10
selection_mark = 0
gain_day=[]
coin_idx = 1

t_end = float((data_file.split('.pckl')[0]).split('_')[-1])
if t_end > 1000:
    t_sampling = t_end%( round(t_end/10)*10 )
else:
    t_sampling = 1
sec = 0
delay_excess = 0 
delay_excess_accum = []
for sec in t:
    total_time = np.append(total_time, sec)
    df_tp = data_price.loc[sec]
    # print(df_tp)
    if sec == 0:
        df_price = pd.DataFrame( [df_tp] )
        df_rt = get_current_rate(df_price)
        # print(df_price)
        # print(df_rt)
        

    else:
        df_price = df_price.append( df_tp )
        df_price.index = t[:len(df_price["KRW-BTC"])]
        
        temp_rate = get_current_rate(df_price)
        df_rt = df_rt.append( temp_rate )
        df_rt.index = t[:len(df_price["KRW-BTC"])]
        
        if sec >= select_time:
            if selection_mark == 0:

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

    if sec == t[-1]:
        
        print('timeout')
        if coin1_state == 1:
            coin_1.close(sec)
            coin_1.case = 'timeout'
            coin_1.state = 2
        break

# plot test data results
plt.figure(num=1)
fig = plt.figure(num=1)
mngr = plt.get_current_fig_manager()
mngr.window.setGeometry(800,50,1100, 1050)
ax1 = fig.add_subplot(3,1,1)
ax1.clear()
ax1.plot(coin_1.coin_time,coin_1.rt, 'k*-')
ax1.plot([coin_1.select_time], [coin_1.r0], 'ro')
ax1.plot([coin_1.sec_stop], [coin_1.rt_raw[-1]], 'bo'); ax1.grid()
ax1.set_title(f"rt-{coin_1.selected_coin} : {coin_1.select_time} sec")
ax2 = fig.add_subplot(3,1,2); ax2.grid()
ax2.plot(coin_1.coin_time,coin_1.rt_dt1, 'k*-')
ax2.set_title(f'rt/dt')
ax3 = fig.add_subplot(3,1,3); ax3.grid()
ax3.plot(coin_1.coin_time,coin_1.rt_dt2, 'k*-')
ax3.set_title(f'd/dt(rt/dt)')
plt.tight_layout()
# plt.close()

fig2 = plt.figure(num=2)
plt.plot(t, np.array(df_rt[coin_1.selected_coin])*100, 'k*-')
plt.plot([coin_1.select_time], [coin_1.r0], 'ro')
plt.plot([coin_1.sec_stop], [coin_1.rt_raw[-1]], 'bo'); plt.grid()
plt.title(f"total rt-{coin_1.selected_coin}")
# plt.close()
plt.show()



