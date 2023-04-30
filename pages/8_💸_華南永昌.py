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
    page_icon="📈",
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