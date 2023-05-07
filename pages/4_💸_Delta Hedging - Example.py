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
    page_icon="💸",
    layout="wide",
)

S0 = 49
quantity = 100 # brokerage sales quantity ex. 100=賣100個

#%% === A區: Input 區 ===
st.header("Delta Hedging - Example")
st.markdown("券商賣100張權證，參數如下")
st.markdown("**S0 =** $49")
c1, c2 = st.columns(2, gap="large")
with c1:
    K_A = st.number_input("**K =**",min_value=40,max_value=60,value=50, help="履約價")
    r = st.number_input("**r =**",min_value=0.0,max_value=0.1,value=0.05)
    sigma = st.number_input("**sigma =**",min_value=0.1,max_value=0.5,value=0.2)
    T = st.selectbox(
    "**T**",
    ( round(20/52,4), 1) )
    
with c2:
    CP_A = st.selectbox(
    """**Type =**""",
    ("Short Call","Short Put"), help="券商要賣Call還是賣Put" )
    sell_price = st.number_input("""**Sell Price =**""",min_value=1,max_value=20,value=3, help="券商賣這個選擇權的售價，應高於理論價值(相當於成本)，這樣才有利潤")

    if CP_A=="Short Call": st.metric(label="option value at t=0", value=round(bsmodel.call(S0,K_A,r,sigma,T).price,2))
    if CP_A=="Short Put": st.metric(label="option value at t=0", value=round(bsmodel.put(S0,K_A,r,sigma,T).price,2))

K_B=48 ; K_C=50
CP_B="Call" ; CP_C="Call" 

#%% === 側邊區 ===
with st.sidebar:
    St_sce = st.sidebar.selectbox(
    "**股價情境**",
    ("大漲","小漲","持平","小跌","大跌","17.2","17.3"),  )#label_visibility ="collapsed"
    st.markdown("此頁的股價情境皆為預設數值，沒有任何隨機參數，詳見附件EXCEL[Delta避險_Excel練習題目.xlsx]中的[股價五情境]表格，或參考[此頁面](https://github.com/TanukiFin/option_pricing_2023/blob/main/stock%20price.csv)")

df_St = bsmodel.get_default_St(St_sce, r=r, sigma=sigma, T=T)
df_price = bsmodel.get_greeks(df_St, K_list=[K_A,K_B,K_C], CP=[CP_A, CP_B, CP_C], r=r, sigma=sigma, T=T)   

#%% === B區: 股價 & 權證價圖 ===
st.info(f"""目前參數:　　:red[S0]={S0},　　:red[K]={K_A},　　:red[r]={r},　　:red[T]={round(T,2)},　　:red[sigma]={sigma} 
        \n 　　　　　　:red[type]={CP_A},　　:red[sell price]={sell_price},　　:red[情境]={St_sce}""")

