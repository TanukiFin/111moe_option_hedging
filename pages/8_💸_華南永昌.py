import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import datetime
import matplotlib.pyplot as plt
import plotly.express as px
from scipy import log,exp,sqrt,stats
from scipy.stats import norm
import random
from myfunction import bsmodel
import warnings
warnings.filterwarnings("ignore")

# === 預設參數 ===
st.set_page_config(
    page_title="選擇權避險操作模組",
    page_icon="💸",
    layout="wide",
)
st.header("華南永昌案例")

with st.sidebar:
    sigma_select = st.sidebar.selectbox( "**用於計算Greeks的波動率基礎**", ("台股指數的 HV","永昌權證的 IV","TXO9600的 IV","VIX"))

c1, c2 = st.columns(2, gap="large")
# === 大盤指數Close ===
TAIEX  = pd.read_csv("data/TAIEX_noadj_201912-202006.csv", index_col="Date")
tab1, tab2 = c1.tabs(["📈 TAIEX Chart", "📚 TAIEX Data"])
TAIEX["K"] = 10000
fig = px.line(TAIEX.loc["2019-12-18":"2020-05-31"].round(2), y=["Close","K"], 
              title="TAIEX 2020年3-5月收盤價 ", height=400, template="plotly_white").update_layout(showlegend=True)
