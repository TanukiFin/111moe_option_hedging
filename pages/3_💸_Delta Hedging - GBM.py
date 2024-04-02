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
from myfunction import hedging
import warnings
warnings.filterwarnings("ignore")

# === 預設參數 ===
st.set_page_config(
    page_title="選擇權避險操作模組",
    page_icon="💸",
    layout="wide",
)
st.header("Delta Hedging - GBM")
S0 = 50 # initial stock price
quantity = 100 # brokerage sales quantity ex. 100=賣100個

# === 打開網頁時，隨機跑一個股價 ===
if 'openweb' not in st.session_state:
    st.session_state.openweb = True
    df_St = bsmodel.get_GBM_St()
    st.session_state.df_St = df_St
    print("=== START ===")

#%% === 側邊區 ===
with st.sidebar:
    st.markdown("**GBM模擬股價的參數**")
    steps_input = st.number_input("**steps =**", min_value=10,max_value=70,value=20)
    r_input = st.number_input("**r =**",min_value=0.0,max_value=0.1,value=0.05)
    sigma_input = st.number_input("**sigma =**", min_value=0.1,max_value=1.0,value=0.3)
    T_input = st.number_input("**T =**",min_value=0.1,max_value=2.0,value=1.0)
    # 按Simulate St 股價才會變動
    if st.button("Simulate St"):
        df_St = bsmodel.get_GBM_St(steps=steps_input, r=r_input, sigma=sigma_input, T=T_input)
        st.session_state.df_St = df_St # 暫存df
    st.markdown("此頁的股價產生方式為根據GBM隨機產生，每次點選網頁左側的[Simulate St]按鈕，即會根據所選參數產生新的隨機股價。")

#%% === A區: Input 區 ===
st.markdown("券商賣100張權證，參數可調整的僅有履約價(K)、Type、Sell Price，其餘皆跟隨網頁左側的GBM參數。")
st.markdown("**S0 =** $50")
c1, c2 = st.columns(2, gap="large")
with c1:
    K_A = st.number_input("**K =**",min_value=40,max_value=60,value=50)
with c2:
    CP_A = st.selectbox(
    "Type: 券商要賣Call還是賣Put",
    ("Short Call","Short Put") )
    sell_price = st.number_input("Sell Price: 券商賣這個選擇權的售價，應高於理論價值(相當於成本)，這樣才有利潤",min_value=1,max_value=20,value=8)
    if CP_A=="Short Call": st.metric(label="option value at t=0", value=round(bsmodel.call(S0,K_A,r_input,sigma_input,T_input).price,2))
    if CP_A=="Short Put": st.metric(label="option value at t=0", value=round(bsmodel.put(S0,K_A,r_input,sigma_input,T_input).price,2))
    
K_B=50 ; K_C=50
CP_B="Call" ; CP_C="Call" 

df_price = bsmodel.get_greeks(st.session_state.df_St, K_list=[K_A,K_B,K_C], CP = [CP_A, CP_B, CP_C])   

#%% === B區: 股價 & 權證價圖 ===
st.subheader("股價與選擇權價格")
st.info(f"""目前參數:　　:red[S0]={S0},　　:red[K]={K_A},　　:red[r]={r_input},　　:red[T]={round(T_input,2)},　　:red[sigma]={sigma_input} 
        \n 　　　　　　:red[type]={CP_A},　　:red[sell price]={sell_price}""")

c1, c2 = st.columns(2, gap="large")
with c1:
    tab1, tab2 = st.tabs(["📈 Chart", "📚 Data"])
    fig = px.line(df_price.round(2), x="t", y="St", title="Stock Price", height=300, template="plotly_white").update_layout(showlegend=False)
    tab1.plotly_chart(fig, use_container_width=True)
    tab2.write(df_price[["t","St"]].round(2),axis=1)

with c2:
    tab1, tab2 = st.tabs(["📈 Chart", "📚 Data"])
    fig = px.line(df_price.round(2), x="t", y="A_Price", title=CP_A[6:10]+" Option Price", height=300, template="plotly_white").update_layout(showlegend=False)
    tab1.plotly_chart(fig, use_container_width=True)
    tab2.write(df_price[["t","A_Price"]].round(2).rename({"A_Price":"Option Price"},axis=1))

