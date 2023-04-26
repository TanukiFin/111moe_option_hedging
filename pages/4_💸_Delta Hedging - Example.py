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
    page_title="Delta Hedging - Example",
    page_icon="📈",
    layout="wide",
)

S0 = 49
quantity = 100 # brokerage sales quantity ex. 100=賣100個

st.header("Delta Hedging - Example")
st.markdown("券商賣100個單位的選擇權，參數如下")
st.markdown("**S0 =** $49")
c1, c2 = st.columns(2, gap="large")
with c1:
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

    if CP_A=="Short Call": st.metric(label="option value at t=0", value=round(bsmodel.call(S0,K_A,r,sigma,T).price,2))
    if CP_A=="Short Put": st.metric(label="option value at t=0", value=round(bsmodel.put(S0,K_A,r,sigma,T).price,2))

K_B=50 ; K_C=50
CP_B="Call" ; CP_C="Call" 


# 側邊
with st.sidebar:
    St_sce = st.sidebar.selectbox(
    "**股價情境**",
    ("大漲","小漲","持平","小跌","大跌","17.2","17.3"),  )#label_visibility ="collapsed"
    st.markdown("此頁的股價情境皆為預設數值，沒有任何隨機參數，詳見附件EXCEL[Delta避險_Excel練習題目.xlsx]中的[股價五情境]表格，或參考[此頁面](https://github.com/TanukiFin/option_pricing_2023/blob/main/stock%20price.csv)")

df_St=bsmodel.get_default_St(St_sce, r=r, sigma=sigma, T=T)
df_price = bsmodel.get_greeks(df_St, K_list=[K_A,K_B,K_C], CP=[CP_A, CP_B, CP_C], r=r, sigma=sigma, T=T)   

# 股價 & Greek Letters圖 ==================================================================================
c1, c2 = st.columns(2, gap="large")
with c1:
    tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
    fig = px.line(df_price.round(2), x="t", y="St", title="Stock Price: "+St_sce, height=300, template="plotly_white").update_layout(showlegend=False)
    tab1.plotly_chart(fig, use_container_width=True)
    tab2.write(df_price[["t","St"]].round(2),axis=1)

with c2:
    tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
    fig = px.line(df_price.round(2), x="t", y="A_Price", title=CP_A[6:10]+" Option Price", height=300, template="plotly_white").update_layout(showlegend=False)
    tab1.plotly_chart(fig, use_container_width=True)
    tab2.write(df_price[["t","A_Price"]].round(2).rename({"A_Price":"Option Price"},axis=1))


st.markdown("---")
# 損益圖 ==================================================================================
# get_delta_hedge(df_price, r=0.05, sigma=0.3, T=1, sell_price=3)
df_delta = bsmodel.get_delta_hedge(df_price, r, sigma, T, sell_price)
df_delta2 = bsmodel.get_delta_hedge_2week(df_price, freq=2, r=r, sigma=sigma, T=T, sell_price=sell_price)
df_delta5 = bsmodel.get_delta_hedge_2week(df_price, freq=5, r=r, sigma=sigma, T=T, sell_price=sell_price)
df_delta10 = bsmodel.get_delta_hedge_2week(df_price, freq=10, r=r, sigma=sigma, T=T, sell_price=sell_price)
df_delta20 = bsmodel.get_delta_hedge_2week(df_price, freq=20, r=r, sigma=sigma, T=T, sell_price=sell_price)

df_all_hedge = pd.DataFrame()
df_all_hedge["t"] = df_delta["t"]
df_all_hedge["No Hedging"] = df_delta["Option_Profit"]
df_all_hedge["Delta1"] = df_delta["Total_Profit"]
df_all_hedge["Delta2"] = df_delta2["Total_Profit"]
df_all_hedge["Delta5"] = df_delta5["Total_Profit"]
df_all_hedge["Delta10"] = df_delta10["Total_Profit"]
df_all_hedge["Delta20"] = df_delta20["Total_Profit"]




c1, c2 = st.columns([2,1], gap="large")
with c2:
    st.markdown("Variable顯示")
    hedge_list = []
    cname = ["No Hedging","Delta1","Delta5","Delta20"]
    cname2 = [" : 不避險的損益"," : 每期避險"," : 每五期避險(week0,week5,week10...)"," : 僅第一期避險"]
    for count in range(len(cname)):
        if st.checkbox(cname[count]+cname2[count],value=True):
            hedge_list.append(cname[count])
    #clist = st.columns(len(cname))
    #for count in range(len(clist)):
    #    with clist[count]: 
    #        if st.checkbox(cname[count],value=True):
    #            hedge_list.append(cname[count])
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
with c1:
    st.plotly_chart(fig, use_container_width=True)

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
#st.plotly_chart(fig)

st.info(f"""目前參數:　　:red[S0]={S0},　　:red[K]={K_A},　　:red[r]={r},　　:red[T]={round(T,2)},　　:red[sigma]={sigma} 
        \n 　　　　　　:red[type]={CP_A},　　:red[sell price]={sell_price}""")

# 圖: Delta Hedging 各部位損益
fig = px.line(df_delta.round(2), x="t", y=["Option_Profit","HedgingStock_Profit","Total_Profit"], title="Delta Hedging 各部位損益(每期避險)", \
               labels={"value":"profit"},height=400, width=600, template="plotly_white") 
fig.update_layout(legend=dict( orientation="h",
    yanchor="bottom", y=1.02,
    xanchor="right", x=1))
#st.plotly_chart(fig)

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
#st.plotly_chart(fig)

# 各類避險的表格


if CP_A == "Short Call":
    if df_price["St"].iloc[-1] > K_A: # Call履約
        cost = df_delta["Cumulative_cost_including_interest"].iloc[-1] - K_A*quantity
        cost5 = df_delta5["Cumulative_cost_including_interest"].iloc[-1] - K_A*quantity
        cost20 = df_delta20["Cumulative_cost_including_interest"].iloc[-1] - K_A*quantity
    elif df_price["St"].iloc[-1] < K_A: # Call不履約
        cost = df_delta["Cumulative_cost_including_interest"].iloc[-1]
        cost5 = df_delta5["Cumulative_cost_including_interest"].iloc[-1]
        cost20 = df_delta20["Cumulative_cost_including_interest"].iloc[-1]
elif CP_A == "Short Put":
    if df_price["St"].iloc[-1] < K_A: # Put履約
        cost = df_delta["Cumulative_cost_including_interest"].iloc[-1]
        cost5 = df_delta5["Cumulative_cost_including_interest"].iloc[-1] - K_A*quantity
        cost20 = df_delta20["Cumulative_cost_including_interest"].iloc[-1] - K_A*quantity
    elif df_price["St"].iloc[-1] > K_A: # Put不履約
        cost = df_delta["Cumulative_cost_including_interest"].iloc[-1]
        cost5 = df_delta5["Cumulative_cost_including_interest"].iloc[-1]
        cost20 = df_delta20["Cumulative_cost_including_interest"].iloc[-1]

st.dataframe(df_price[["t","St","A_Price","A_Delta","A_Gamma","A_Vega","A_Theta"]])

st.markdown(f"""**每期避險** 避險成本={round(cost,2)}""")
st.dataframe(df_delta)
st.markdown(f"""**每5期避險** 避險成本={round(cost5,2)}""")
st.dataframe(df_delta5)
st.markdown(f"""**靜態避險(僅第一期避險)** 避險成本={round(cost20,2)}""")
st.dataframe(df_delta20)