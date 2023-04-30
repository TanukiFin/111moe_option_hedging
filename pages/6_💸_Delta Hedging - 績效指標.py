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
    page_title="Delta Hedging - 績效指標",
    page_icon="📈",
    layout="wide",
)

S0 = 50 # initial stock price
quantity = 100 # brokerage sales quantity ex. 100=賣100個

# 打開網頁時，隨機跑一個股價 ==============================================================================
if 'openweb' not in st.session_state:
    st.session_state.openweb = True
    df_St = bsmodel.get_GBM_St()
    st.session_state.df_St = df_St
    print("=== START ===")

# 側邊 sidebar ==============================================================================
with st.sidebar:
    st.markdown("**GBM模型模擬股價的參數**")
    steps_input = st.number_input("**steps =**", min_value=10,max_value=70,value=20)
    numberOfSims = st.number_input("**number of sims =**", min_value=10,max_value=1000,value=50)
    r_input = st.number_input("**r =**",min_value=0.0,max_value=0.1,value=0.05)
    sigma_input = st.number_input("**sigma =**", min_value=0.1,max_value=1.0,value=0.3)
    T_input = st.number_input("**T =**",min_value=0.1,max_value=2.0,value=1.0)
    # 按Simulate St 股價才會變動
    if st.button("Simulate St"):
        df_St = bsmodel.get_GBM_St(steps=steps_input, r=r_input, sigma=sigma_input, T=T_input)
        st.session_state.df_St = df_St # 暫存df
    st.markdown("此頁的股價產生方式為根據GBM模型隨機產生，每次點選網頁左側的[Simulate St]按鈕，即會根據所選參數產生新的隨機股價。")

# ==============================================================================


st.header("Delta Hedging - 績效指標")
st.markdown("券商賣100個單位的選擇權，參數可調整的僅有履約價(K)、Type、Sell Price，其餘皆跟隨網頁左側的GBM模型參數。")
st.markdown("**S0 =** $50")
c1, c2 = st.columns(2, gap="large")
with c1:
    K_A = st.number_input("**K =**",min_value=40,max_value=60,value=50)
with c2:
    CP_A = st.selectbox(
    "Type: 券商要賣Call還是賣Put",
    ("Short Call","Short Put") )
    sell_price = st.number_input("Sell Price: 券商賣這個選擇權的售價，應高於理論價值(相當於成本)，這樣才有利潤",min_value=1,max_value=20,value=8)
    if CP_A=="Short Call": option_value=round(bsmodel.call(S0,K_A,r_input,sigma_input,T_input).price,2)
    if CP_A=="Short Put": option_value=round(bsmodel.put(S0,K_A,r_input,sigma_input,T_input).price,2)
    st.metric(label="option value at t=0", value=option_value)
    
K_B=48 ; K_C=51
CP_B="Call" ; CP_C="Call" 

st.info(f"""目前參數:　　:red[S0]={S0},　　:red[K]={K_A},　　:red[r]={r_input},　　:red[T]={round(T_input,2)},　　:red[sigma]={sigma_input} 
        \n 　　　　　　:red[type]={CP_A},　　:red[sell price]={sell_price}""")


df_price = bsmodel.get_greeks(st.session_state.df_St, K_list=[K_A,K_B,K_C], CP = [CP_A, CP_B, CP_C])   

c1, c2 = st.columns(2, gap="large")
with c1:
    st.image("table19.4.png")
with c2:
    st.markdown("""
    Table 19.4 shows statistics on the performance of delta hedging obtained from one million random stock price paths in our example. 
    The performance measure is calculated, similarly to Table 19.1, as the ratio of the standard deviation of the cost of hedging the 
    option to the Black–Scholes–Merton price of the option. It is clear that delta hedging is a great improvement over a stop-loss strategy. 
    Unlike a stop-loss strategy, the performance of delta-hedging gets steadily better as the hedge is monitored more frequently.""")
    st.latex(r"""
    避險成本績效指標= \frac{SD \space of \space cost}{Option \space Value}
    """)
    st.latex(r"""
    損益績效指標= \frac{SD \space of \space profit}{Option \space Value}
    """)
    st.markdown("""<center>越小越好</center>""",unsafe_allow_html=True)
# 模擬100次
df_nohedge_monte = pd.DataFrame()
df_delta_monte = pd.DataFrame()
df_delta20_monte = pd.DataFrame()
df_gamma_monte = pd.DataFrame()
all_delta_cost, all_delta20_cost, all_gamma_cost = [], [], []

