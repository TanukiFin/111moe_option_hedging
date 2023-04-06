import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import datetime
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from scipy import log,exp,sqrt,stats
from scipy.stats import norm
import random
from myfunction import bsmodel
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Delta hedging",
    page_icon="📈",
    layout="wide",
)

S0 = 49

st.header("Delta hedging")

st.text("券商賣100個單位的選擇權，參數如下")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**S0 =** $49")
    K_A = st.number_input("**K =**",min_value=40,max_value=60,value=50)
    r = st.number_input("**r =**",min_value=0.0,max_value=0.1,value=0.05)
    sigma = st.number_input("**sigma =**",min_value=0.1,max_value=0.5,value=0.2)
    T = st.selectbox(
    "**T**",
    ( round(20/52,4), 1) )
    
with c2:
    CP_A = st.selectbox(
    "Type: 券商要賣Call還是賣Put",
    ("Short Call","Short Put") )
    sell_price = st.number_input("Sell Price: 券商賣這個選擇權的售價，應高於理論價值(相當於成本)，這樣才有利潤",min_value=1,max_value=20,value=3)
    st.metric(label="option value at t=0", value=round(bsmodel.call(S0,K_A,r,sigma,T).price,2))
K_B=50 ; K_C=50
CP_B="Call" ; CP_C="Call" 


# 側邊
with st.sidebar:
    st.markdown("**NO PARAM**")
    St_sce = st.sidebar.selectbox(
    "股價情境",
    ("大漲","小漲","持平","小跌","大跌","17.2","17.3"),  )#label_visibility ="collapsed"
df_St=bsmodel.get_default_St(St_sce, r=r, sigma=sigma, T=T)

df_price = bsmodel.get_greeks(df_St, K_list=[K_A,K_B,K_C], CP=[CP_A, CP_B, CP_C], r=r, sigma=sigma, T=T)   

# 股價 & Greek Letters圖 ==================================================================================
c1, c2 = st.columns(2)
with c1:
    fig = px.line(df_price.round(2), x="第t期", y="St", title="Stock Price",height=300, width=400, template="plotly_white").update_layout(showlegend=False)
    st.plotly_chart(fig)
with c2:
    fig = px.line(df_price.round(2), x="第t期", y=["A_Price"], title="Option Price", 
                  height=300, width=400, template="plotly_white").update_layout(showlegend=False)
    st.plotly_chart(fig)

# 損益圖 ==================================================================================
# get_delta_hedge(df_price, r=0.05, sigma=0.3, T=1, sell_price=3)
df_delta = bsmodel.get_delta_hedge(df_price, r, sigma, T, sell_price)
df_delta2 = bsmodel.get_delta_hedge_2week(df_price, freq=2, r=r, sigma=sigma, T=T, sell_price=sell_price)
df_delta5 = bsmodel.get_delta_hedge_2week(df_price, freq=5, r=r, sigma=sigma, T=T, sell_price=sell_price)
df_delta10 = bsmodel.get_delta_hedge_2week(df_price, freq=10, r=r, sigma=sigma, T=T, sell_price=sell_price)
df_delta20 = bsmodel.get_delta_hedge_2week(df_price, freq=20, r=r, sigma=sigma, T=T, sell_price=sell_price)

df_all_hedge = pd.DataFrame()
df_all_hedge["第t期"] = df_delta["第t期"]
df_all_hedge["No Hedging"] = df_delta["A部位_損益"]
df_all_hedge["Delta1"] = df_delta["總部位_損益"]
df_all_hedge["Delta2"] = df_delta2["總部位_損益"]
df_all_hedge["Delta5"] = df_delta5["總部位_損益"]
df_all_hedge["Delta10"] = df_delta10["總部位_損益"]
df_all_hedge["Delta20"] = df_delta20["總部位_損益"]


hedge_list = []
cname= ["No Hedging","Delta1","Delta5","Delta20"]
clist = st.columns(len(cname))
for count in range(len(clist)):
    with clist[count]: 
        if st.checkbox(cname[count],value=True):
            hedge_list.append(cname[count])


# 圖: 全部避險損益
fig = px.line(df_all_hedge.round(2), x="第t期", y=hedge_list, title="Delta Hedging", \
               labels={"value":"profit"},height=400, width=600, template="plotly_white") 
fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
c1, c2 = st.columns([2,1])
with c1:
    st.plotly_chart(fig)
with c2:
    st.markdown("**No Hedging**: 不避險的損益")
    st.markdown("**Delta1**: 每期避險")
    st.markdown("**Delta5**: 每五期避險(week0,week5,week10...)")
    st.markdown("**Delta20**: 僅第一期避險")

# 圖: Delta與現貨應持有量的關係
df_spot = pd.DataFrame()
df_spot["第t期"] = df_delta["第t期"]
df_spot["A部位Delta"] = df_price["A_總Delta"]
df_spot["避險部位_現貨持有量"] = df_delta["現貨部位_持有量"]
df_spot["Portfolio_Delta"] = round(df_price["A_總Delta"]+df_delta["現貨部位_持有量"],2)
fig = px.line(df_spot, x="第t期", y=["A部位Delta","避險部位_現貨持有量","Portfolio_Delta"], title="Delta Hedging Delta與現貨應持有量的關係", \
               labels={"x":"第t期"},height=400, width=600, template="plotly_white",)
fig.update_layout(legend=dict( orientation="h",
    yanchor="bottom", y=1.02,
    xanchor="right", x=1))
#st.plotly_chart(fig)

st.info(f"""目前參數:　　:red[S0]={S0},　　:red[K]={K_A},　　:red[r]={r},　　:red[T]={round(T,2)},　　:red[sigma]={sigma} 
        \n 　　　　　　:red[type]={CP_A},　　:red[sell price]={sell_price}""")

# 圖: Delta Hedging 各部位損益
fig = px.line(df_delta.round(2), x="第t期", y=["A部位_損益","現貨部位_損益","總部位_損益"], title="Delta Hedging 各部位損益(每期避險)", \
               labels={"value":"profit"},height=400, width=600, template="plotly_white") 
fig.update_layout(legend=dict( orientation="h",
    yanchor="bottom", y=1.02,
    xanchor="right", x=1))
#st.plotly_chart(fig)

# 圖: Delta Hedging 不同頻率的現貨持有量
df_spot = pd.DataFrame()
df_spot["第t期"] = df_delta["第t期"]
df_spot["Delta1"] = df_delta["現貨部位_持有量"]
df_spot["Delta2"] = df_delta2["現貨部位_持有量"]
df_spot["Delta5"] = df_delta5["現貨部位_持有量"]
df_spot["Delta10"] = df_delta10["現貨部位_持有量"]
df_spot["Delta20"] = df_delta20["現貨部位_持有量"]
fig = px.line(df_spot, x="第t期", y=cname[1:] , title="Delta Hedging 不同頻率的現貨持有量", \
               labels={"x":"第t期","value":"現貨部位_持有量"},height=400, width=600, template="plotly_white",)
fig.update_layout(legend=dict( orientation="h",
    yanchor="bottom", y=1.02,
    xanchor="right", x=1))
#st.plotly_chart(fig)
st.dataframe(df_price[["第t期","St","A_Price","A_Delta","A_Gamma","A_Vega","A_Theta"]])
st.markdown("**每期避險**")
st.dataframe(df_delta)
st.markdown("**每5期避險**")
st.dataframe(df_delta5)
st.markdown("**靜態避險(僅第一期避險)**")
st.dataframe(df_delta20)