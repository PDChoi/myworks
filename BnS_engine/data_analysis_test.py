import numpy as np
import math as m
import pandas as pd
import os, sys, time, requests, glob
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

py_path = 'C:\\Users\\Jk-home1\\Desktop\\python\\Coin_trade'
data_path = py_path + '\\data'
plot_path = py_path+ '\\plot'

os.chdir(data_path)
date = 320
price_list = glob.glob(f'total_price_Data_{date}*.csv')

df_data = pd.read_csv(price_list[0])
df_data = df_data.drop(['Unnamed: 0'],axis=1)
print(df_data)
t_cut = 10
for sec in range(t_cut+1):
    if sec ==0:
        df_rt = get_current_rate(df_data, sec)
    elif sec > 0:
        temp_rate = get_current_rate(df_data, sec)
        df_rt = df_rt.append( temp_rate )
        df_rt = df_rt.reset_index(drop=True)
df_tp = df_rt
argmax_list = []
r0_list = []
coin_candidate = []
coin_score=[]
# print(sec)
for n in range(5):
    argmax_tp = df_tp.loc[sec].idxmax(axis=1)
    print(argmax_tp, round(df_tp[argmax_tp].loc[sec]*100,2))
    argmax_list.append( argmax_tp )
    r0_list.append(round(df_tp[argmax_tp].loc[sec]*100,2))
    df_tp = df_tp.drop(argmax_tp, axis=1)
    
for n in range(len(argmax_list)):
    test_coin = argmax_list[n]; r0 = r0_list[n]  
    test_rt = np.array(df_rt[test_coin])*100
    coin_idx, score = select_coin(test_coin,test_rt,n)
    coin_candidate.append(coin_idx)
    coin_score.append(score)
print(coin_candidate)
coin_idx =  np.argmax( np.array(coin_score)  )
coin_name = argmax_list[coin_idx]

print(df_data[f'{coin_name}'])

data = np.array(df_data[f'{coin_name}'])
data_normalized = (data-data[0])/data[0]*100

data_avgfil = average_filter(data_normalized, 3)

plt.figure(num=1)
plt.plot( data_normalized[:400], 'k*-' )
plt.grid()
plt.title(f'data: {coin_name}')
plt.xlabel('time[sec]')
plt.ylabel('normalized value [%]')
os.chdir(plot_path)
plt.savefig(f'data_{coin_name}_{date}.png')

velocity = np.diff(data_normalized)

plt.figure(num=2)
# plt.plot(velocity[:400], 'r--' )
plt.plot( average_filter(data_normalized[:400],5), 'k*-' )
plt.grid()
plt.title(f'data_avgfilter: {coin_name}')
plt.xlabel('time[sec]')
plt.ylabel('normalized value [%]')


plt.show()