c1, c2 = st.columns(2, gap="large")
with c1:
    tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
    df_price["K"] = K_A
    fig = px.line(df_price.round(2), x="t", y=["St", "K"], title="Stock Price: "+St_sce, height=300, template="plotly_white")
    fig.update_layout(legend=dict( orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    tab1.plotly_chart(fig, use_container_width=True)
    tab2.write(df_price[["t","St"]].round(2),axis=1)

with c2:
    tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
    fig = px.line(df_price.round(2), x="t", y="A_Price", title=CP_A[6:10]+" Option Price", height=300, template="plotly_white").update_layout(showlegend=False)
    tab1.plotly_chart(fig, use_container_width=True)
    tab2.write(df_price[["t","A_Price"]].round(2).rename({"A_Price":"Option Price"},axis=1))

#%% === C區: Greeks圖 ===
tab1, tab2 = st.tabs(["📈 Greeks","🗃 Data"])
c1, c2 = tab1.columns(2)
fig = px.line(df_price.round(2), x="t", y="A_Delta", title="Delta", height=300, template="plotly_white").update_layout(showlegend=False)
c1.plotly_chart(fig, use_container_width=True)
fig = px.line(df_price.round(2), x="t", y="A_Gamma", title="Gamma", height=300, template="plotly_white").update_layout(showlegend=False)
c2.plotly_chart(fig, use_container_width=True)
tab2.dataframe(df_price[["t","St","A_Price","A_Delta","A_Gamma","B_Price","B_Delta","B_Gamma" ]])
#%% === D區: 損益圖Delta避險 ===
df_delta = bsmodel.get_delta_hedge(df_price, r, sigma, T, sell_price)
df_delta2 = bsmodel.get_delta_hedge_2week(df_price, freq=2, r=r, sigma=sigma, T=T, sell_price=sell_price)
df_delta5 = bsmodel.get_delta_hedge_2week(df_price, freq=5, r=r, sigma=sigma, T=T, sell_price=sell_price)
df_delta10 = bsmodel.get_delta_hedge_2week(df_price, freq=10, r=r, sigma=sigma, T=T, sell_price=sell_price)
df_delta20 = bsmodel.get_delta_hedge_2week(df_price, freq=20, r=r, sigma=sigma, T=T, sell_price=sell_price)
df_all_hedge = pd.DataFrame()
df_all_hedge["t"] = df_delta["t"]
df_all_hedge = pd.concat([df_all_hedge,df_delta["A部位損益"],df_delta["總損益"],df_delta2["總損益"],
                          df_delta5["總損益"],df_delta10["總損益"],df_delta20["總損益"]], axis=1)
df_all_hedge.columns = ["t","No Hedging","Delta1","Delta2","Delta5","Delta10","Delta20"]

tab1, tab2, tab3, tab4 = st.tabs(["📈 不同頻率避險損益","🗃 每期避險", "🗃 每5期避險", "🗃 靜態避險"])
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
fig = px.line(df_all_hedge.round(2), x="t", y=hedge_list, title="Delta Hedging避險損益", \
               labels={"value":"profit"},height=400, width=600, template="plotly_white") 
fig.update_layout(legend=dict( orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
c1.plotly_chart(fig, use_container_width=True)

# D-2~5 每種頻率避險方式的表格
if CP_A == "Short Call":
    if df_price["St"].iloc[-1] > K_A: # Call履約
        cost = df_delta["現貨累積成本"].iloc[-1] - K_A*quantity
        cost5 = df_delta5["現貨累積成本"].iloc[-1] - K_A*quantity
        cost20 = df_delta20["現貨累積成本"].iloc[-1] - K_A*quantity
    elif df_price["St"].iloc[-1] < K_A: # Call不履約
        cost = df_delta["現貨累積成本"].iloc[-1]
        cost5 = df_delta5["現貨累積成本"].iloc[-1]
        cost20 = df_delta20["現貨累積成本"].iloc[-1]
elif CP_A == "Short Put":
    if df_price["St"].iloc[-1] < K_A: # Put履約
        cost = df_delta["現貨累積成本"].iloc[-1]
        cost5 = df_delta5["現貨累積成本"].iloc[-1] - K_A*quantity
        cost20 = df_delta20["現貨累積成本"].iloc[-1] - K_A*quantity
    elif df_price["St"].iloc[-1] > K_A: # Put不履約
        cost = df_delta["現貨累積成本"].iloc[-1]
        cost5 = df_delta5["現貨累積成本"].iloc[-1]
        cost20 = df_delta20["現貨累積成本"].iloc[-1]

tab2.markdown(f"""避險成本={round(cost,2)}""")
tab2.dataframe(df_delta)
tab3.markdown(f"""避險成本={round(cost5,2)}""")
tab3.dataframe(df_delta5)
tab4.markdown(f"""避險成本={round(cost20,2)}""")
tab4.dataframe(df_delta20)






#%% === D區: 損益圖Delta-Gamma避險 ===
df_gamma = bsmodel.get_gamma_hedge(df_price, r, sigma, T, sell_price)
cname = ["No Hedging","Delta Hedging","Delta-Gamma Hedging"]
df_all_hedge = pd.DataFrame()
df_all_hedge["t"] = df_delta["t"]
df_all_hedge = pd.concat([df_all_hedge,df_delta["A部位損益"],df_delta["總損益"],df_gamma["總損益"]], axis=1)
df_all_hedge.columns = ["t"]+cname

fig1 = px.line(df_all_hedge.round(2), x="t", y=cname, title="Delta-Gamma避險損益", \
               labels={"value":"profit"},height=400, width=700, template="plotly_white")
fig2 = px.line(df_gamma.round(2), x="t", y=["A部位損益","B部位損益","現貨部位損益","總損益"], title="Delta-Gamma Hedging", \
               labels={"value":"profit"},height=400, width=700, template="plotly_white") 
tab1, tab2, tab3 = st.tabs(["📈 Delta-Gamma避險損益", "📈 各部位損益","🗃 Data"])
tab1.plotly_chart(fig1)
tab2.plotly_chart(fig2)
tab3.dataframe(df_gamma)