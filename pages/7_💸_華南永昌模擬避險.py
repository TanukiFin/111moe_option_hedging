import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
st.header("華南永昌模擬避險")


warrent  = pd.read_csv("data/權證日交易資料.csv")
warrent["日期"] = pd.to_datetime(warrent["日期"])
warrent["名稱"] = warrent["名稱"]+" "+warrent["履約價(元)"].apply(int).apply(str)
filt = warrent[ warrent["履約價(元)"].isin([10000]) & warrent["到期月份"].isin(["96","97","98"]) ]
names = filt.groupby("名稱").count().index

TXO  = pd.read_csv("data/TXO日交易資料.csv")
TXO_names = TXO.groupby("名稱").count().index


with st.sidebar:
    sigma_select = st.sidebar.selectbox( "**用於計算Greeks的波動率基礎**", ("台股指數的 HV","永昌權證的 IV","TXO9600的 IV","VIX"))
    st.text("施工中...")
    B_tool = st.sidebar.selectbox( "**避險工具TXO Put**", ("TXO202006P9600","TXO202006P9800","TXO202006P10000","TXO202006P12000"))
    K_B = TXO[TXO["代號"].isin([B_tool])]["履約價"].iloc[0]

c1, c2 = st.columns(2, gap="small")

# === HV、IV、VIX ===
TXOP9600  = pd.read_csv("data/TXO202006P9600.csv", index_col="Date")
TXOP9600.index = pd.to_datetime(TXOP9600.index)
VIX  = pd.read_csv("data/VIXTWN.csv", index_col="Date")
VIX.index = pd.to_datetime(VIX.index)
VIX = VIX*0.01

# === 讀csv ===
info  = pd.read_csv("data/華南永昌案例_基本資料.csv")
df_St  = pd.read_csv("data/華南永昌案例數據_計算.csv", index_col="Date")
df_St.index = pd.to_datetime(df_St.index)
if sigma_select=="台股指數的 HV": sigma_greeks = df_St["HV"].tolist()
if sigma_select=="永昌權證的 IV": sigma_greeks = df_St["A_IV"].tolist()
if sigma_select=="TXO9600的 IV": sigma_greeks = df_St["B_IV"].tolist()
if sigma_select=="VIX":          sigma_greeks = VIX["VIX_Close"].tolist()

df_price = bsmodel.get_greeks_vol(df_St, [10000,K_B,10000], ["Short Put","Long Put","Long Put"], r=0.01045, sigma=sigma_greeks, conversion=1)
tab1, tab2, tab3 = st.tabs(["📚 華南永昌案例基本資料","📚 華南永昌案例數據", "📈 Greeks"])
tab1.dataframe(info)
tab1.markdown("本研究假設無股息支付，因此q=0")
c1, c2 = tab2.columns([1,1], gap="small")
c1.dataframe(df_price)
c2.markdown("""
\n **資料說明**
\n St : 台灣加權指數收盤價，數據來源為TEJ
\n T-t : 距離到期日的時間(年)，數據來源為自行計算
\n HV : 歷史波動率，依當日及往前260個交易日資料計算標準差並換算成年波動，數據來源 [TEJ](https://www.tej.com.tw/webtej/doc/option.htm)
\n A_Close : 臺股指永昌96售04(以下簡稱永昌證)的每日收盤價，數據來源 [TEJ](https://www.tej.com.tw/webtej/doc/warnt.htm)
\n A_Value : 永昌證的理論價值，根據BS公式自行計算，σ使用<span style="color:red">每日的HV</span>
\n A_IV : 永昌證的隱含波動率，利用BS公式反推出隱含在該權證收盤價中的年波動率，數據來源 [TEJ](https://www.tej.com.tw/webtej/doc/warnt.htm)
\n A_Delta : 永昌證的Delta，根據BS公式自行計算，σ使用<span style="color:red">TXO的IV</span>
\n A_Gamma : 永昌證的Gamma，根據BS公式自行計算，σ使用<span style="color:red">TXO的IV</span>

\n B_Close : TXO202006P9600(以下簡稱TXO)的每日結算價，數據來源 [TEJ](https://www.tej.com.tw/webtej/doc/option.htm)
\n B_Value : TXO的理論價值，根據BS模型自行計算，σ使用<span style="color:red">每日的HV</span>
\n B_IV : TXO的隱含波動率，利用BS公式反推出隱含在該TXO結算價中的年波動率，數據來源 [TEJ](https://www.tej.com.tw/webtej/doc/option.htm)
\n B_Delta : TXO的Delta，根據BS公式自行計算，σ使用<span style="color:red">TXO的IV</span>
\n B_Gamma : TXO的Gamma，根據BS公式自行計算，σ使用<span style="color:red">TXO的IV</span>
""",unsafe_allow_html=True)

c1, c2 = tab3.columns([1,1], gap="small")
fig = px.line(df_price, y=["A_Delta","B_Delta"], title="Delta", height=300, template="plotly_white").update_layout(showlegend=False)
c1.plotly_chart(fig, use_container_width=True)
fig = px.line(df_price, y=["A_Gamma","B_Gamma"], title="Gamma", height=300, template="plotly_white").update_layout(showlegend=False)
c2.plotly_chart(fig, use_container_width=True)

# === Delta-Gamma避險 ===

df_delta = hedging.get_warrent_delta_hedge(df_price)
df_gamma = hedging.get_warrent_gamma_hedge(df_price)

tab1, tab2, tab3, tab4 = st.tabs(["📈 Delta、Delta-Gamma避險比較", "📚 Data", "📚 Data: Delta Hedging", "📚 Data: Delta-Gamma Hedging"])
df_mix = pd.concat([df_delta[["A部位損益","總損益"]], df_gamma[["總損益"]]], axis=1)
df_mix.columns =  ["No Hedging","Delta Hedging","Delta-Gamma Hedging"]
fig = px.line(df_mix,
              title="Delta避險損益、Delta-Gamma避險損益", height=400, width=700, template="plotly_white").update_layout(showlegend=True)
c1, c2 = tab1.columns([2,1], gap="small")
c1.plotly_chart(fig, use_container_width=True)
summary = pd.DataFrame([[df_delta["A部位損益"].iloc[-1], round(df_delta["A部位損益"].std(),2)],
                        [df_delta["總損益"].iloc[-1], round( df_delta["總損益"].std(),2)],
                        [df_gamma["總損益"].iloc[-1], round( df_gamma["總損益"].std(),2)]], columns=["最終總損益","總損益的標準差"], index=["不避險","Delta避險","Delta-Gamma避險"])
c2.dataframe(summary)
tab2.dataframe(df_mix)
tab3.dataframe(df_delta)
tab4.dataframe(df_gamma)


