"""
=== Hedging ===
1. get_delta_hedge(df_price, r=0.05, sigma=0.3, T=1, sell_price=3)
2. get_delta_hedge_2week(df_price, freq=2, r=0.05, sigma=0.3, T=1, sell_price=3)
3. get_gamma_hedge(df_price, r=0.05, sigma=0.3, T=1, sell_price=3)
4. get_vega_hedge(df_price, r=0.05, sigma=0.3, T=1, sell_price=3)
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import datetime
import matplotlib.pyplot as plt
import plotly.express as px
from scipy import log,exp,sqrt,stats
from scipy.stats import norm
import warnings
warnings.filterwarnings("ignore")

# === 參數 ===
numberOfSims = 1 # number of sims
mu = 0.1 # drift coefficent
S0 = 50 # initial stock price
quantity = 100 # brokerage sales quantity ex. 100=賣100個
'''
sigma = 0.3 # volatility
T = 1 # time in years
sell_price = 8
r=0.05
'''

# === Hedging ===
def get_delta_hedge(df_price, r=0.05, sigma=0.3, T=1, sell_price=3):
    steps = len(df_price)-1
    dt = T/steps # calc each time step
    df_delta = pd.DataFrame(columns=["St","現貨持有量","現貨增減量","現貨增減成本","現貨利息成本 ",
                                    "現貨累積成本","A部位損益","現貨部位損益","總損益"])

    df_delta["St"] = df_price["St"]
    df_delta["現貨持有量"] = - round( df_price["A_總Delta"], 1 )
    df_delta["現貨增減量"] = df_delta["現貨持有量"] - df_delta["現貨持有量"].shift()
    df_delta["現貨增減量"].iloc[0] = df_delta["現貨持有量"].iloc[0]
    df_delta["現貨增減成本"] = df_delta["現貨增減量"] * df_price["St"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_delta["現貨利息成本 "].iloc[0] = 0.0
            df_delta["現貨累積成本"].iloc[0] = df_delta["現貨增減成本"].iloc[0]
        else:
            df_delta.at[step,"現貨利息成本 "] = df_delta["現貨累積成本"].iloc[step-1] *  (exp(r*dt)-1)
            df_delta.at[step,"現貨累積成本"] = df_delta["現貨累積成本"].iloc[step-1] \
                                                        + df_delta["現貨增減成本"].iloc[step] \
                                                        + df_delta["現貨利息成本 "].iloc[step]
    df_delta["A部位損益"] = ( sell_price*exp(r*df_price["t"]) -  df_price["A_Price"] ) * quantity
    df_delta["現貨部位損益"] =  df_delta["現貨持有量"] * df_price["St"] - df_delta["現貨累積成本"]
    df_delta["總損益"] =  df_delta["A部位損益"] + df_delta["現貨部位損益"]
    df_delta = pd.concat([df_price["t"],df_delta.astype(float)],axis=1)
    return df_delta.round(2)

def get_delta_hedge_2week(df_price, freq=2, r=0.05, sigma=0.3, T=1, sell_price=3):
    steps = len(df_price)-1
    dt = T/steps # calc each time step
    df_delta = pd.DataFrame(columns=["St","現貨持有量","現貨增減量","現貨增減成本","現貨利息成本 ",
                                    "現貨累積成本","A部位損益","現貨部位損益","總損益"])
    df_delta["St"] = df_price["St"]
    for step in range(0, len(df_price)): #0~20
            if step%freq == 0:  # 0,2,4...
                df_delta.at[step,"現貨持有量"] = - round(df_price.at[step,"A_總Delta"], 1)
            else: df_delta.at[step,"現貨持有量"] = df_delta.at[step-1,"現貨持有量"]
                
            
    df_delta["現貨增減量"] = df_delta["現貨持有量"] - df_delta["現貨持有量"].shift()
    df_delta["現貨增減量"].iloc[0] = df_delta["現貨持有量"].iloc[0]
    df_delta["現貨增減成本"] = df_delta["現貨增減量"] * df_price["St"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_delta["現貨利息成本 "].iloc[0] = 0
            df_delta["現貨累積成本"].iloc[0] = df_delta["現貨增減成本"].iloc[0]
        else:
            df_delta.at[step,"現貨利息成本 "] = df_delta["現貨累積成本"].iloc[step-1] *  (exp(r*dt)-1)
            df_delta.at[step,"現貨累積成本"] = df_delta["現貨累積成本"].iloc[step-1] \
                                                        + df_delta["現貨增減成本"].iloc[step] \
                                                        + df_delta["現貨利息成本 "].iloc[step]
    df_delta["A部位損益"] = ( sell_price*exp(r*df_price["t"]) -  df_price["A_Price"] ) * quantity
    df_delta["現貨部位損益"] =  df_delta["現貨持有量"] * df_price["St"] - df_delta["現貨累積成本"]
    df_delta["總損益"] =  df_delta["A部位損益"] + df_delta["現貨部位損益"]
    df_delta = pd.concat([df_price["t"],df_delta.astype(float)],axis=1)
    return df_delta.round(2)

def get_gamma_hedge(df_price, r=0.05, sigma=0.3, T=1, sell_price=3):
    steps = len(df_price)-1
    dt = T/steps # calc each time step
    # B部位
    df_gamma = pd.DataFrame(columns=["St","B持有量","B增減量","B增減成本","B利息成本","B累積成本","用B避險後的總Delta",
                                     "現貨持有量","現貨增減量","現貨增減成本","現貨利息成本 ","現貨累積成本",
                                     "A部位損益","B部位損益","現貨部位損益","總損益"])
    df_gamma["St"] = df_price["St"]
    df_gamma["B持有量"] = -1 * round( df_price["A_Gamma"] * quantity / df_price["B_Gamma"], 2 )
    df_gamma["B持有量"][df_gamma["B持有量"].isnull()]=0
    df_gamma.replace([np.inf, -np.inf], 0, inplace=True)
    df_gamma["B增減量"] = df_gamma["B持有量"] - df_gamma["B持有量"].shift()
    df_gamma["B增減量"].iloc[0] = df_gamma["B持有量"].iloc[0]
    df_gamma["B增減成本"] = df_gamma["B增減量"] * df_price["B_Price"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_gamma["B利息成本"] = 0.0
            df_gamma["B累積成本"] = df_gamma["B增減成本"].iloc[0]
        else:
            df_gamma.at[step,"B利息成本"] = df_gamma["B累積成本"].iloc[step-1] *  (exp(r*dt)-1)
            df_gamma.at[step,"B累積成本"] = df_gamma["B累積成本"].iloc[step-1] \
                                                        + df_gamma["B增減成本"].iloc[step] \
                                                        + df_gamma["B利息成本"].iloc[step]
    df_gamma["用B避險後的總Delta"] = df_price["A_總Delta"] + df_gamma["B持有量"] * df_price["B_Delta"]
    # 現貨部位
    df_gamma["現貨持有量"] = round( -1 * df_gamma["用B避險後的總Delta"], 1 )
    df_gamma["現貨增減量"] = df_gamma["現貨持有量"] - df_gamma["現貨持有量"].shift()
    df_gamma["現貨增減量"].iloc[0] = df_gamma["現貨持有量"].iloc[0]
    df_gamma["現貨增減成本"] = df_gamma["現貨增減量"] * df_price["St"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_gamma["現貨利息成本 "] = 0.0
            df_gamma["現貨累積成本"] = df_gamma["現貨增減成本"].iloc[0]
        else:
            df_gamma.at[step,"現貨利息成本 "] = df_gamma["現貨累積成本"].iloc[step-1] *  (exp(r*dt)-1)
            df_gamma.at[step,"現貨累積成本"] = df_gamma["現貨累積成本"].iloc[step-1] \
                                                        + df_gamma["現貨增減成本"].iloc[step] \
                                                        + df_gamma["現貨利息成本 "].iloc[step]
    df_gamma["A部位損益"] = ( sell_price*exp(r*df_price["t"]) -  df_price["A_Price"] ) * quantity
    df_gamma["B部位損益"] = df_gamma["B持有量"] * df_price["B_Price"] - df_gamma["B累積成本"]
    df_gamma["現貨部位損益"] =  df_gamma["現貨持有量"] * df_price["St"] - df_gamma["現貨累積成本"]
    df_gamma["總損益"] =  df_gamma["A部位損益"] + df_gamma["B部位損益"] + df_gamma["現貨部位損益"]
    df_gamma = pd.concat([df_price["t"],df_gamma.astype(float)],axis=1)
    return df_gamma.round(2)

def get_gamma_hedge_v2(df_price, r=0.05, sigma=0.3, T=1, sell_price=3):
    steps = len(df_price)-1
    dt = T/steps # calc each time step
    # B部位
    df_gamma = pd.DataFrame(columns=["St","B持有量","B增減量","B增減成本","B利息成本","B累積成本","用B避險後的總Delta",
                                     "現貨持有量","現貨增減量","現貨增減成本","現貨利息成本 ","現貨累積成本",
                                     "A部位損益","B部位損益","現貨部位損益","總損益"])
    df_gamma["St"] = df_price["St"]
    df_gamma["B持有量"] = -1 * round( df_price["A_Gamma"] * quantity / df_price["B_Gamma"], 2 )
    for i in range(3):
        df_gamma.at[df_gamma.index[-i-1],"B持有量"] = 0
    df_gamma["B持有量"][df_gamma["B持有量"].isnull()]=0 # 最後三期變gamma = 0
    df_gamma.replace([np.inf, -np.inf], 0, inplace=True)
    df_gamma["B增減量"] = df_gamma["B持有量"] - df_gamma["B持有量"].shift()
    df_gamma["B增減量"].iloc[0] = df_gamma["B持有量"].iloc[0]
    df_gamma["B增減成本"] = df_gamma["B增減量"] * df_price["B_Price"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_gamma["B利息成本"] = 0.0
            df_gamma["B累積成本"] = df_gamma["B增減成本"].iloc[0]
        else:
            df_gamma.at[step,"B利息成本"] = df_gamma["B累積成本"].iloc[step-1] *  (exp(r*dt)-1)
            df_gamma.at[step,"B累積成本"] = df_gamma["B累積成本"].iloc[step-1] \
                                                        + df_gamma["B增減成本"].iloc[step] \
                                                        + df_gamma["B利息成本"].iloc[step]
    df_gamma["用B避險後的總Delta"] = df_price["A_總Delta"] + df_gamma["B持有量"] * df_price["B_Delta"]
    # 現貨部位
    df_gamma["現貨持有量"] = round( -1 * df_gamma["用B避險後的總Delta"], 1 )
    df_gamma["現貨增減量"] = df_gamma["現貨持有量"] - df_gamma["現貨持有量"].shift()
    df_gamma["現貨增減量"].iloc[0] = df_gamma["現貨持有量"].iloc[0]
    df_gamma["現貨增減成本"] = df_gamma["現貨增減量"] * df_price["St"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_gamma["現貨利息成本 "] = 0.0
            df_gamma["現貨累積成本"] = df_gamma["現貨增減成本"].iloc[0]
        else:
            df_gamma.at[step,"現貨利息成本 "] = df_gamma["現貨累積成本"].iloc[step-1] *  (exp(r*dt)-1)
            df_gamma.at[step,"現貨累積成本"] = df_gamma["現貨累積成本"].iloc[step-1] \
                                                        + df_gamma["現貨增減成本"].iloc[step] \
                                                        + df_gamma["現貨利息成本 "].iloc[step]
    df_gamma["A部位損益"] = ( sell_price*exp(r*df_price["t"]) -  df_price["A_Price"] ) * quantity
    df_gamma["B部位損益"] = df_gamma["B持有量"] * df_price["B_Price"] - df_gamma["B累積成本"]
    df_gamma["現貨部位損益"] =  df_gamma["現貨持有量"] * df_price["St"] - df_gamma["現貨累積成本"]
    df_gamma["總損益"] =  df_gamma["A部位損益"] + df_gamma["B部位損益"] + df_gamma["現貨部位損益"]
    df_gamma = pd.concat([df_price["t"],df_gamma.astype(float)],axis=1)
    return df_gamma.round(2)

def get_vega_hedge(df_price, r=0.05, sigma=0.3, T=1, sell_price=3):
    steps = len(df_price)-1
    dt = T/steps # calc each time step
    # B部位
    df_vega = pd.DataFrame(columns=["St","B持有量","B增減量","B增減成本","B利息成本","B累積成本",
                                    "C部位_持有量","C部位_增減量","C部位_增減成本","C部位_利息成本","C部位_累積成本",
                                    "現貨持有量","現貨增減量","現貨增減成本","現貨利息成本 ","現貨累積成本",
                                    "A部位損益","B部位損益","C部位_損益","現貨部位損益","總損益"])
    df_vega["St"] = df_price["St"]
    for step in range(0, len(df_price)): #0~20
        try:
            # Delta、Gamma、Vega
            X = np.array([[df_price["B_Delta"][step], df_price["C_Delta"][step], 1], 
                          [df_price["B_Gamma"][step], df_price["C_Gamma"][step], 0], 
                          [df_price["B_Vega"][step], df_price["C_Vega"][step], 0]]) # B + C + Spot = A
            Y = np.array([-df_price["A_總Delta"][step], -df_price["A_總Gamma"][step], -df_price["A_總Vega"][step]])
            ans = np.linalg.solve(X, Y)
            df_vega.at[step,"B持有量"]=ans[0]
            df_vega.at[step,"C部位_持有量"]=ans[1]
            df_vega.at[step,"現貨持有量"]=ans[2]
            # 避險數量太大
            if ans[0]>10000 or ans[0]<-10000:
                print("EXT")
                df_vega.at[step,"B持有量"]=df_vega["B持有量"][step-1]
                df_vega.at[step,"C部位_持有量"]=df_vega["C部位_持有量"][step-1]
                df_vega.at[step,"現貨持有量"]=df_vega["現貨持有量"][step-1]
        except Exception as ex:
            df_vega.at[step,"B持有量"] = 0
            df_vega.at[step,"C部位_持有量"] = 0
            df_vega.at[step,"現貨持有量"] = round(-1 * df_price["A_總Delta"][step], 1)
            pass
    df_vega.replace([np.inf, -np.inf], 0, inplace=True)
    # B
    df_vega["B增減量"] = df_vega["B持有量"] - df_vega["B持有量"].shift()
    df_vega["B增減量"].iloc[0] = df_vega["B持有量"].iloc[0]
    df_vega["B增減成本"] = df_vega["B增減量"] * df_price["B_Price"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_vega["B利息成本"] = 0.0
            df_vega["B累積成本"] = df_vega["B增減成本"].iloc[0]
        else:
            df_vega.at[step,"B利息成本"] = df_vega["B累積成本"].iloc[step-1] * (exp(r*dt)-1)
            df_vega.at[step,"B累積成本"] = df_vega["B累積成本"].iloc[step-1] \
                                                        + df_vega["B增減成本"].iloc[step] \
                                                        + df_vega["B利息成本"].iloc[step]  
    # C
    df_vega["C部位_增減量"] = df_vega["C部位_持有量"] - df_vega["C部位_持有量"].shift()
    df_vega["C部位_增減量"].iloc[0] = df_vega["C部位_持有量"].iloc[0]
    df_vega["C部位_增減成本"] = df_vega["C部位_增減量"] * df_price["C_Price"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_vega["C部位_利息成本"] = 0.0
            df_vega["C部位_累積成本"] = df_vega["C部位_增減成本"].iloc[0]
        else:
            df_vega.at[step,"C部位_利息成本"] = df_vega["C部位_累積成本"].iloc[step-1] *  (exp(r*dt)-1)
            df_vega.at[step,"C部位_累積成本"] = df_vega["C部位_累積成本"].iloc[step-1] \
                                                        + df_vega["C部位_增減成本"].iloc[step] \
                                                        + df_vega["C部位_利息成本"].iloc[step]
    # SPOT
    df_vega["現貨增減量"] = df_vega["現貨持有量"] - df_vega["現貨持有量"].shift()
    df_vega["現貨增減量"].iloc[0] = df_vega["現貨持有量"].iloc[0]
    df_vega["現貨增減成本"] = df_vega["現貨增減量"] * df_price["St"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_vega["現貨利息成本 "] = 0.0
            df_vega["現貨累積成本"] = df_vega["現貨增減成本"].iloc[0]
        else:
            df_vega.at[step,"現貨利息成本 "] = df_vega["現貨累積成本"].iloc[step-1] * (exp(r*dt)-1)
            df_vega.at[step,"現貨累積成本"] = df_vega["現貨累積成本"].iloc[step-1] \
                                                        + df_vega["現貨增減成本"].iloc[step] \
                                                        + df_vega["現貨利息成本 "].iloc[step]
    df_vega["A部位損益"] = ( sell_price*exp(r*df_price["t"]) -  df_price["A_Price"] ) * quantity
    df_vega["B部位損益"] = df_vega["B持有量"] * df_price["B_Price"] - df_vega["B累積成本"]
    df_vega["C部位_損益"] = df_vega["C部位_持有量"] * df_price["C_Price"] - df_vega["C部位_累積成本"]
    df_vega["現貨部位損益"] =  df_vega["現貨持有量"] * df_price["St"] - df_vega["現貨累積成本"]
    df_vega["總損益"] =  df_vega["A部位損益"] + df_vega["B部位損益"] + df_vega["C部位_損益"] + df_vega["現貨部位損益"]
    df_vega = pd.concat([df_price["t"], df_vega.astype(float)],axis=1)

    return df_vega.round(2)


def get_warrent_delta_hedge(df_price, freq=1, r=0.01045, TTE=183/365, sell_price=2.355, quantity=20000, conversion=0.06):
    df_delta = pd.DataFrame(index=df_price.index,columns=["St","現貨持有量","現貨增減量","現貨增減成本","現貨利息成本 ","現貨累積成本",
                                     "A部位損益","現貨部位損益","總損益"])
    df_delta["St"] = df_price["St"]
    for step in range(0, len(df_price)): #0~20
        if step%freq == 0: df_delta["現貨持有量"].iloc[step] = - round( df_price["A_Delta"].iloc[step] * quantity * conversion, 2 )
        else:              df_delta["現貨持有量"].iloc[step] = df_delta["現貨持有量"].iloc[step-1]
    df_delta.at[df_delta.index[-1], "現貨持有量"] = 0
    df_delta["現貨增減量"] = df_delta["現貨持有量"] - df_delta["現貨持有量"].shift()
    df_delta["現貨增減量"].iloc[0] = df_delta["現貨持有量"].iloc[0]
    df_delta["現貨增減成本"] = df_delta["現貨增減量"] * df_price["St"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_delta["現貨利息成本 "].iloc[0] = 0.0
            df_delta["現貨累積成本"].iloc[0] = df_delta["現貨增減成本"].iloc[0]
        else:
            df_delta.at[df_delta.index[step],"現貨利息成本 "] = df_delta["現貨累積成本"].iloc[step-1] *  (exp( r *(df_price["T-t"].iloc[step-1]-df_price["T-t"].iloc[step]) )-1)
            df_delta.at[df_delta.index[step],"現貨累積成本"] = df_delta["現貨累積成本"].iloc[step-1] \
                                                        + df_delta["現貨增減成本"].iloc[step] \
                                                        + df_delta["現貨利息成本 "].iloc[step]
    df_delta["A部位損益"] = ( sell_price * exp( r * (TTE-df_price["T-t"]) )-  df_price["A_Close"] ) * quantity
    df_delta["現貨部位損益"] =  df_delta["現貨持有量"] * df_price["St"] - df_delta["現貨累積成本"]
    df_delta["總損益"] =  df_delta["A部位損益"] + df_delta["現貨部位損益"]
    df_delta = pd.concat([df_price["T-t"],df_delta.astype(float)],axis=1)
    return df_delta.round(2)

def get_warrent_gamma_hedge(df_price, freq=1, r=0.01045, TTE=183/365, sell_price=2.355, quantity=20000, conversion=0.06):
    df_gamma = pd.DataFrame(index=df_price.index, columns=["St","B持有量","B增減量","B增減成本","B利息成本","B累積成本",
                                     "用B避險後的總Delta","現貨持有量","現貨增減量","現貨增減成本","現貨利息成本 ","現貨累積成本",
                                     "A部位損益","B部位損益","現貨部位損益","總損益"])
    df_gamma["St"] = df_price["St"]
    # 計算 B持有量
    for step in range(0, len(df_price)): 
        if step%freq == 0: df_gamma["B持有量"].iloc[step] = -1 * round( df_price["A_Gamma"].iloc[step] * quantity * conversion / df_price["B_Gamma"].iloc[step], 8 )
        else:              df_gamma["B持有量"].iloc[step] = df_gamma["B持有量"].iloc[step-1]
    df_gamma["B持有量"][df_gamma["B持有量"].isnull()]=0
    df_gamma.replace([np.inf, -np.inf], 0, inplace=True)
    df_gamma["用B避險後的總Delta"] = df_price["A_Delta"] * quantity * conversion + df_gamma["B持有量"] * df_price["B_Delta"]
    # 計算 現貨持有量
    for step in range(0, len(df_price)): 
        if step%freq == 0: df_gamma["現貨持有量"].iloc[step] = round( -1 * df_gamma["用B避險後的總Delta"].iloc[step], 8 )
        else:              df_gamma["現貨持有量"].iloc[step] = df_gamma["現貨持有量"].iloc[step-1]
    df_gamma.at[df_gamma.index[-1], "B持有量"] = 0
    df_gamma.at[df_gamma.index[-1], "現貨持有量"] = 0
    # 計算 B成本
    df_gamma["B增減量"] = df_gamma["B持有量"] - df_gamma["B持有量"].shift()
    df_gamma["B增減量"].iloc[0] = df_gamma["B持有量"].iloc[0]
    df_gamma["B增減成本"] = df_gamma["B增減量"] * df_price["B_Settlement Price"]
    for step in range(0, len(df_price)): 
        if step == 0:
            df_gamma["B利息成本"] = 0.0
            df_gamma["B累積成本"] = df_gamma["B增減成本"].iloc[0]
        else:
            df_gamma.at[df_gamma.index[step],"B利息成本"] \
                = df_gamma["B累積成本"].iloc[step-1] *  (exp( r *(df_price["T-t"].iloc[step-1]-df_price["T-t"].iloc[step]) )-1)
            df_gamma.at[df_gamma.index[step],"B累積成本"] \
                = df_gamma["B累積成本"].iloc[step-1] + df_gamma["B增減成本"].iloc[step] + df_gamma["B利息成本"].iloc[step]
    # 計算現貨成本
    df_gamma["現貨增減量"] = df_gamma["現貨持有量"] - df_gamma["現貨持有量"].shift()
    df_gamma["現貨增減量"].iloc[0] = df_gamma["現貨持有量"].iloc[0]
    df_gamma["現貨增減成本"] = df_gamma["現貨增減量"] * df_price["St"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_gamma["現貨利息成本 "] = 0.0
            df_gamma["現貨累積成本"] = df_gamma["現貨增減成本"].iloc[0]
        else:
            df_gamma.at[df_gamma.index[step],"現貨利息成本 "] = df_gamma["現貨累積成本"].iloc[step-1] *  (exp( r *(df_price["T-t"].iloc[step-1]-df_price["T-t"].iloc[step]) )-1)
            df_gamma.at[df_gamma.index[step],"現貨累積成本"] = df_gamma["現貨累積成本"].iloc[step-1] \
                                                        + df_gamma["現貨增減成本"].iloc[step] \
                                                        + df_gamma["現貨利息成本 "].iloc[step]
    df_gamma["A部位損益"] = ( sell_price * exp( r * (TTE-df_price["T-t"]) ) -  df_price["A_Close"] ) * quantity
    df_gamma["B部位損益"] = df_gamma["B持有量"] * df_price["B_Settlement Price"] - df_gamma["B累積成本"]
    df_gamma["現貨部位損益"] =  df_gamma["現貨持有量"] * df_price["St"] - df_gamma["現貨累積成本"]
    df_gamma["總損益"] =  df_gamma["A部位損益"] + df_gamma["B部位損益"] + df_gamma["現貨部位損益"]
    df_gamma = pd.concat([df_price["T-t"], df_gamma.astype(float)],axis=1)
    return df_gamma.round(2)