progress_text = "蒙特卡羅模擬正在進行中，請稍候..."
my_bar = st.progress(0, text=progress_text)
for i in range(numberOfSims):
    my_bar.progress((i + 1)/numberOfSims, text=progress_text)
    df_St = bsmodel.get_GBM_St(steps=steps_input, r=r_input, sigma=sigma_input, T=T_input)
    df_price = bsmodel.get_greeks(df_St, K_list=[K_A,K_B,K_C], CP = [CP_A, CP_B, CP_C])  
    df_delta = bsmodel.get_delta_hedge(df_price, r_input, sigma_input, T_input, sell_price)
    df_delta20 = bsmodel.get_delta_hedge_2week(df_price, freq=20, r=r_input, sigma=sigma_input, T=T_input, sell_price=sell_price) 
    df_gamma =  bsmodel.get_gamma_hedge(df_price, r_input, sigma_input, T_input, sell_price)

    df_nohedge_monte = pd.concat([df_nohedge_monte, df_delta["Option_Profit"]], axis=1).reset_index(drop=True)
    df_delta_monte = pd.concat([df_delta_monte, df_delta["Total_Profit"]], axis=1).reset_index(drop=True)
    df_delta20_monte = pd.concat([df_delta20_monte, df_delta20["Total_Profit"]], axis=1).reset_index(drop=True)
    df_gamma_monte = pd.concat([df_gamma_monte, df_gamma["Total_Profit"]], axis=1).reset_index(drop=True)

    if df_price["St"].loc[20] <= K_A: # 不履約 = [ 最後一期的累積成本 ] exp(-r*T)
        delta_cost = df_delta["Cumulative_cost_including_interest"].loc[20] *  exp(-r_input*T_input)
        delta20_cost = df_delta20["Cumulative_cost_including_interest"].loc[20] *  exp(-r_input*T_input)
        gamma_cost = df_gamma["B部位_累積成本"].loc[20] + df_gamma["Cumulative_cost_including_interest"].loc[20] 
    elif df_price["St"].loc[20] > K_A:  # 有履約 = [ 最後一期的累積成本-投資人履約付的錢(K*n) ] exp(-r*T)
        delta_cost = (df_delta["Cumulative_cost_including_interest"].loc[20] - K_A*quantity)*  exp(-r_input*T_input)
        delta20_cost = (df_delta20["Cumulative_cost_including_interest"].loc[20] - K_A*quantity)*  exp(-r_input*T_input)
        gamma_cost = ( df_gamma["B部位_累積成本"].loc[20] + df_gamma["Cumulative_cost_including_interest"].loc[20] ) - K_A*quantity
    if df_price["St"].loc[20] > K_B: 
        gamma_cost = gamma_cost + K_B*df_gamma["B部位_持有量"].loc[20]
    gamma_cost = gamma_cost * exp(-r_input*T_input)


    all_delta_cost.append(delta_cost)
    all_delta20_cost.append(delta20_cost)
    all_gamma_cost.append(gamma_cost)

my_bar.empty()   

df_nohedge_monte.columns=np.arange(0,len(df_nohedge_monte.columns))
df_delta_monte.columns=np.arange(0,len(df_delta_monte.columns))
df_delta20_monte.columns=np.arange(0,len(df_delta20_monte.columns))
df_gamma_monte.columns=np.arange(0,len(df_gamma_monte.columns))



st.header("蒙地卡羅模擬所有路徑")
# 圖1: 不避險
tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data-損益"])
c1, c2, c3 = tab1.columns([3,3,2], gap="medium")
with c1:
    fig = px.line(df_nohedge_monte, title="不避險損益", \
               labels={"index":"t", "value":"profit", "variable":"路徑"}, height=400, template="plotly_white").update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
with c2:
    fig = px.histogram(y=df_nohedge_monte.loc[20], title="不避險 期末避險損益分布圖", \
               labels={"value":"profit at t=T"}, nbins=40, height=400, template="plotly_white").update_layout(showlegend=False)

    st.plotly_chart(fig, use_container_width=True)
with c3:
    st.metric(label="避險成本的績效指標: SD of cost / Option Value", value="-")
    st.metric(label="避險成本的平均: average(cost)", value="-")
    st.markdown("---")
    st.metric(label="避險損益的績效指標: SD of profit / Option Value", value=round(df_nohedge_monte.loc[20].std()/option_value,4))
    st.metric(label="避險損益的平均: average(cost)", value=round(df_delta20_monte.loc[20].mean(),4))
tab2.markdown("columns=路徑, index=t")
tab2.dataframe(df_nohedge_monte)

# 圖2: delta 1
tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data-損益"])
c1, c2, c3= tab1.columns([3,3,2], gap="medium")
with c1:
    fig = px.line(df_delta_monte, title="Delta1 每期避險損益", \
               labels={"index":"t", "value":"profit", "variable":"路徑"}, height=400, template="plotly_white").update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
with c2:
    fig = px.histogram(y=df_delta_monte.loc[20], title="Delta1 期末避險損益分布圖", \
               labels={"value":"profit at t=T"}, nbins=40, height=400, template="plotly_white").update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
