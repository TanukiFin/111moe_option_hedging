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

st.set_page_config(
    page_title="Delta hedging",
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

st.header("Delta hedging")

# function
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
    steps = 20 # number of steps
    numberOfSims = 1 # number of sims
    mu = 0.1 # drift coefficent
    T = 1 # time in years
    S0 = 50 # initial stock price
    sigma = 0.3 # volatility
    dt = T/steps # calc each time step
    quantity = -100 # brokerage sales quantity ex. -100=賣100個

    St = np.exp(
        (mu - sigma ** 2 / 2) * dt
        + sigma * np.random.normal(0, np.sqrt(dt), size=(steps,numberOfSims))
    )  # 每一期的增量/漲跌幅
    St = np.vstack([np.ones(numberOfSims), St])  # 垂直合併二維數列(水平=hstack)
    St = S0 * St.cumprod(axis=0) # 累積加減

    time = np.linspace(0,T,steps+1)
    df = pd.concat([pd.DataFrame(time,columns=["第t期"]),pd.DataFrame(St,columns=["St"])],axis=1)
    df_greek = pd.DataFrame(columns=["A_Price","A_Delta","A_Gamma","A_Vega", "A_Theta",
                                     "B_Price","B_Delta","B_Gamma","B_Vega", "B_Theta",
                                     "C_Price","C_Delta","C_Gamma","C_Vega", "C_Theta",
                                     "A_總Delta","A_總Gamma","A_總Vega"])
    
    K_list = [K_A,K_B,K_C]
    CP = [CP_A, CP_B, CP_C]
    for i in range(len(df)):
        option=[]
        for x in range(len(CP)):
            c = call(df.at[i,"St"], K_list[x], r, sigma, T-df.at[i,"第t期"])
            p = put(df.at[i,"St"], K_list[x], r, sigma, T-df.at[i,"第t期"])
            if CP[x] == "Long Call":
                option.append( np.hstack([c.price, c.greek]) )
            elif CP[x] == "Long Put":
                option.append( np.hstack([p.price, p.greek]) )
            elif CP[x] == "Short Call":
                option.append( np.hstack([c.price, c.greek*-1]) )
            elif CP[x] == "Short Put":
                option.append( np.hstack([p.price, p.greek*-1]) )
        df_greek.loc[i] = np.hstack([option[0], option[1], option[2], option[0][1:4]*quantity])      
    
    return pd.concat([df,df_greek],axis=1)
steps = 20 # number of steps
T = 1 # time in years
quantity = -100 # brokerage sales quantity ex. -100=賣100個
sell_price = 3 
dt = T/steps # calc each time step
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
    df_delta["A部位_損益"] = ( sell_price*exp(r*df["第t期"]/T) -  df_price["A_Price"] ) * quantity
    df_delta["現貨部位_損益"] =  df_delta["現貨部位_持有量"] * df_price["St"] - df_delta["現貨部位_累積成本"]
    df_delta["總部位_損益"] =  df_delta["A部位_損益"] + df_delta["現貨部位_損益"]
    df_delta = pd.concat([df_price["第t期"],df_delta.astype(float)],axis=1)
    return df_delta.round(2)

# Strike Price ================================================================================================
c1, c2, c3 = st.columns(3)
with c1:
    st.text("券商賣100個單位的Call\n履約價=50")
    K_A = 50
    CP_A = "Short Call"

with c2:
    K_B = st.slider("K2", 30, 70, 48, 1)
    CP_B = st.radio("Boption",("Long Call","Long Put","Short Call","Short Put"),label_visibility="hidden")
with c3:
    K_C = st.slider("K3", 30, 70, 52, 1)
    CP_C = st.radio("Coption",("Long Call","Long Put","Short Call","Short Put"),label_visibility="hidden")

st.button("Simulate")

r=0.05
df = get_GBM_St()
# 股價 & Greek Letters圖 ==================================================================================
c1, c2 = st.columns(2)
with c1:
    fig = px.line(df.round(2), x="第t期", y="St", title="Stock Price",height=300, width=300, template="plotly_white").update_layout(showlegend=False)
    st.plotly_chart(fig)
with c2:
    fig = px.line(df.round(2), x="第t期", y=["A_Price","B_Price","C_Price"], title="Option Price", 
                  height=300, width=500, template="plotly_white")#.update_layout(showlegend=False)
    st.plotly_chart(fig)

# 損益圖 ==================================================================================


df_price = get_GBM_St()
df_delta = get_delta_hedge(df_price)
fig = px.line(df_delta.round(2), x="第t期", y=["總部位_損益","A部位_損益"], title="Delta Hedging", \
               labels={"value":"profit"},height=300, width=500, template="plotly_white") \
                        .for_each_trace(lambda t: t.update(name={'總部位_損益': "Delta hedging",'A部位_損益': "No hedging"}[t.name]))
st.plotly_chart(fig)

st.dataframe(df_delta)

