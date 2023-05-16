"""
=== Calculate Option Value, Greeks ===
1. call(self,S,K,r,sigma,T)
2. put(self,S,K,r,sigma,T)
3. get_greeks(df_St, K_list, CP, r=0.05, sigma=0.3, T=1, steps=20)
=== Simulate Stock Price(Future) ===
1. get_GBM_St(steps=20, r=0.05, sigma=0.3, T=1)
2. get_default_St(St_sce, r=0.05, sigma=0.3, T=1, steps=20)
===
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

#%% === Calculate Option Value, Greeks ===
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
def get_greeks(df_St, K_list, CP, r=0.05, sigma=0.3, T=1):
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
def get_greeks_vol(df_St, K_list, CP, r=0.01045, sigma=[0.3], TTE=1, conversion=1):
    df_greek = pd.DataFrame(index = df_St.index,columns=["A_Price","A_Delta","A_Gamma","A_Vega", "A_Theta",
                                     "B_Price","B_Delta","B_Gamma","B_Vega", "B_Theta",
                                     "C_Price","C_Delta","C_Gamma","C_Vega", "C_Theta"])

    for i in range(len(df_St)):
        option=[]
        for x in range(len(CP)):
            c = call(df_St["St"].iloc[i], K_list[x], r, sigma[i], df_St["T-t"].iloc[i])
            p = put(df_St["St"].iloc[i], K_list[x], r, sigma[i], df_St["T-t"].iloc[i])
            if CP[x] == "Long Call" or CP[x] == "Call":
                option.append( np.hstack([c.price, c.greek]) )
            elif CP[x] == "Long Put" or CP[x] == "Put":
                option.append( np.hstack([p.price, p.greek]) )
            elif CP[x] == "Short Call":
                option.append( np.hstack([c.price, c.greek*-1]) )
            elif CP[x] == "Short Put":
                option.append( np.hstack([p.price, p.greek*-1]) )
        
        df_greek.iloc[i] = np.hstack([option[0], option[1], option[2]]) *conversion     
    
    return pd.concat([df_St[["St","T-t","HV","A_Close","A_IV","B_Settlement Price","B_IV"]], df_greek],axis=1).fillna(0).round(8)

#%% === Simulate Stock Price(Future) ===
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