#%% === C區: Greeks圖 ===
st.subheader("Delta與Gamma圖")
tab1, tab2 = st.tabs(["📈 Greeks","📚 Data"])
c1, c2 = tab1.columns(2)
fig = px.line(df_price.round(2), x="t", y="A_Delta", title="Delta", height=300, template="plotly_white").update_layout(showlegend=False)
c1.plotly_chart(fig, use_container_width=True)
fig = px.line(df_price.round(2), x="t", y="A_Gamma", title="Gamma", height=300, template="plotly_white").update_layout(showlegend=False)
c2.plotly_chart(fig, use_container_width=True)
tab2.dataframe(df_price[["t","St","A_Price","A_Delta","A_Gamma","B_Price","B_Delta","B_Gamma" ]])

#%% === D區: Delta避險損益圖 ===
st.subheader("Delta避險損益圖")
df_delta = hedging.get_delta_hedge(df_price, r_input, sigma_input, T_input, sell_price)
df_delta2 = hedging.get_delta_hedge_2week(df_price, freq=2, r=r_input, sigma=sigma_input, T=T_input, sell_price=sell_price)
df_delta5 = hedging.get_delta_hedge_2week(df_price, freq=5, r=r_input, sigma=sigma_input, T=T_input, sell_price=sell_price)
df_delta10 = hedging.get_delta_hedge_2week(df_price, freq=10, r=r_input, sigma=sigma_input, T=T_input, sell_price=sell_price)
df_delta20 = hedging.get_delta_hedge_2week(df_price, freq=20, r=r_input, sigma=sigma_input, T=T_input, sell_price=sell_price)

df_all_hedge = df_delta[["t"]]
df_all_hedge = pd.concat([df_all_hedge,df_delta["A部位損益"],df_delta["總損益"],df_delta2["總損益"],
                          df_delta5["總損益"],df_delta10["總損益"],df_delta20["總損益"]], axis=1)
df_all_hedge.columns = ["t","No Hedging","Delta1","Delta2","Delta5","Delta10","Delta20"]


tab1, tab2, tab3, tab4, tab5= st.tabs(["📈 不同頻率避險損益","📚 Delta1 每期避險","📚 Delta2 每2期避險", "📚 Delta5 每5期避險", "📚 Delta20 靜態避險"])
# D-tab1
c1, c2 = tab1.columns([2,1], gap="large")
with c2:
    st.markdown("避險方式")
    hedge_list = []
    cname = [["No Hedging"   , "Delta1"    , "Delta2"      , "Delta5"      , "Delta20"    ],
            ["不避險的損益", "每期避險", "每二期避險", "每五期避險(week0,week5,week10,week15)", "靜態避險(僅第一期避險)"]]
    for count in range(len(cname[0])):
        if st.checkbox(cname[0][count], value=True, help=cname[1][count]):
            hedge_list.append(cname[0][count])
fig = px.line(df_all_hedge.round(2), x="t", y=hedge_list, title="Delta避險損益", \
               labels={"value":"profit","variable":"避險方式"},height=400, width=600, template="plotly_white") 
