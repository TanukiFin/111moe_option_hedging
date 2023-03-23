import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import datetime as dt
import matplotlib.pyplot as plt
import plotly.express as px
from scipy import log,exp,sqrt,stats
from scipy.stats import norm
import random

st.set_page_config(
    page_title="Delta-Gamma hedging",
    page_icon="📈",
    layout="wide",
)

# 不要有hamburger, footer: Made with Streamlit
st.markdown("""
<style>
.css-9s5bis edgvbvh3
{
    visibility: hidden;
}
.css-164nlkn egzxvld1 
{
    visibility: hidden;
}
</style>
""",unsafe_allow_html=True)
st.header("Delta-Gamma-Vega hedging")

# 參數 ==========================================================================================
numberOfSims = 1 # number of sims
mu = 0.1 # drift coefficent
S0 = 50 # initial stock price
sigma = 0.3 # volatility
steps = 20 # number of steps
T = 1 # time in years
dt = T/steps # calc each time step
quantity = -100 # brokerage sales quantity ex. -100=賣100個
sell_price = 3 
r=0.05

# function ===================================================================================================
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
def get_GBM_St():
    St = np.exp(
        (mu - sigma ** 2 / 2) * dt
        + sigma * np.random.normal(0, np.sqrt(dt), size=(steps,numberOfSims))
    )  # 每一期的增量/漲跌幅
    St = np.vstack([np.ones(numberOfSims), St])  # 垂直合併二維數列(水平=hstack)
    St = S0 * St.cumprod(axis=0) # 累積加減

    time = np.linspace(0,T,steps+1)
    df_St = pd.concat([pd.DataFrame(time,columns=["第t期"]),pd.DataFrame(St,columns=["St"])],axis=1)
    
    return df_St
def get_greeks(df_St):
    df_greek = pd.DataFrame(columns=["A_Price","A_Delta","A_Gamma","A_Vega", "A_Theta",
                                     "B_Price","B_Delta","B_Gamma","B_Vega", "B_Theta",
                                     "C_Price","C_Delta","C_Gamma","C_Vega", "C_Theta",
                                     "A_總Delta","A_總Gamma","A_總Vega"])
    
    K_list = [K_A,K_B,K_C]
    CP = [CP_A, CP_B, CP_C]
    for i in range(len(df_St)):
        option=[]
        for x in range(len(CP)):
            c = call(df_St.at[i,"St"], K_list[x], r, sigma, T-df_St.at[i,"第t期"])
            p = put(df_St.at[i,"St"], K_list[x], r, sigma, T-df_St.at[i,"第t期"])
            if CP[x] == "Call":
                option.append( np.hstack([c.price, c.greek]) )
            elif CP[x] == "Put":
                option.append( np.hstack([p.price, p.greek]) )
            elif CP[x] == "Short Call":
                option.append( np.hstack([c.price, c.greek*-1]) )
        df_greek.loc[i] = np.hstack([option[0], option[1], option[2], option[0][1:4]*quantity])      
    
    return pd.concat([df_St, df_greek],axis=1)