with c3:
    st.metric(label="避險成本的績效指標: SD of cost / Option Value", value=round(np.std(all_delta_cost)/option_value,4))
    st.metric(label="避險成本的平均: average(cost)", value=round(np.average(all_delta_cost),4))
    st.markdown("---")
    st.metric(label="避險損益的績效指標: SD of profit / Option Value", value=round(df_delta_monte.loc[20].std()/option_value,4))
    st.metric(label="避險損益的平均: average(cost)", value=round(df_delta_monte.loc[20].mean(),4))
tab2.markdown("columns=路徑, index=t")
tab2.dataframe(df_delta_monte)


# 圖3: delta 20
tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data-損益"])
c1, c2, c3 = tab1.columns([3,3,2], gap="medium")
with c1:
    fig = px.line(df_delta20_monte, title="Delta20 靜態避險損益", \
               labels={"index":"t", "value":"profit", "variable":"路徑"}, height=400, template="plotly_white").update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
with c2:
    fig = px.histogram(y=df_delta20_monte.loc[20], title="Delta20 期末避險損益分布圖", \
               labels={"value":"profit at t=T"}, nbins=40, height=400, template="plotly_white").update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
with c3:
    st.metric(label="避險成本的績效指標: SD of cost / Option Value", value=round(np.std(all_delta20_cost)/option_value,4))
    st.metric(label="避險成本的平均: average(cost)", value=round(np.average(all_delta20_cost),4))
    st.markdown("---")
    st.metric(label="避險損益的績效指標: SD of profit / Option Value", value=round(df_delta20_monte.loc[20].std()/option_value,4))
    st.metric(label="避險損益的平均: average(cost)", value=round(df_delta20_monte.loc[20].mean(),4))
tab2.markdown("columns=路徑, index=t")
tab2.dataframe(df_delta20_monte)

# 圖4: delta-gamma
tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data-損益"])
c1, c2, c3 = tab1.columns([3,3,2], gap="medium")
with c1:
    fig = px.line(df_gamma_monte, title="Delta-Gamma 避險損益", \
               labels={"index":"t", "value":"profit", "variable":"路徑"}, height=400, template="plotly_white").update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
with c2:
    fig = px.histogram(y=df_gamma_monte.loc[20], title="Delta-Gamma 期末避險損益分布圖", \
               labels={"value":"profit at t=T"}, nbins=40, height=400, template="plotly_white").update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
with c3:
    st.metric(label="避險成本的績效指標: SD of cost / Option Value", value=round(np.std(all_gamma_cost)/option_value,4))
    st.metric(label="避險成本的平均: average(cost)", value=round(np.average(all_gamma_cost),4))
    st.markdown("---")
    st.metric(label="避險損益的績效指標: SD of profit / Option Value", value=round(df_gamma_monte.loc[20].std()/option_value,4))
    st.metric(label="避險損益的平均: average(cost)", value=round(df_gamma_monte.loc[20].mean(),4))
tab2.markdown("columns=路徑, index=t")
tab2.dataframe(df_gamma_monte)

# 統整圖: 避險成本分布比較
st.markdown("---")
c1, c2 = st.columns([1,1], gap="medium")
df1 = pd.DataFrame([all_delta_cost, ["Delta1"]*len(all_delta_cost)], index=["避險成本", "避險方式"]).T
df2 = pd.DataFrame([all_delta20_cost, ["Delta20"]*len(all_delta20_cost)], index=["避險成本", "避險方式"]).T
df3 = pd.DataFrame([all_gamma_cost, ["Delta-Gamma"]*len(all_gamma_cost)], index=["避險成本", "避險方式"]).T
df_all_cost = pd.concat([df1, df2, df3], axis=0).reset_index(drop=True)
fig = px.histogram(df_all_cost, title="避險成本分布圖: Delta1、Delta20、Delta-Gamma", x="避險成本", color="避險方式", nbins=40, marginal="rug", # can be `box`, `violin`
                         hover_data=df_all_cost.columns)
with c1:
    st.plotly_chart(fig)

df1 = pd.concat( [ df_delta_monte.loc[20], pd.DataFrame( ["Delta1"]*len(all_delta_cost) ) ], axis=1 )
df2 = pd.concat( [ df_delta20_monte.loc[20], pd.DataFrame( ["Delta20"]*len(all_delta20_cost) ) ], axis=1 )
df3 = pd.concat( [ df_gamma_monte.loc[20], pd.DataFrame( ["Delta-Gamma"]*len(all_gamma_cost) ) ], axis=1 )
df4 = pd.concat( [ df_nohedge_monte.loc[20], pd.DataFrame( ["No Hedging"]*len(all_delta_cost) ) ], axis=1 )
df_all_profit = pd.concat([df1, df2, df3, df4], axis=0).reset_index(drop=True)
df_all_profit.columns=["最終損益", "避險方式"]
fig = px.histogram(df_all_profit, title="最終損益分布圖: Delta1、Delta20、Delta-Gamma、No Hedging ", x="最終損益", color="避險方式", nbins=60, marginal="rug", # can be `box`, `violin`
                         hover_data=df_all_profit.columns)
with c2:
    st.plotly_chart(fig)
