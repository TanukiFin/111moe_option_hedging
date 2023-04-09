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
    page_title="Delta Hedging - GBM",
    page_icon="📈",
    layout="wide",
)

S0 = 50 # initial stock price

# 打開網頁時，隨機跑一個股價 ==============================================================================
if 'openweb' not in st.session_state:
    st.session_state.openweb = True
    df_St = bsmodel.get_GBM_St()
    st.session_state.df_St = df_St
    print("=== START ===")

# 側邊 ==============================================================================
with st.sidebar:
    st.markdown("**GBM模型模擬股價的參數**")
    steps_input = st.number_input("**steps =**", min_value=10,max_value=70,value=20)
    r_input = st.number_input("**r =**",min_value=0.0,max_value=0.1,value=0.05)
    sigma_input = st.number_input("**sigma =**", min_value=0.1,max_value=1.0,value=0.3)
    T_input = st.number_input("**T =**",min_value=0.1,max_value=2.0,value=1.0)
    # 按Simulate St 股價才會變動
    if st.button("Simulate St"):
        df_St = bsmodel.get_GBM_St(steps=steps_input, r=r_input, sigma=sigma_input, T=T_input)
        st.session_state.df_St = df_St # 暫存df
    st.markdown("此頁的股價產生方式為根據GBM模型隨機產生，每次點選網頁左側的[Simulate St]按鈕，即會根據所選參數產生新的隨機股價。")

# ==============================================================================


st.header("Delta Hedging - GBM")
st.markdown("券商賣100個單位的選擇權，參數可調整的僅有履約價(K)、Type、Sell Price，其餘皆跟隨網頁左側的GBM模型參數。")
st.markdown("**S0 =** $50")
c1, c2 = st.columns(2)
with c1:
    K_A = st.number_input("**K =**",min_value=40,max_value=60,value=50)
with c2:
    CP_A = st.selectbox(
    "Type: 券商要賣Call還是賣Put",
    ("Short Call","Short Put") )
    sell_price = st.number_input("Sell Price: 券商賣這個選擇權的售價，應高於理論價值(相當於成本)，這樣才有利潤",min_value=1,max_value=20,value=8)
    st.metric(label="option value at t=0", value=round(bsmodel.call(S0,K_A,r_input,sigma_input,T_input).price,2))
K_B=50 ; K_C=50
CP_B="Call" ; CP_C="Call" 

st.info(f"""目前參數:　　:red[S0]={S0},　　:red[K]={K_A},　　:red[r]={r_input},　　:red[T]={round(T_input,2)},　　:red[sigma]={sigma_input} 
        \n 　　　　　　:red[type]={CP_A},　　:red[sell price]={sell_price}""")


df_price = bsmodel.get_greeks(st.session_state.df_St, K_list=[K_A,K_B,K_C], CP = [CP_A, CP_B, CP_C])   

# 股價 & Greek Letters圖 ==================================================================================
c1, c2 = st.columns(2)
with c1:
    fig = px.line(df_price.round(2), x="t", y="St", title="Stock Price",height=300, width=400, template="plotly_white").update_layout(showlegend=False)
    st.plotly_chart(fig)
with c2:
    fig = px.line(df_price.round(2), x="t", y=["A_Price"], title="Option Price", 
                  height=300, width=400, template="plotly_white").update_layout(showlegend=False)
    st.plotly_chart(fig)

# 損益圖 ==================================================================================
df_delta = bsmodel.get_delta_hedge(df_price, r_input, sigma_input, T_input, sell_price)
df_delta2 = bsmodel.get_delta_hedge_2week(df_price, freq=2, r=r_input, sigma=sigma_input, T=T_input, sell_price=sell_price)
df_delta5 = bsmodel.get_delta_hedge_2week(df_price, freq=5, r=r_input, sigma=sigma_input, T=T_input, sell_price=sell_price)
df_delta10 = bsmodel.get_delta_hedge_2week(df_price, freq=10, r=r_input, sigma=sigma_input, T=T_input, sell_price=sell_price)
df_delta20 = bsmodel.get_delta_hedge_2week(df_price, freq=20, r=r_input, sigma=sigma_input, T=T_input, sell_price=sell_price)

df_all_hedge = pd.DataFrame()
df_all_hedge["t"] = df_delta["t"]
df_all_hedge["No Hedging"] = df_delta["Option_Profit"]
df_all_hedge["Delta1"] = df_delta["Total_Profit"]
df_all_hedge["Delta2"] = df_delta2["Total_Profit"]
df_all_hedge["Delta5"] = df_delta5["Total_Profit"]
df_all_hedge["Delta10"] = df_delta10["Total_Profit"]
df_all_hedge["Delta20"] = df_delta20["Total_Profit"]


hedge_list = []
cname= ["No Hedging","Delta1","Delta2","Delta5","Delta10","Delta20"]
clist = st.columns(len(cname))
for count in range(len(clist)):
    with clist[count]: 
        if st.checkbox(cname[count],value=True):
            hedge_list.append(cname[count])


# 圖: 全部避險損益
fig = px.line(df_all_hedge.round(2), x="t", y=hedge_list, title="Delta Hedging", \
               labels={"value":"profit"},height=400, width=600, template="plotly_white") 
fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
st.plotly_chart(fig)

# 圖: Delta與現貨應持有量的關係
df_spot = pd.DataFrame()
df_spot["t"] = df_delta["t"]
df_spot["A部位Delta"] = df_price["A_總Delta"]
df_spot["避險部位_現貨持有量"] = df_delta["Holding_shares"]
df_spot["Portfolio_Delta"] = round(df_price["A_總Delta"]+df_delta["Holding_shares"],2)
fig = px.line(df_spot, x="t", y=["A部位Delta","避險部位_現貨持有量","Portfolio_Delta"], title="Delta Hedging Delta與現貨應持有量的關係", \
               labels={"x":"t"},height=400, width=600, template="plotly_white",)
fig.update_layout(legend=dict( orientation="h",
    yanchor="bottom", y=1.02,
    xanchor="right", x=1))
st.plotly_chart(fig)

# 圖: Delta Hedging 各部位損益
fig = px.line(df_delta.round(2), x="t", y=["Option_Profit","HedgingSpot_Profit","Total_Profit"], title="Delta Hedging 各部位損益(每期避險)", \
               labels={"value":"profit"},height=400, width=600, template="plotly_white") 
fig.update_layout(legend=dict( orientation="h",
    yanchor="bottom", y=1.02,
    xanchor="right", x=1))
st.plotly_chart(fig)

# 圖: Delta Hedging 不同頻率的現貨持有量
df_spot = pd.DataFrame()
df_spot["t"] = df_delta["t"]
df_spot["Delta1"] = df_delta["Holding_shares"]
df_spot["Delta2"] = df_delta2["Holding_shares"]
df_spot["Delta5"] = df_delta5["Holding_shares"]
df_spot["Delta10"] = df_delta10["Holding_shares"]
df_spot["Delta20"] = df_delta20["Holding_shares"]
fig = px.line(df_spot, x="t", y=cname[1:] , title="Delta Hedging 不同頻率的現貨持有量", \
               labels={"x":"t","value":"Holding_shares"},height=400, width=600, template="plotly_white",)
fig.update_layout(legend=dict( orientation="h",
    yanchor="bottom", y=1.02,
    xanchor="right", x=1))
st.plotly_chart(fig)


st.dataframe(df_delta)
