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
    page_title="華南永昌案例",
    page_icon="💸",
    layout="wide",
)
st.header("華南永昌案例")


c1, c2 = st.columns(2, gap="large")
# === 大盤指數Close ===
TAIEX  = pd.read_csv("data/TAIEX_noadj_201912-202006.csv", index_col="Date")
tab1, tab2 = c1.tabs(["📈 TAIEX Chart", "🗃 TAIEX Data"])
fig = px.line(TAIEX.loc["2020-03-01":"2020-05-31"].round(2), y=["Close"], 
              title="TAIEX 2020年3-5月收盤價 ", height=400, template="plotly_white").update_layout(showlegend=False)
tab1.plotly_chart(fig, use_container_width=True)
tab2.dataframe(TAIEX)

# === 華南永昌Close ===
HuaNanPut  = pd.read_csv("data/股指永昌P_close.csv", index_col="Date")
tab1, tab2 = c2.tabs(["📈 收盤價Chart", "🗃 收盤價Data"])
fig = px.line(HuaNanPut.loc["2020-03-01":"2020-05-31"].round(2), y=["臺股指永昌96售03","臺股指永昌96售04","臺股指永昌96售05","臺股指永昌96售06","臺股指永昌96售07"], 
              title="華南永昌2020年3-5月認售權證(PUT)收盤價", height=400, template="plotly_white").update_layout(showlegend=True)
tab1.plotly_chart(fig, use_container_width=True)
tab2.dataframe(HuaNanPut)

# === 波動率 ===
TXO  = pd.read_csv("data/TXO202006P9600.csv", index_col="Date")
tab1, tab2 = st.tabs(["📈 TXO Chart", "🗃 TXO Data"])
c1, c2 = tab1.columns(2, gap="large")

fig = px.line(TXO.loc["2020-03-01":"2020-05-31"].round(2), y=["Close"], 
              title="TXO202006P9600 2020年3-5月收盤價", height=400, template="plotly_white").update_layout(showlegend=True)
c1.plotly_chart(fig, use_container_width=True)
c1.markdown(""" * TXO202006P9600 = 以台股指為標的，2022年6月到期的台指選PUT，K=9600""")
fig = px.line(TXO.loc["2020-01-01":"2020-05-31"].round(2), y=["波動性","隱含波動"], 
              title="歷史波動率&隱含波動率", height=400, template="plotly_white").update_layout(showlegend=True)
c2.plotly_chart(fig, use_container_width=True)
c2.markdown("""
    * 歷史波動率: 依當日及往前260個交易日資料計算標準差 => 理論價格 \n
    * 隱含波動率: 用TXO202006P9600收盤價反推出來""")
tab2.dataframe(TXO)

# === 讀csv ===
info  = pd.read_csv("data/華南永昌案例_基本資料.csv")
df_price  = pd.read_csv("data/華南永昌案例數據_計算.csv", index_col="Date")
df_price.index = pd.to_datetime(df_price.index)

tab1, tab2, tab3 = st.tabs(["🗃 華南永昌案例基本資料","🗃 華南永昌案例數據", "📈 大盤指數"])
tab1.dataframe(info)
tab1.markdown("本研究假設無股息支付，因此q=0")
c1, c2 = tab2.columns([1,1], gap="small")
c1.dataframe(df_price)
fig = px.line(df_price.loc["2020-01-01":"2020-05-31"].round(2), y=["St"], 
              title="台灣加權指數 TAIEX 2020年1-5月收盤價 ", height=400, template="plotly_white").update_layout(showlegend=False)
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

tab3.plotly_chart(fig, use_container_width=True)


# === Delta-Gamma避險 ===
def get_warrent_delta_hedge(df_price, r=0.01045, sigma=0.3, TTE=183/365, sell_price=2.355, quantity=20000, conversion=0.06):
    df_delta = pd.DataFrame(index=df_price.index,columns=["St","現貨持有量","現貨增減量","現貨增減成本","現貨利息成本 ","現貨累積成本",
                                     "A部位損益","現貨部位損益","總損益"])
    
    df_delta["St"] = df_price["St"]
    df_delta["現貨持有量"] = - round( df_price["A_Delta"] * quantity * conversion, 2 )
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
    df_delta["A部位損益"] = ( sell_price * exp( r * (TTE-df_price["T-t"]) )-  df_price["A_Value"] ) * quantity
    df_delta["現貨部位損益"] =  df_delta["現貨持有量"] * df_price["St"] - df_delta["現貨累積成本"]
    df_delta["總損益"] =  df_delta["A部位損益"] + df_delta["現貨部位損益"]
    df_delta = pd.concat([df_price["T-t"],df_delta.astype(float)],axis=1)
    return df_delta.round(2)

def get_warrent_gamma_hedge(df_price, r=0.01045, sigma=0.3, TTE=183/365, sell_price=2.355, quantity=20000, conversion=0.06):
    df_gamma = pd.DataFrame(index=df_price.index, columns=["St","B持有量","B增減量","B增減成本","B利息成本","B累積成本",
                                     "用B避險後的總Delta","現貨持有量","現貨增減量","現貨增減成本","現貨利息成本 ","現貨累積成本",
                                     "A部位損益","B部位損益","現貨部位損益","總損益"])
    df_gamma["St"] = df_price["St"]
    # B 部位
    df_gamma["B持有量"] = -1 * round( df_price["A_Gamma"] * quantity * conversion / df_price["B_Gamma"], 8 )
    df_gamma["B持有量"][df_gamma["B持有量"].isnull()]=0
    df_gamma.replace([np.inf, -np.inf], 0, inplace=True)
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
    df_gamma.iloc[-1]["B利息成本"] ="123121312"
    df_gamma["用B避險後的總Delta"] = df_price["A_Delta"] * quantity * conversion + df_gamma["B持有量"] * df_price["B_Delta"]
    # 現貨部位
    df_gamma["現貨持有量"] = round( -1 * df_gamma["用B避險後的總Delta"], 8 )
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
    df_gamma["A部位損益"] = ( sell_price * exp( r * (TTE-df_price["T-t"]) ) -  df_price["A_Value"] ) * quantity
    df_gamma["B部位損益"] = df_gamma["B持有量"] * df_price["B_Settlement Price"] - df_gamma["B累積成本"]
    df_gamma["現貨部位損益"] =  df_gamma["現貨持有量"] * df_price["St"] - df_gamma["現貨累積成本"]
    df_gamma["總損益"] =  df_gamma["A部位損益"] + df_gamma["B部位損益"] + df_gamma["現貨部位損益"]
    df_gamma = pd.concat([df_price["T-t"], df_gamma.astype(float)],axis=1)
    return df_gamma.round(2)
df_delta = get_warrent_delta_hedge(df_price)
df_gamma = get_warrent_gamma_hedge(df_price)
tab1, tab2, tab3, tab4 = st.tabs(["📈 Delta-Gamma避險損益", "🗃 Data", "🗃 Data: Delta Hedging", "🗃 Data: Delta-Gamma Hedging"])
df_mix = pd.concat([df_delta[["A部位損益","總損益"]], df_gamma[["總損益"]]], axis=1)
df_mix.columns =  ["No Hedging","Delta Hedging","Delta-Gamma Hedging"]
fig = px.line(df_mix,
              title="Delta避險損益、Delta-Gamma避險損益", height=400, width=700, template="plotly_white").update_layout(showlegend=True)
tab1.plotly_chart(fig, use_container_width=False)
tab2.dataframe(df_mix)
tab3.dataframe(df_delta)
tab4.dataframe(df_gamma)
