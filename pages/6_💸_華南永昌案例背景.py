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
import warnings
warnings.filterwarnings("ignore")

# === 預設參數 ===
st.set_page_config(
    page_title="選擇權避險操作模組",
    page_icon="💸",
    layout="wide",
)
st.header("華南永昌案例背景")

c1, c2 = st.columns(2, gap="small")

#%% === 大盤指數Close ===
TAIEX  = pd.read_csv("data/TAIEX_noadj_201912-202006.csv", index_col="Date")
tab1, tab2 = c1.tabs(["📈 TAIEX Chart", "📚 TAIEX Data"])
TAIEX["K"] = 10000
fig = px.line(TAIEX.loc["2019-12-18":"2020-05-31"].round(2), y=["Close","K"], 
              title="TAIEX 2020年1-6月收盤價 ", height=400, template="plotly_white").update_layout(showlegend=True)
fig.update_layout(legend=dict( orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
tab1.plotly_chart(fig, use_container_width=True)
tab2.dataframe(TAIEX)

# === 期現貨 ==
TX  = pd.read_csv("data/TX2020.csv", index_col="日期")
TX.index = pd.to_datetime(TX.index)
name_list = TX.groupby("名稱").count().index
filt = TX["名稱"]=="台指 2020/06"
diff = pd.DataFrame(TX[filt]["標的證券價格"]-TX[filt]["收盤價"], columns=["價差"])

fig = make_subplots(rows=2, cols=1, shared_xaxes=True,  
                    vertical_spacing=0.03,  
                    row_width=[0.2, 0.7])
fig.add_trace( go.Line(x=TX[filt].index, y=TX[filt]["收盤價"], name="收盤價"))
fig.add_trace( go.Line(x=TX[filt].index, y=TX[filt]["標的證券價格"], name="標的證券價格"))

fig.add_trace(  go.Bar(x=diff.index, y=diff["價差"], name="價差"), row=2, col=1)

fig.update_layout( title="台指期和加權指數 2020年1-5月收盤價", yaxis=dict(title="台指期、加權指數"), yaxis2=dict(title="價差"),
    showlegend=True, template="plotly_white" )
fig.update_layout(legend=dict( orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
tab1, tab2 = c2.tabs(["📈 期貨價差 Chart", "📚 期貨價差 Data"])
tab1.plotly_chart(fig, use_container_width=True)
tab2.dataframe(TX)

#%% === 華南永昌Close ===
c1, c2 = st.columns([1,1], gap="small")
HuaNanPut  = pd.read_csv("data/股指永昌P_close.csv", index_col="Date")
tab1, tab2 = c1.tabs(["📈 收盤價Chart", "📚 收盤價Data"])
fig = px.line(HuaNanPut.loc["2019-12-18":"2020-05-31"].round(2), y=["臺股指永昌96售03","臺股指永昌96售04","臺股指永昌96售05","臺股指永昌96售06","臺股指永昌96售07"], 
              title="華南永昌2020年1-6月認售權證(PUT)收盤價", height=400, template="plotly_white").update_layout(showlegend=True)
tab1.plotly_chart(fig, use_container_width=True)
tab2.dataframe(HuaNanPut)

# === HV、IV、VIX ===
TXO  = pd.read_csv("data/TXO202006P9600.csv", index_col="Date")
TXO.index = pd.to_datetime(TXO.index)
VIX  = pd.read_csv("data/VIXTWN.csv", index_col="Date")
VIX.index = pd.to_datetime(VIX.index)
VIX = VIX*0.01
fig2 = px.line(pd.concat([TXO, VIX],axis=1).loc["2019-12-18":"2020-05-31"].round(2), y=["波動性","隱含波動","VIX_Close"],
              title="歷史波動率&隱含波動率", height=400, template="plotly_white").update_layout(showlegend=True)
fig2.update_traces(name="歷史波動率", selector=dict(name="波動性")
)

tab1, tab2, tab3, tab4 = c2.tabs(["📈 TXO Chart", "📚 TXO Data", "📚 VIX Data", "📚 VIX 說明"])
tab1.plotly_chart(fig2, use_container_width=True)
tab1.markdown("""
    * 歷史波動率: 依當日及往前260個台股指數交易日資料計算標準差 => 理論價格 \n
    * 隱含波動率: 用TXO202006P9600收盤價反推出來的隱含波動率
    * VIX_Close: 臺指選擇權波動率指數的每日收盤價""")
tab2.markdown("TXO202006P9600")
tab2.dataframe(TXO)
tab3.dataframe(VIX)
tab4.markdown("""
**臺指選擇權波動率指數 VIX TWN**
\n [統一期貨說明](https://www.pfcf.com.tw/product/detail/2923)
\n 細看軟體報價，可以發現CALL跟PUT的隱含波動率不同，各履約價的隱含波動率也並不一樣(稱為Option Smile現象)，為了滿足方便解讀的需求，交易所便編制VIX指數來代表該商品整體選擇權的波動率，第一檔也是最知名的CBOE交易所VIX指數，即是代表S&P500期權的隱含波動率。而我們熟悉的台指選擇權，台灣期交所也於2006年推出台指權VIX。
\n [期交所說明](https://www.taifex.com.tw/cht/7/vixQA)
\n 波動率指數(VXO, Volatility Index)為美國芝加哥選擇權交易所 (CBOE)於1993年推出，目的係藉由當時市場對未來30天股票市場波動率看法，提供選擇權交易人更多元化資訊，作為交易及避險操作策略參考。2003年9月22日CBOE將原來S&P 100股價指數選擇權價格，改以S&P 500股價指數選擇權報價中價進行採樣，計算VIX指數，對未來市場預期提供更為堅實衡量方法。一般而言，VIX指數愈高時，顯示交易人預期未來股價指數的波動程度愈劇烈；相反地，VIX指數愈低時，顯示交易人預期股價指數變動將趨於和緩。由於該指數具有描述投資人心理變化情形，故又稱為「投資人恐慌指標(The investor fear gauge)」。

臺灣期貨交易所2006年12月18日推出「臺指選擇權波動率指數(TAIWAN VIX)」，即是參考CBOE VIX指數方法，及臺指選擇權(TXO)市場特性編製而成，以期正確地描繪當時市場上價格波動情形，提供選擇權交易人更多資訊內容，協助其判斷市場狀況與擬定合宜交易決策。""")

# === 讀csv ===
df_St  = pd.read_csv("data/華南永昌案例數據_計算.csv", index_col="Date")
df_St.index = pd.to_datetime(df_St.index)
df_price = bsmodel.get_greeks_vol(df_St, [10000,9600,10000], ["Short Put","Long Put","Long Put"], r=0.01045, sigma=VIX["VIX_Close"].tolist(), conversion=1)



#%% 
tab1, tab2, tab3, tab4 = st.tabs(["📈 Charts", "📚 Data", "📚 3", "📚 4"])
warrent  = pd.read_csv("data/93-96權證.csv")
warrent["日期"] = pd.to_datetime(warrent["日期"])
warrent["名稱"] = warrent["名稱"]+" "+warrent["履約價(元)"].apply(int).apply(str)


# 選券商
tab1.markdown("**券商:**")
brokers =  warrent.groupby("券商").count().index
col_brokers = tab1.columns(len(brokers))
chosen_brokers = []
for bIdx in range(len(brokers)):
    if (bIdx==1) or (bIdx==4) or (bIdx==10) or (bIdx==13):  # 預設3券商、永昌
        if col_brokers[bIdx].checkbox(label=brokers[bIdx], value=True):
            chosen_brokers.append(brokers[bIdx])
    else:
        if col_brokers[bIdx].checkbox(label=brokers[bIdx], value=False):
            chosen_brokers.append(brokers[bIdx])
# 選到期月份
tab1.markdown("**到期月份:**")
maturity = warrent.groupby("到期月份").count().index
col_maturity = tab1.columns(len(maturity))
chosen_maturity = []
for mIdx in range(len(maturity)): 
    if mIdx == 5:   # 預設6月到期
        if col_maturity[mIdx].checkbox(label=maturity[mIdx], value=True):
            chosen_maturity.append(maturity[mIdx])
        
    else:
        if col_maturity[mIdx].checkbox(label=maturity[mIdx], value=False):
            chosen_maturity.append(maturity[mIdx])


# 選名稱
filt = warrent[warrent["券商"].isin(chosen_brokers)&warrent["到期月份"].isin(chosen_maturity)]
names = filt.groupby("名稱").count().index
chosen_warrent = tab1.multiselect( "**權證:**", names, default=["臺股指永昌96售04 10000","臺股指凱基96售08 10000","臺股指群益96售02 10000","臺股指元大96售03 10400"])

c1, c2 = tab1.columns(2)
try:
    fig1 = make_subplots(rows=1, cols=1)
    fig2 = make_subplots(rows=1, cols=1)
    fig3 = make_subplots(rows=1, cols=1)
    for windex in range(len(chosen_warrent)):
        df = warrent[warrent["名稱"]==chosen_warrent[windex]]
        fig1.add_trace(  go.Line(x=df["日期"], y=df["權證收盤價(元)"], name=chosen_warrent[windex]),  row=1, col=1  )  
        fig2.add_trace(  go.Line(x=df["日期"], y=df["權證收盤價(元)"]/df["權證收盤價(元)"].iloc[0], name=chosen_warrent[windex]),  row=1, col=1  )  
        fig3.add_scatter(x=df["日期"], y=df["隱含波動"],  name=chosen_warrent[windex])
    fig1.update_layout( title="權證收盤價", yaxis=dict(title="收盤價"), height=400, width=1000, showlegend=True, template="plotly_white",
                       legend=dict( orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig2.update_layout( title="權證收盤價(百分比)", yaxis=dict(title="百分比"), height=400, width=1000, showlegend=True, template="plotly_white",
                       legend=dict( orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig3.update_layout( title="隱含波動", yaxis=dict(title="%"), height=400, width=1000, showlegend=True, template="plotly_white",
                       legend=dict( orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    c1.plotly_chart(fig1, use_container_width=True)
    c2.plotly_chart(fig2, use_container_width=True)
except:
    print("ERORRRRRRRR")
    tab1.text("...請選擇權證產生收盤價線圖")
    pass
tab2.dataframe(warrent[warrent["名稱"].isin(chosen_warrent)])
st.plotly_chart(fig3, use_container_width=True)

