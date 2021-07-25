import numpy as np
import math as m
import os, sys, time, requests
import pandas as pd
import pyupbit as ub
from matplotlib import pyplot as plt
from datetime import datetime, date, timedelta
import hashlib
import time
from urllib.parse import urlencode
import jwt
import requests
import uuid
def average_filter(vector,winsize):
    winsize=int(winsize)
    vector=vector.astype('float32')
    avg_filtered_vector=np.zeros(len(vector), dtype=np.float32)
    # print(vector, vector.shape)
    for k in range(len(vector)):
        if k < int((winsize-1)/2) :
            avg_filtered_vector[k]=np.mean(vector[0:int(k+(winsize-1)/2 +1)])
        elif k <= int( len(vector)-(winsize-1)/2 -1 ):
            avg_filtered_vector[k]=np.mean(vector[ int(k-(winsize-1)/2) : int(k+(winsize-1)/2 +1) ] , axis=0)
        else :
            
            avg_filtered_vector[k]=np.mean(vector[int(k-(winsize-1)/2) :])
        # print(avg_filtered_vector[k])
    # print(avg_filtered_vector)

    return avg_filtered_vector



def get_all_market():
    url = "https://api.upbit.com/v1/market/all"
    querystring = {"isDetails": True}
    response = requests.request("GET", url, params=querystring)
    # print(response.json())
    return response.json()


def get_change_rate(market):
    url = "https://api.upbit.com/v1/candles/days"
    querystring = {"market": market, "count": "1"}
    response = requests.request("GET", url, params=querystring)
    print(response.json()[0]["market"])
    print(round(response.json()[0]['change_rate']*100, 2) )
    

def get_KRW_market():
    all_market = get_all_market()
    KRW_market = []
    for n in range(len(all_market)):
        if len(all_market[n]['market'].split('KRW-')) ==2:
            KRW_market.append(all_market[n])
    return KRW_market

# def get_current_price(market):
#     url = "https://api.upbit.com/v1/ticker"
#     querystring = {"markets": market}
#     response = requests.request("GET", url, params=querystring)
#     print(response)
#     # print(response.json()[0]['trade_price'])
#     return response.json()[0]['trade_price']

def get_current_rate(df_price, sec):

    temp1 = df_price[0:1]
    # print(temp1)
    temp2 = df_price[sec:sec+1]; temp2=temp2.reset_index(drop=True)
    # print(temp2)
    temp3 = temp2.sub(temp1, axis=0)
    # print(temp3)
    change_rate = temp3.div(temp1)
    return change_rate
        
def get_current_price_rev(coin_list, add_list):
    current_price = dict(ub.get_current_price(coin_list) )
    add_price = dict(ub.get_current_price(add_list) )
    for key_name in list(add_price.keys()) :
        value = add_price[key_name]
        current_price[key_name] = value
    return current_price

def get_current_priceDATA(coin_list):
    return
        
def get_current_linfit(arr, win):
    if len(arr) > win:
        t = len(arr) - 1
        x = np.linspace(t-win+1,t,win)
        y = arr[-win:]
        z = np.polyfit(x,y,1)
        
    else:
        if len(arr) == 1:
            return 0
        t = len(arr) - 1
        x = np.linspace(0,t, t+1 )
        y = arr[-win:]
        z = np.polyfit(x,y,1)
    return z[0]

def select_coin(test_coin,test_rt,n):
    test_diff = np.diff(test_rt)
    score_list = []
    # print(test_coin, test_diff[-4:])
    if len(np.where( abs(test_diff[-4:]) < 0.07 )[0] ) >= 2:
        # print(f'check condition 1: {test_coin}')
        # print('selection condition 1: fail')
        score_list.append(-1)
    else:
        score_list.append(1)

    if (len(np.where( test_diff[-4:] < -6 )[0]) >= 1):
        # print(f'check condition 2: {test_coin}')
        # print('selection condition 2: fail')
        score_list.append(-1)
    else:
        score_list.append(1)
    if (np.max(test_diff) + np.min(test_diff) ) < 0:
        # print(f'check condition 3: {test_coin}')
        # print('selection condition 3: fail')
        score_list.append(-1)
    else:
        score_list.append(1)
    
    if get_current_linfit(test_rt[-5:],5) < 0:
        # print(f'check condition 4: {test_coin}')
        # print('selection condition 4: fail')
        score_list.append(-1)
    else:
        score_list.append(1)
    
    if len(np.where(test_rt[-5:] == 0)[0]) >= 1:
        # print(f'check condition 5: {test_coin}')
        # print('selection condition 5: fail')
        score_list.append(-1)
    else:
        score_list.append(1)
    
    total_score = np.sum(np.array(score_list))       
    print(f'{test_coin}: total score {total_score}') 
    # estimate good coin
    coin_idx = n 
    return coin_idx, total_score
        
def selection_coin_v2(test_coin,test_rt):
    # selection score = R-square
    tp_rt = test_rt[2:]
    tmax = len(test_rt)-1
    if tmax-8 < 1:
        return print('rt length error')
    else:
        results = {}
        tp_t = np.linspace(tmax-8,tmax,9)
        coeff= np.polyfit(tp_t, tp_rt, 1)
        results['coeff'] = coeff.tolist()
        # r-square
        p =np.poly1d(coeff)
        yhat = p(tp_t)
        ybar = np.sum(tp_rt)/len(tp_rt)
        ssreg = np.sum( (yhat-ybar)**2 )
        sstot = np.sum( (tp_rt-ybar)**2 )
        Rsquare = ssreg/sstot
        # print(Rsquare) 
        # plt.figure()
        # plt.plot(tp_t,tp_rt, 'k*-')
        # plt.plot(tp_t,coeff[0]*tp_t+coeff[1] , 'r')
        # plt.show()
        total_score = round((Rsquare*100)*coeff[0],2)
        print(f'{test_coin}: total score {total_score}')
    return total_score
        
    
          
        
        
# KRW_market = get_KRW_market()

# coin_list = [ KRW_market[n]['market'] for n in range(len(KRW_market) ) ]   
# print(coin_list)
# print(len(coin_list))

# temp_price = get_current_price("KRW-LSK")
# print("KRW-LSK",temp_price)

# for coin in coin_list:
#     time.sleep(0.01)
#     print(coin)
#     temp_price = get_current_price(coin)
#     print(temp_price)

# print(price)
        
        
# current_price = dict(ub.get_current_price(coin_list) )
# got_market = current_price.keys()
# print(got_market)
# print(len(got_market))