import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import datetime as dt
import matplotlib.pyplot as plt
import plotly.express as px
import warnings
warnings.filterwarnings("ignore")

api_key="12a476fe-a758-47da-bd31-4c4942430f23"
api_key="d8ae61a9-6d58-491f-9128-7fecaddf0324"
v0_url = "https://api.helius.xyz/v0"
v1_url = "https://api.helius.xyz/v1"

st.set_page_config(
    page_title="BM GBM",
    page_icon="📈",
    #layout="wide",
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

class getBM:
    def __init__(self,steps,numberOfSims,S0,sigma):
        # steps = number of steps
        # number = number of sims
        T = 1 # time in years
        dt = T/steps # calc each time step

        dw = sigma*np.random.normal(0, np.sqrt(dt), size=(steps,numberOfSims))
        dw = np.vstack([np.zeros(numberOfSims), dw]) 
        St = S0 + dw.cumsum(axis=0)

        time = np.linspace(0,T,steps+1)
        self.df=pd.DataFrame(St, index=time)
        self.fig = px.line(self.df, height=400, width=600, template="plotly_white").update_layout(showlegend=False)


class getGBM:
    def __init__(self,steps,numberOfSims,mu,S0,sigma):
        # drift coefficent
        # initial stock price
        # volatility
        T = 1 # time in years
        dt = T/steps # calc each time step
        
        Rt = (mu - sigma ** 2 / 2) * dt + sigma * np.random.normal(0, 1          , size=(steps, numberOfSims)) * np.sqrt(dt) # 每一期的增量/漲跌幅
        Rt = (mu - sigma ** 2 / 2) * dt + sigma * np.random.normal(0, np.sqrt(dt), size=(steps, numberOfSims))  # 每一期的增量/漲跌幅
        self.Rt = np.vstack([np.zeros(numberOfSims), Rt])
        # 待修正
        self.lnSt = (1+self.Rt).cumprod(axis=0)
        St = np.exp(self.Rt)
        self.St = St
        # np.random.normal(loc平均=0.0, scale標準差=1.0, size輸出大小=None)
        St = np.exp(
            (mu - sigma ** 2 / 2) * dt
            + sigma * np.random.normal(0, np.sqrt(dt), size=(steps,numberOfSims))
        )  # 每一期的增量/漲跌幅
        St = np.vstack([np.ones(numberOfSims), St])  # 垂直合併二維數列(水平=hstack)
        St = S0 * St.cumprod(axis=0) # 累積乘積 
        
        time = np.linspace(0,T,steps+1)
        self.df = pd.DataFrame(St, index=time)
        self.fig = px.line(self.df, height=400, width=600, template="plotly_white").update_layout(showlegend=False)

# 2.  ==========================================================================================
st.header("BM")
st.markdown(
"""
算術布朗運動 Arithmetic Brownian Motion (ABM) 

多了一個sigma，t=0時S不一定=0，符合股價
""")
st.latex(r"""
\Delta W_t \text{\textasciitilde} \mathcal{N}(0, \textcolor{red}{sigma} \times \Delta t) 
""")
c1, c2 = st.columns(2)
with c1:
    steps = st.slider("number of steps(BM)", 10, 100, 10, 10)
with c2:
    numberOfSims = st.slider("number of sims(BM)", 5, 50, 10, 5)
c3, c4 = st.columns(2)
with c3:
    S0 = st.slider("S0(BM)", 10, 100, 50, 10)
with c4:
    sigma = st.slider("sigma(BM)", 0.1, 1.0, 0.3, 0.05)
    
BMline = getBM(steps,numberOfSims,S0,sigma)
st.plotly_chart(BMline.fig)

st.code(
"""
import
""")


# 3. ==========================================================================================
st.header("GBM")
st.markdown(
"""
幾何布朗運動 Geometric Brownian Motion

累加變成累積相乘，股價不會變0
""")


c1, c2 = st.columns(2)
with c1:
    steps = st.slider("number of steps2", 10, 100, 10, 10)
with c2:
    numberOfSims = st.slider("number of sims2", 5, 50, 10, 5)

c3, c4, c5 = st.columns(3)
with c3:
    mu = st.slider("drift coefficent", 0.1, 1.0, 0.1, 0.1)
with c4:
    S0 = st.slider("S0", 10, 100, 50, 10)
with c5:
    sigma = st.slider("sigma", 0.1, 1.0, 0.3, 0.05)


tab1, tab2, tab3, tab4 = st.tabs(["📈 Chart", "🗃 Rt", "🗃 lnSt", "🗃 St"])

GBMline = getGBM(steps, numberOfSims, mu, S0, sigma)
tab1.plotly_chart(GBMline.fig)
tab2.dataframe(GBMline.Rt)
tab3.dataframe(GBMline.lnSt)
tab4.dataframe(GBMline.St)

st.code("""
mu = 0.1 # drift coefficent
steps = 3 # number of steps
T = 1 # time in years
numberOfSims = 5 # number of sims
S0 = 100 # initial stock price
sigma = 0.3 # volatility
dt = T/steps # calc each time step

St = np.exp(
    (mu - sigma ** 2 / 2) * dt
    + sigma * np.random.normal(0, np.sqrt(dt), size=(steps,numberOfSims))
)  # 每一期的增量/漲跌幅
St = np.vstack([np.ones(numberOfSims), St])  # 垂直合併二維數列(水平=hstack)
St = S0 * St.cumprod(axis=0) # 累積加減

time = np.linspace(0,T,steps+1)
self.df = pd.DataFrame(St, index=time)
self.fig = px.line(self.df, height=400, width=700, template="plotly_white").update_layout(showlegend=False)
""")