# function hedging ===================================================================================================
def get_delta_hedge(df_price):
    df_delta = pd.DataFrame(columns=["現貨部位_持有量","現貨部位_增減量","現貨部位_增減成本","現貨部位_利息成本",
                                    "現貨部位_累積成本","A部位_損益","現貨部位_損益","總部位_損益"])
    #df_delta["現貨部位_持有量"] = round( -1 * df_price["A部位總Delta"], 2 )
    df_delta["現貨部位_持有量"] = -1 * df_price["A_總Delta"]
    df_delta["現貨部位_增減量"] = df_delta["現貨部位_持有量"] - df_delta["現貨部位_持有量"].shift()
    df_delta["現貨部位_增減量"].iloc[0] = df_delta["現貨部位_持有量"].iloc[0]
    df_delta["現貨部位_增減成本"] = df_delta["現貨部位_增減量"] * df_price["St"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_delta["現貨部位_利息成本"].iloc[0] = 0.0
            df_delta["現貨部位_累積成本"].iloc[0] = df_delta["現貨部位_增減成本"].iloc[0]
        else:
            df_delta.at[step,"現貨部位_利息成本"] = df_delta["現貨部位_累積成本"].iloc[step-1] *  (exp(r*dt)-1)
            df_delta.at[step,"現貨部位_累積成本"] = df_delta["現貨部位_累積成本"].iloc[step-1] \
                                                        + df_delta["現貨部位_增減成本"].iloc[step] \
                                                        + df_delta["現貨部位_利息成本"].iloc[step]
    df_delta["A部位_損益"] = ( sell_price*exp(r*df_price["第t期"]/T) -  df_price["A_Price"] ) * quantity
    df_delta["現貨部位_損益"] =  df_delta["現貨部位_持有量"] * df_price["St"] - df_delta["現貨部位_累積成本"]
    df_delta["總部位_損益"] =  df_delta["A部位_損益"] + df_delta["現貨部位_損益"]
    df_delta = pd.concat([df_price["第t期"],df_delta.astype(float)],axis=1)
    return df_delta.round(2)
def get_gamma_hedge(df_price):
    # B部位
    df_gamma = pd.DataFrame(columns=["B部位_持有量","B部位_增減量","B部位_增減成本","B部位_利息成本","B部位_累積成本","持有B後的_總Delta",
                                     "現貨部位_持有量","現貨部位_增減量","現貨部位_增減成本","現貨部位_利息成本","現貨部位_累積成本",
                                     "A部位_損益","B部位_損益","現貨部位_損益","總部位_損益"])
    #df_gamma["B部位_持有量"] = round( -1 * df_price["A部位總Gamma"] / df_price["B選擇權Gamma"], 4)
    df_gamma["B部位_持有量"] =  -1 * df_price["A_總Gamma"] / df_price["B_Gamma"]
    df_gamma["B部位_持有量"][df_gamma["B部位_持有量"].isnull()]=0
    df_gamma.replace([np.inf, -np.inf], 0, inplace=True)
    df_gamma["B部位_增減量"] = df_gamma["B部位_持有量"] - df_gamma["B部位_持有量"].shift()
    df_gamma["B部位_增減量"].iloc[0] = df_gamma["B部位_持有量"].iloc[0]
    df_gamma["B部位_增減成本"] = df_gamma["B部位_增減量"] * df_price["B_Price"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_gamma["B部位_利息成本"] = 0.0
            df_gamma["B部位_累積成本"] = df_gamma["B部位_增減成本"].iloc[0]
        else:
            df_gamma.at[step,"B部位_利息成本"] = df_gamma["B部位_累積成本"].iloc[step-1] *  (exp(r*dt)-1)
            df_gamma.at[step,"B部位_累積成本"] = df_gamma["B部位_累積成本"].iloc[step-1] \
                                                        + df_gamma["B部位_增減成本"].iloc[step] \
                                                        + df_gamma["B部位_利息成本"].iloc[step]
    df_gamma["持有B後的_總Delta"] = df_price["A_總Delta"] + df_gamma["B部位_持有量"] * df_price["B_Delta"]
    # 現貨部位
    #df_gamma["現貨部位_持有量"] = round( -1 * df_gamma["持有B後的_總Delta"], 2 )
    df_gamma["現貨部位_持有量"] = -1 * df_gamma["持有B後的_總Delta"]
    df_gamma["現貨部位_增減量"] = df_gamma["現貨部位_持有量"] - df_gamma["現貨部位_持有量"].shift()
    df_gamma["現貨部位_增減量"].iloc[0] = df_gamma["現貨部位_持有量"].iloc[0]
    df_gamma["現貨部位_增減成本"] = df_gamma["現貨部位_增減量"] * df_price["St"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_gamma["現貨部位_利息成本"] = 0.0
            df_gamma["現貨部位_累積成本"] = df_gamma["現貨部位_增減成本"].iloc[0]
        else:
            df_gamma.at[step,"現貨部位_利息成本"] = df_gamma["現貨部位_累積成本"].iloc[step-1] *  (exp(r*dt)-1)
            df_gamma.at[step,"現貨部位_累積成本"] = df_gamma["現貨部位_累積成本"].iloc[step-1] \
                                                        + df_gamma["現貨部位_增減成本"].iloc[step] \
                                                        + df_gamma["現貨部位_利息成本"].iloc[step]
    df_gamma["A部位_損益"] = ( sell_price*exp(r*df_price["第t期"]/T) -  df_price["A_Price"] ) * quantity
    df_gamma["B部位_損益"] = df_gamma["B部位_持有量"] * df_price["B_Price"] - df_gamma["B部位_累積成本"]
    df_gamma["現貨部位_損益"] =  df_gamma["現貨部位_持有量"] * df_price["St"] - df_gamma["現貨部位_累積成本"]
    df_gamma["總部位_損益"] =  df_gamma["A部位_損益"] + df_gamma["B部位_損益"] + df_gamma["現貨部位_損益"]
    df_gamma = pd.concat([df_price["第t期"],df_gamma.astype(float)],axis=1)
    return df_gamma.round(2)
def get_vega_hedge(df_price):
    # B部位
    df_vega = pd.DataFrame(columns=["B部位_持有量","B部位_增減量","B部位_增減成本","B部位_利息成本","B部位_累積成本",
                                    "C部位_持有量","C部位_增減量","C部位_增減成本","C部位_利息成本","C部位_累積成本",
                                    "現貨部位_持有量","現貨部位_增減量","現貨部位_增減成本","現貨部位_利息成本","現貨部位_累積成本",
                                    "A部位_損益","B部位_損益","C部位_損益","現貨部位_損益","總部位_損益"])
    for step in range(0, len(df_price)): #0~20
        try:
            # Delta、Gamma、Vega
            X = np.array([[df_price["B_Delta"][step], df_price["C_Delta"][step], 1], 
                          [df_price["B_Gamma"][step], df_price["C_Gamma"][step], 0], 
                          [df_price["B_Vega"][step], df_price["C_Vega"][step], 0]]) # B + C + Spot = A
            Y = np.array([-df_price["A_總Delta"][step], -df_price["A_總Gamma"][step], -df_price["A_總Vega"][step]])
            ans = np.linalg.solve(X, Y)
            df_vega.at[step,"B部位_持有量"]=ans[0]
            df_vega.at[step,"C部位_持有量"]=ans[1]
            df_vega.at[step,"現貨部位_持有量"]=ans[2]
            # 避險數量太大
            if ans[0]>10000 or ans[0]<-10000:
                print("EXT")
                df_vega.at[step,"B部位_持有量"]=df_vega["B部位_持有量"][step-1]
                df_vega.at[step,"C部位_持有量"]=df_vega["C部位_持有量"][step-1]
                df_vega.at[step,"現貨部位_持有量"]=df_vega["現貨部位_持有量"][step-1]
        except Exception as ex:
            df_vega.at[step,"B部位_持有量"] = 0
            df_vega.at[step,"C部位_持有量"] = 0
            df_vega.at[step,"現貨部位_持有量"] = -1 * df_price["A_總Delta"][step]
            pass
    df_vega.replace([np.inf, -np.inf], 0, inplace=True)
    # B
    df_vega["B部位_增減量"] = df_vega["B部位_持有量"] - df_vega["B部位_持有量"].shift()
    df_vega["B部位_增減量"].iloc[0] = df_vega["B部位_持有量"].iloc[0]
    df_vega["B部位_增減成本"] = df_vega["B部位_增減量"] * df_price["B_Price"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_vega["B部位_利息成本"] = 0.0
            df_vega["B部位_累積成本"] = df_vega["B部位_增減成本"].iloc[0]
        else:
            df_vega.at[step,"B部位_利息成本"] = df_vega["B部位_累積成本"].iloc[step-1] * (exp(r*dt)-1)
            df_vega.at[step,"B部位_累積成本"] = df_vega["B部位_累積成本"].iloc[step-1] \
                                                        + df_vega["B部位_增減成本"].iloc[step] \
                                                        + df_vega["B部位_利息成本"].iloc[step]  
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
    df_vega["現貨部位_增減量"] = df_vega["現貨部位_持有量"] - df_vega["現貨部位_持有量"].shift()
    df_vega["現貨部位_增減量"].iloc[0] = df_vega["現貨部位_持有量"].iloc[0]
    df_vega["現貨部位_增減成本"] = df_vega["現貨部位_增減量"] * df_price["St"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_vega["現貨部位_利息成本"] = 0.0
            df_vega["現貨部位_累積成本"] = df_vega["現貨部位_增減成本"].iloc[0]
        else:
            df_vega.at[step,"現貨部位_利息成本"] = df_vega["現貨部位_累積成本"].iloc[step-1] * (exp(r*dt)-1)
            df_vega.at[step,"現貨部位_累積成本"] = df_vega["現貨部位_累積成本"].iloc[step-1] \
                                                        + df_vega["現貨部位_增減成本"].iloc[step] \
                                                        + df_vega["現貨部位_利息成本"].iloc[step]
    df_vega["A部位_損益"] = ( sell_price*exp(r*df_price["第t期"]/T) -  df_price["A_Price"] ) * quantity
    df_vega["B部位_損益"] = df_vega["B部位_持有量"] * df_price["B_Price"] - df_vega["B部位_累積成本"]
    df_vega["C部位_損益"] = df_vega["C部位_持有量"] * df_price["C_Price"] - df_vega["C部位_累積成本"]
    df_vega["現貨部位_損益"] =  df_vega["現貨部位_持有量"] * df_price["St"] - df_vega["現貨部位_累積成本"]
    df_vega["總部位_損益"] =  df_vega["A部位_損益"] + df_vega["B部位_損益"] + df_vega["C部位_損益"] + df_vega["現貨部位_損益"]
    df_vega = pd.concat([df_price["第t期"], df_vega.astype(float)],axis=1)

    return df_vega.round(2)


# Strike Price ================================================================================================
c1, c2, c3 = st.columns(3)
with c1:
    st.text("券商賣100個單位的Call\n履約價=50")
    K_A = 50
    CP_A = "Short Call"

with c2:
    K_B = st.slider("避險工具K2", 30, 70, 48, 1)
    CP_B = st.radio("Boption",("Call","Put"),label_visibility="hidden")
with c3:
    K_C = st.slider("避險工具K3", 30, 70, 52, 1)
    CP_C = st.radio("Coption",("Call","Put"),label_visibility="hidden")

# 預設股價
@st.cache_data 
def bind_socket():
    df_St = get_GBM_St()
    return df_St
df_St = bind_socket()
df_price = get_greeks(df_St)

# 按Simulate St 股價才會變動
if st.button("Simulate St"):
    df_St = get_GBM_St()
    df_price = get_greeks(df_St)
    print("YOU CLICK")

# 股價 & Greek Letters圖 ==================================================================================



c1, c2 = st.columns(2)
with c1:
    fig = px.line(df_price.round(2), x="第t期", y="St", title="Stock Price",height=300, width=300, template="plotly_white").update_layout(showlegend=False)
    st.plotly_chart(fig)
with c2:
    fig = px.line(df_price.round(2), x="第t期", y=["A_Price","B_Price","C_Price"], title="Option Price", 
                  height=300, width=500, template="plotly_white")#.update_layout(showlegend=False)
    st.plotly_chart(fig)

# 損益圖 ==================================================================================
df_delta = get_delta_hedge(df_price)
df_gamma = get_gamma_hedge(df_price)
df_vega = get_vega_hedge(df_price)

df_all_hedge = pd.DataFrame(columns=["第t期","No Hedging","Delta Hedging","Delta-Gamma Hedging"])
df_all_hedge["第t期"] = df_delta["第t期"]
df_all_hedge["No Hedging"] = df_delta["A部位_損益"]
df_all_hedge["Delta Hedging"] = df_delta["總部位_損益"]
df_all_hedge["Delta-Gamma Hedging"] = df_gamma["總部位_損益"]
df_all_hedge["Delta-Gamma-Vega Hedging"] = df_vega["總部位_損益"]


fig = px.line(df_all_hedge.round(2), x="第t期", y=["No Hedging","Delta Hedging","Delta-Gamma Hedging","Delta-Gamma-Vega Hedging"], title="Delta-Gamma Hedging", \
               labels={"value":"profit"},height=300, width=500, template="plotly_white") 
st.plotly_chart(fig)

st.dataframe(df_all_hedge)