fig.update_layout(legend=dict( orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
tab1.plotly_chart(fig, use_container_width=True)
tab2.dataframe(TAIEX)

# === 華南永昌Close ===
HuaNanPut  = pd.read_csv("data/股指永昌P_close.csv", index_col="Date")
tab1, tab2 = c2.tabs(["📈 收盤價Chart", "📚 收盤價Data"])
fig = px.line(HuaNanPut.loc["2019-12-18":"2020-05-31"].round(2), y=["臺股指永昌96售03","臺股指永昌96售04","臺股指永昌96售05","臺股指永昌96售06","臺股指永昌96售07"], 
              title="華南永昌2020年3-5月認售權證(PUT)收盤價", height=400, template="plotly_white").update_layout(showlegend=True)
tab1.plotly_chart(fig, use_container_width=True)
tab2.dataframe(HuaNanPut)

# === 波動率 ===
TXO  = pd.read_csv("data/TXO202006P9600.csv", index_col="Date")
TXO.index = pd.to_datetime(TXO.index)
VIX  = pd.read_csv("data/VIXTWN.csv", index_col="Date")
VIX.index = pd.to_datetime(VIX.index)
VIX = VIX*0.01
tab1, tab2, tab3 = st.tabs(["📈 TXO Chart", "📚 TXO Data", "📚 VIX Data"])
c1, c2 = tab1.columns(2, gap="large")

fig1 = px.line(TXO.loc["2019-12-18":"2020-05-31"].round(2), y=["Close"], 
              title="TXO202006P9600 2020年3-5月收盤價", height=400, template="plotly_white").update_layout(showlegend=True)
c1.plotly_chart(fig1, use_container_width=True)
c1.markdown(""" * TXO202006P9600 = 以台股指為標的，2022年6月到期的台指選PUT，K=9600""")
fig2 = px.line(pd.concat([TXO, VIX],axis=1).loc["2019-12-18":"2020-05-31"].round(2), y=["波動性","隱含波動","VIX_Close"],
              title="歷史波動率&隱含波動率", height=400, template="plotly_white").update_layout(showlegend=True)
fig2.update_traces(name="歷史波動率", selector=dict(name="波動性")
)
c2.plotly_chart(fig2, use_container_width=True)
c2.markdown("""
    * 歷史波動率: 依當日及往前260個台股指數交易日資料計算標準差 => 理論價格 \n
    * 隱含波動率: 用TXO202006P9600收盤價反推出來的隱含波動率
    * VIX_Close: 臺指選擇權波動率指數的每日收盤價""")
tab2.markdown("TXO202006P9600")
tab2.dataframe(TXO)
c1, c2 = tab3.columns(2, gap="large")
c1.dataframe(VIX)
c2.markdown("""
**臺指選擇權波動率指數 VIX TWN**
\n [統一期貨說明](https://www.pfcf.com.tw/product/detail/2923)
\n 細看軟體報價，可以發現CALL跟PUT的隱含波動率不同，各履約價的隱含波動率也並不一樣(稱為Option Smile現象)，為了滿足方便解讀的需求，交易所便編制VIX指數來代表該商品整體選擇權的波動率，第一檔也是最知名的CBOE交易所VIX指數，即是代表S&P500期權的隱含波動率。而我們熟悉的台指選擇權，台灣期交所也於2006年推出台指權VIX。
\n [期交所說明](https://www.taifex.com.tw/cht/7/vixQA)
\n 波動率指數(VXO, Volatility Index)為美國芝加哥選擇權交易所 (CBOE)於1993年推出，目的係藉由當時市場對未來30天股票市場波動率看法，提供選擇權交易人更多元化資訊，作為交易及避險操作策略參考。2003年9月22日CBOE將原來S&P 100股價指數選擇權價格，改以S&P 500股價指數選擇權報價中價進行採樣，計算VIX指數，對未來市場預期提供更為堅實衡量方法。一般而言，VIX指數愈高時，顯示交易人預期未來股價指數的波動程度愈劇烈；相反地，VIX指數愈低時，顯示交易人預期股價指數變動將趨於和緩。由於該指數具有描述投資人心理變化情形，故又稱為「投資人恐慌指標(The investor fear gauge)」。

臺灣期貨交易所2006年12月18日推出「臺指選擇權波動率指數(TAIWAN VIX)」，即是參考CBOE VIX指數方法，及臺指選擇權(TXO)市場特性編製而成，以期正確地描繪當時市場上價格波動情形，提供選擇權交易人更多資訊內容，協助其判斷市場狀況與擬定合宜交易決策。""")



# === 讀csv ===
info  = pd.read_csv("data/華南永昌案例_基本資料.csv")
df_St  = pd.read_csv("data/華南永昌案例數據_計算.csv", index_col="Date")
df_St.index = pd.to_datetime(df_St.index)
#( "**用於計算Greeks的波動率基礎**", ("台股指數的 HV","永昌權證的 IV","TXO9600的 IV","VIX"))
if sigma_select=="台股指數的 HV": sigma_greeks = df_St["HV"].tolist()
if sigma_select=="永昌權證的 IV": sigma_greeks = df_St["A_IV"].tolist()
if sigma_select=="TXO9600的 IV": sigma_greeks = df_St["B_IV"].tolist()
if sigma_select=="VIX":          sigma_greeks = VIX["VIX_Close"].tolist()

df_price = bsmodel.get_greeks_vol(df_St, [10000,9600,10000], ["Short Put","Long Put","Long Put"], r=0.01045, sigma=sigma_greeks, conversion=1)
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
def get_warrent_delta_hedge(df_price, freq=1, r=0.01045, TTE=183/365, sell_price=2.355, quantity=20000, conversion=0.06):
    df_delta = pd.DataFrame(index=df_price.index,columns=["St","現貨持有量","現貨增減量","現貨增減成本","現貨利息成本 ","現貨累積成本",
                                     "A部位損益","現貨部位損益","總損益"])
    df_delta["St"] = df_price["St"]
    for step in range(0, len(df_price)): #0~20
        if step%freq == 0: df_delta["現貨持有量"].iloc[step] = - round( df_price["A_Delta"].iloc[step] * quantity * conversion, 2 )
        else:              df_delta["現貨持有量"].iloc[step] = df_delta["現貨持有量"].iloc[step-1]
    df_delta.at[df_delta.index[-1], "現貨持有量"] = 0
    df_delta["現貨增減量"] = df_delta["現貨持有量"] - df_delta["現貨持有量"].shift()
    df_delta["現貨增減量"].iloc[0] = df_delta["現貨持有量"].iloc[0]
    df_delta["現貨增減成本"] = df_delta["現貨增減量"] * df_price["St"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_delta["現貨利息成本 "].iloc[0] = 0.0
            df_delta["現貨累積成本"].iloc[0] = df_delta["現貨增減成本"].iloc[0]
        else:
            df_delta.at[df_delta.index[step],"現貨利息成本 "] = df_delta["現貨累積成本"].iloc[step-1] *  (exp( r *(df_price["T-t"].iloc[step-1]-df_price["T-t"].iloc[step]) )-1)
            df_delta.at[df_delta.index[step],"現貨累積成本"] = df_delta["現貨累積成本"].iloc[step-1] \
                                                        + df_delta["現貨增減成本"].iloc[step] \
                                                        + df_delta["現貨利息成本 "].iloc[step]
    df_delta["A部位損益"] = ( sell_price * exp( r * (TTE-df_price["T-t"]) )-  df_price["A_Close"] ) * quantity
    df_delta["現貨部位損益"] =  df_delta["現貨持有量"] * df_price["St"] - df_delta["現貨累積成本"]
    df_delta["總損益"] =  df_delta["A部位損益"] + df_delta["現貨部位損益"]
    df_delta = pd.concat([df_price["T-t"],df_delta.astype(float)],axis=1)
    return df_delta.round(2)

def get_warrent_gamma_hedge(df_price, freq=1, r=0.01045, TTE=183/365, sell_price=2.355, quantity=20000, conversion=0.06):
    df_gamma = pd.DataFrame(index=df_price.index, columns=["St","B持有量","B增減量","B增減成本","B利息成本","B累積成本",
                                     "用B避險後的總Delta","現貨持有量","現貨增減量","現貨增減成本","現貨利息成本 ","現貨累積成本",
                                     "A部位損益","B部位損益","現貨部位損益","總損益"])
    df_gamma["St"] = df_price["St"]
    # 計算 B持有量
    for step in range(0, len(df_price)): 
        if step%freq == 0: df_gamma["B持有量"].iloc[step] = -1 * round( df_price["A_Gamma"].iloc[step] * quantity * conversion / df_price["B_Gamma"].iloc[step], 8 )
        else:              df_gamma["B持有量"].iloc[step] = df_gamma["B持有量"].iloc[step-1]
    df_gamma["B持有量"][df_gamma["B持有量"].isnull()]=0
    df_gamma.replace([np.inf, -np.inf], 0, inplace=True)
    df_gamma["用B避險後的總Delta"] = df_price["A_Delta"] * quantity * conversion + df_gamma["B持有量"] * df_price["B_Delta"]
    # 計算 現貨持有量
    for step in range(0, len(df_price)): 
        if step%freq == 0: df_gamma["現貨持有量"].iloc[step] = round( -1 * df_gamma["用B避險後的總Delta"].iloc[step], 8 )
        else:              df_gamma["現貨持有量"].iloc[step] = df_gamma["現貨持有量"].iloc[step-1]
    df_gamma.at[df_gamma.index[-1], "B持有量"] = 0
    df_gamma.at[df_gamma.index[-1], "現貨持有量"] = 0
    # 計算 B成本
    df_gamma["B增減量"] = df_gamma["B持有量"] - df_gamma["B持有量"].shift()
    df_gamma["B增減量"].iloc[0] = df_gamma["B持有量"].iloc[0]
    df_gamma["B增減成本"] = df_gamma["B增減量"] * df_price["B_Settlement Price"]
    for step in range(0, len(df_price)): 
        if step == 0:
            df_gamma["B利息成本"] = 0.0
            df_gamma["B累積成本"] = df_gamma["B增減成本"].iloc[0]
        else:
            df_gamma.at[df_gamma.index[step],"B利息成本"] \
                = df_gamma["B累積成本"].iloc[step-1] *  (exp( r *(df_price["T-t"].iloc[step-1]-df_price["T-t"].iloc[step]) )-1)
            df_gamma.at[df_gamma.index[step],"B累積成本"] \
                = df_gamma["B累積成本"].iloc[step-1] + df_gamma["B增減成本"].iloc[step] + df_gamma["B利息成本"].iloc[step]
    # 計算現貨成本
    df_gamma["現貨增減量"] = df_gamma["現貨持有量"] - df_gamma["現貨持有量"].shift()
    df_gamma["現貨增減量"].iloc[0] = df_gamma["現貨持有量"].iloc[0]
    df_gamma["現貨增減成本"] = df_gamma["現貨增減量"] * df_price["St"]
    for step in range(0, len(df_price)): #0~20
        if step == 0:
            df_gamma["現貨利息成本 "] = 0.0
            df_gamma["現貨累積成本"] = df_gamma["現貨增減成本"].iloc[0]
        else:
            df_gamma.at[df_gamma.index[step],"現貨利息成本 "] = df_gamma["現貨累積成本"].iloc[step-1] *  (exp( r *(df_price["T-t"].iloc[step-1]-df_price["T-t"].iloc[step]) )-1)
            df_gamma.at[df_gamma.index[step],"現貨累積成本"] = df_gamma["現貨累積成本"].iloc[step-1] \
                                                        + df_gamma["現貨增減成本"].iloc[step] \
                                                        + df_gamma["現貨利息成本 "].iloc[step]
    df_gamma["A部位損益"] = ( sell_price * exp( r * (TTE-df_price["T-t"]) ) -  df_price["A_Close"] ) * quantity
    df_gamma["B部位損益"] = df_gamma["B持有量"] * df_price["B_Settlement Price"] - df_gamma["B累積成本"]
    df_gamma["現貨部位損益"] =  df_gamma["現貨持有量"] * df_price["St"] - df_gamma["現貨累積成本"]
    df_gamma["總損益"] =  df_gamma["A部位損益"] + df_gamma["B部位損益"] + df_gamma["現貨部位損益"]
    df_gamma = pd.concat([df_price["T-t"], df_gamma.astype(float)],axis=1)
    return df_gamma.round(2)

df_delta = get_warrent_delta_hedge(df_price)
df_gamma = get_warrent_gamma_hedge(df_price)

tab1, tab2, tab3, tab4 = st.tabs(["📈 Delta、Delta-Gamma避險比較", "📚 Data", "📚 Data: Delta Hedging", "📚 Data: Delta-Gamma Hedging"])
df_mix = pd.concat([df_delta[["A部位損益","總損益"]], df_gamma[["總損益"]]], axis=1)
df_mix.columns =  ["No Hedging","Delta Hedging","Delta-Gamma Hedging"]
fig = px.line(df_mix,
              title="Delta避險損益、Delta-Gamma避險損益", height=400, width=700, template="plotly_white").update_layout(showlegend=True)
tab1.plotly_chart(fig, use_container_width=False)
tab2.dataframe(df_mix)
tab3.markdown("最終總損益"+str(df_delta["總損益"].iloc[-1]))
tab3.dataframe(df_delta)
tab4.markdown("最終總損益"+str(df_gamma["總損益"].iloc[-1]))
tab4.dataframe(df_gamma)
st.markdown( "Delta總損益的標準差:  "+ str(round( df_delta["總損益"].std(),2)) )
st.markdown( "Delta-Gamma總損益的標準差:  "+str(round( df_gamma["總損益"].std(),2) ))
st.markdown( "不避險的標準差:  "+ str(round(df_gamma["A部位損益"].std(),2) ))