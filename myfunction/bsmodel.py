"""
=== Calculate Option Value, Greeks ===
1. call(self,S,K,r,sigma,T)
2. put(self,S,K,r,sigma,T)
3. get_greeks(df_St, K_list, CP, r=0.05, sigma=0.3, T=1, steps=20)
=== Hedging ===
1. get_GBM_St(steps=20, r=0.05, sigma=0.3, T=1)
2. get_default_St(St_sce, r=0.05, sigma=0.3, T=1, steps=20)
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

# === Calculate Option Value, Greeks ===
def hello():
    return "HELLO"
def d1(S,K,r,sigma,T):
    return ((np.log(S/K) + (r + (sigma**2) / 2) * T)) / (sigma * np.sqrt(T))
def d2(S,K,r,sigma,T):
    return d1(S,K,r,sigma,T) - sigma * np.sqrt(T)
class call:
    def callprice(self,S,K,r,sigma,T):
        return norm.cdf(d1(S,K,r,sigma,T)) * S - norm.cdf(d2(S,K,r,sigma,T)) * K * np.exp(-r*T)
    
    def calldelta(self,S,K,r,sigma,T):
        return norm.cdf(d1(S,K,r,sigma,T))

    def callgamma(self,S,K,r,sigma,T):
        return norm.pdf(d1(S,K,r,sigma,T)) / (S * sigma * np.sqrt(T))

    def callvega(self,S,K,r,sigma,T):
        return S * norm.pdf(d1(S,K,r,sigma,T))*np.sqrt(T)

    def calltheta(self,S,K,r,sigma,T):
        return (-S * norm.pdf(d1(S,K,r,sigma,T)) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2(S,K,r,sigma,T))
    
    def __init__(self,S,K,r,sigma,T):
        self.S = S
        self.K = K
        self.r = r
        self.sigma = sigma
        self.T = T
        self.price = self.callprice(S,K,r,sigma,T)
        self.delta = self.calldelta(S,K,r,sigma,T)
        self.gamma = self.callgamma(S,K,r,sigma,T)
        self.vega = self.callvega(S,K,r,sigma,T)
        self.theta = self.calltheta(S,K,r,sigma,T)   
        self.greek = np.array([self.delta,self.gamma,self.vega,self.theta])
class put:
    def putprice(self, S, K, r, sigma, T):
        return norm.cdf(-d2(S,K,r,sigma,T)) * K * np.exp(-r * T) - norm.cdf(-d1(S,K,r,sigma,T)) * S

    def putdelta(self, S, K, r, sigma, T):
        return norm.cdf(d1(S, K, r, sigma, T)) - 1

    def putgamma(self, S, K, r, sigma, T):
        return norm.pdf(d1(S, K, r, sigma, T)) / (S * sigma * np.sqrt(T))

    def putvega(self, S, K, r, sigma, T):
        return S * norm.pdf(d1(S, K, r, sigma, T)) * np.sqrt(T)

    def puttheta(self, S, K, r, sigma, T):
        return (-S * norm.pdf(d1(S, K, r, sigma, T)) * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2(S, K, r, sigma, T))

    def __init__(self,S,K,r,sigma,T):
        self.S = S
        self.K = K
        self.r = r
        self.sigma = sigma
        self.T = T
        self.price = self.putprice(S,K,r,sigma,T)
        self.delta = self.putdelta(S,K,r,sigma,T)
        self.gamma = self.putgamma(S,K,r,sigma,T)
        self.vega = self.putvega(S,K,r,sigma,T)
        self.theta = self.puttheta(S,K,r,sigma,T)
        self.greek = np.array([self.delta,self.gamma,self.vega,self.theta])
def get_greeks(df_St, K_list, CP, r=0.05, sigma=0.3, T=1, steps=20):
    df_greek = pd.DataFrame(columns=["A_Price","A_Delta","A_Gamma","A_Vega", "A_Theta",
                                     "B_Price","B_Delta","B_Gamma","B_Vega", "B_Theta",
                                     "C_Price","C_Delta","C_Gamma","C_Vega", "C_Theta",
                                     "A_總Delta","A_總Gamma","A_總Vega"])
    

    for i in range(len(df_St)):
        option=[]
        for x in range(len(CP)):
            c = call(df_St.at[i,"St"], K_list[x], r, sigma, T-df_St.at[i,"t"])
            p = put(df_St.at[i,"St"], K_list[x], r, sigma, T-df_St.at[i,"t"])
            if CP[x] == "Long Call" or CP[x] == "Call":
                option.append( np.hstack([c.price, c.greek]) )
            elif CP[x] == "Long Put" or CP[x] == "Put":
                option.append( np.hstack([p.price, p.greek]) )
            elif CP[x] == "Short Call":
                option.append( np.hstack([c.price, c.greek*-1]) )
            elif CP[x] == "Short Put":
                option.append( np.hstack([p.price, p.greek*-1]) )
        
        df_greek.loc[i] = np.hstack([option[0], option[1], option[2], option[0][1:4]*quantity])      
    
    return pd.concat([df_St, df_greek],axis=1).fillna(0).round(4)

# === Simulate Stock Price(Future) ===
def get_GBM_St(steps=20, r=0.05, sigma=0.3, T=1):
    dt = T/steps # calc each time step
    
    St = np.exp(
        (mu - sigma ** 2 / 2) * dt
        + sigma * np.random.normal(0, np.sqrt(dt), size=(steps, numberOfSims))
    )  # 每一期的增量/漲跌幅
    St = np.vstack([np.ones(numberOfSims), St])  # 垂直合併二維數列(水平=hstack)
    St = S0 * St.cumprod(axis=0) # 累積加減

    time = np.linspace(0,T,steps+1)
    df_St = pd.concat([pd.DataFrame(time,columns=["t"]),pd.DataFrame(St,columns=["St"])],axis=1)   
    return df_St
def get_default_St(St_sce, r=0.05, sigma=0.3, T=1, steps=20):
    St_default = pd.read_csv("data/stock price.csv")
    df_St = pd.DataFrame( np.linspace(0,T,steps+1) )
    if St_sce == "大漲":
        c="St1"
    elif St_sce == "小漲":
        c="St2"
    elif St_sce == "持平":
        c="St3"
    elif St_sce == "小跌":
        c="St4"
    elif St_sce == "大跌":
        c="St5"
    elif St_sce == "17.2":
        c="St6"
    elif St_sce == "17.3":
        c="St7"
    df_St = pd.concat([df_St,St_default[c]],axis=1)
    df_St.columns=["t","St"]
    return df_St

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