fig.update_layout(legend=dict( orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
c1.plotly_chart(fig, use_container_width=True)

# D-2~5 每種頻率避險方式的表格
if CP_A == "Short Call":
    if df_price["St"].iloc[-1] > K_A: # Call履約
        cost = df_delta["現貨累積成本"].iloc[-1] - K_A*quantity
        cost2 = df_delta2["現貨累積成本"].iloc[-1] - K_A*quantity
        cost5 = df_delta5["現貨累積成本"].iloc[-1] - K_A*quantity
        cost20 = df_delta20["現貨累積成本"].iloc[-1] - K_A*quantity
    elif df_price["St"].iloc[-1] < K_A: # Call不履約
        cost = df_delta["現貨累積成本"].iloc[-1]
        cost2 = df_delta2["現貨累積成本"].iloc[-1]
        cost5 = df_delta5["現貨累積成本"].iloc[-1]
        cost20 = df_delta20["現貨累積成本"].iloc[-1]
elif CP_A == "Short Put":
    if df_price["St"].iloc[-1] < K_A: # Put履約
        cost = df_delta["現貨累積成本"].iloc[-1] - K_A*quantity
        cost2 = df_delta2["現貨累積成本"].iloc[-1] - K_A*quantity
        cost5 = df_delta5["現貨累積成本"].iloc[-1] - K_A*quantity
        cost20 = df_delta20["現貨累積成本"].iloc[-1] - K_A*quantity
    elif df_price["St"].iloc[-1] > K_A: # Put不履約
        cost = df_delta["現貨累積成本"].iloc[-1]
        cost2 = df_delta2["現貨累積成本"].iloc[-1]
        cost5 = df_delta5["現貨累積成本"].iloc[-1]
        cost20 = df_delta20["現貨累積成本"].iloc[-1]

tab2.markdown(f"""避險成本={round(cost,2)}""")
tab2.dataframe(df_delta)
tab3.markdown(f"""避險成本={round(cost2,2)}""")
tab3.dataframe(df_delta2)
tab4.markdown(f"""避險成本={round(cost5,2)}""")
tab4.dataframe(df_delta5)
tab5.markdown(f"""避險成本={round(cost20,2)}""")
tab5.dataframe(df_delta20)



#%% === E區: Delta避險進階探討 ===
st.subheader("Delta避險進階探討")
tab1, tab2, tab3 = st.tabs(["📚 Delta與現貨應持有量的關係", "📚 各部位損益","📚 不同頻率的現貨持有量"])
# E-tab圖1: Delta與現貨應持有量的關係

delta_sce = tab1.selectbox( """選擇不同頻率避險方式1""", cname[0][1:] ) #,label_visibility ="collapsed"
delta_df_list = {"Delta1": df_delta, "Delta2": df_delta2, "Delta5": df_delta5, "Delta20":df_delta20}

df = delta_df_list[delta_sce]

df_spot = pd.DataFrame()
df_spot["t"] = df["t"]
df_spot["A部位Delta"] = df_price["A_總Delta"]
df_spot["避險部位_現貨持有量"] = df["現貨持有量"]
df_spot["Portfolio_Delta"] = round(df_price["A_總Delta"]+df["現貨持有量"],2)
fig = px.line(df_spot, x="t", y=["A部位Delta","避險部位_現貨持有量","Portfolio_Delta"], title=f"{delta_sce}: Delta與現貨應持有量的關係", \
               labels={"x":"t"},height=400, width=600, template="plotly_white",)
fig.update_layout(legend=dict( orientation="h",
    yanchor="bottom", y=1.02,
    xanchor="right", x=1))
tab1.plotly_chart(fig)


# E-tab圖2: Delta Hedging 各部位損益
delta_sce = tab2.selectbox( """選擇不同頻率避險方式2""", cname[0][1:] ) #,label_visibility ="collapsed"
delta_df_list = {"Delta1": df_delta, "Delta2": df_delta2, "Delta5": df_delta5, "Delta20":df_delta20}
fig = px.line(delta_df_list[delta_sce].round(2), x="t", y=["A部位損益","現貨部位損益","總損益"], title=f"{delta_sce}: 避險各部位損益", \
               labels={"value":"profit"},height=400, width=700, template="plotly_white") 
tab2.plotly_chart(fig)

# E-tab圖3: Delta Hedging 不同頻率的現貨持有量
df_spot = pd.DataFrame()
df_spot["t"] = df_delta["t"]
df_spot = pd.concat([df_spot,df_delta["現貨持有量"],df_delta2["現貨持有量"],df_delta5["現貨持有量"],df_delta10["現貨持有量"],df_delta20["現貨持有量"]], axis=1)
df_spot.columns = ["t","Delta1","Delta2","Delta5","Delta10","Delta20"]

fig = px.line(df_spot, x="t", y=cname[0][1:] , title="不同頻率的現貨持有量", \
               labels={"x":"t","value":"現貨持有量"},height=400, width=600, template="plotly_white",)
fig.update_layout(legend=dict( orientation="h",
    yanchor="bottom", y=1.02,
    xanchor="right", x=1))
tab3.plotly_chart(fig)

