import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import datetime as dt
import matplotlib.pyplot as plt
import plotly.express as px
from scipy import log,exp,sqrt,stats
from scipy.stats import norm
import random
from myfunction import bsmodel

st.set_page_config(
    page_title="Delta-Gamma hedging",
    page_icon="📈",
    layout="wide",
)

# 不要有hamburger, footer: Made with Streamlit
st.markdown("""
<style>
.css-9s5bis edgvbvh3
{
    visibility: hidden;
}
.css-164nlkn egzxvld1 
{
    visibility: hidden;
}
</style>
""",unsafe_allow_html=True)
st.header("Delta-Gamma-Vega hedging")


# 側邊
with st.sidebar:
    st.text("券商賣100個單位的Call\n履約價=50")
    K_A = 50
    CP_A = "Short Call"
    # B
    K_B = st.slider("Option B: Strike Price", 30, 70, 48, 1)
    CP_B = st.sidebar.selectbox(
    "Option B: Type",
    ("Call","Put"), label_visibility ="collapsed" )
    # C
    K_C = st.slider("Option C: Strike Price", 30, 70, 52, 1)
    CP_C = st.sidebar.selectbox(
    "Option C: Type",
    ("Call","Put"), label_visibility ="collapsed" )
    

# 打開網頁時，隨機跑一個股價 ==============================================================================
if 'openweb' not in st.session_state:
    st.session_state.openweb = True
    df_St = bsmodel.get_GBM_St()
    st.session_state.df_St = df_St
    print("=== START ===")

# 按Simulate St 股價才會變動
if st.button("Simulate St"):
    df_St = bsmodel.get_GBM_St()
    st.write("YOU CLICK")
    st.session_state.df_St = df_St # 暫存df

df_price = bsmodel.get_greeks(st.session_state.df_St, K_list=[K_A,K_B,K_C], CP = [CP_A, CP_B, CP_C])   


# 股價 & Greek Letters圖 ==================================================================================



c1, c2 = st.columns(2)
with c1:
    fig = px.line(df_price.round(2), x="第t期", y="St", title="Stock Price",height=300, width=300, template="plotly_white").update_layout(showlegend=False)
    st.plotly_chart(fig)
with c2:
    fig = px.line(df_price.round(2), x="第t期", y=["A_Price","B_Price","C_Price"], title="Option Price", 
                  height=300, width=500, template="plotly_white")#.update_layout(showlegend=False)
    st.plotly_chart(fig)

# 損益圖 ==================================================================================
df_delta = bsmodel.get_delta_hedge(df_price)
df_gamma = bsmodel.get_gamma_hedge(df_price)
df_vega = bsmodel.get_vega_hedge(df_price)

df_all_hedge = pd.DataFrame(columns=["第t期","No Hedging","Delta Hedging","Delta-Gamma Hedging"])
df_all_hedge["第t期"] = df_delta["第t期"]
df_all_hedge["No Hedging"] = df_delta["A部位_損益"]
df_all_hedge["Delta Hedging"] = df_delta["總部位_損益"]
df_all_hedge["Delta-Gamma Hedging"] = df_gamma["總部位_損益"]
df_all_hedge["Delta-Gamma-Vega Hedging"] = df_vega["總部位_損益"]


fig = px.line(df_all_hedge.round(2), x="第t期", y=["No Hedging","Delta Hedging","Delta-Gamma Hedging","Delta-Gamma-Vega Hedging"], title="Delta-Gamma-Vega Hedging", \
               labels={"value":"profit"},height=300, width=500, template="plotly_white") 
st.plotly_chart(fig)

st.dataframe(df_all_hedge)

