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
import warnings
import random
from myfunction import bsmodel
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Greek Letters",
    page_icon="📈",
    #layout="wide",
)
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

st.header("Greek Letters")
st.text("GBM模擬股價，S0 = 50，T=1(1年)，共20步、一步t=0.05\
        \n觀察各期t的option價格、Greek Letters")

# 側邊
with st.sidebar:
    K_A = st.slider("Option A: Strike Price", 30, 70, 50, 1)
    CP_A = st.sidebar.selectbox(
    "Option A: Type",
    ("Long Call","Long Put","Short Call","Short Put"), label_visibility ="collapsed" )
    # B
    K_B = st.slider("Option B: Strike Price", 30, 70, 48, 1)
    CP_B = st.sidebar.selectbox(
    "Option B: Type",
    ("Long Call","Long Put","Short Call","Short Put"), label_visibility ="collapsed" )
    # C
    K_C = st.slider("Option C: Strike Price", 30, 70, 52, 1)
    CP_C = st.sidebar.selectbox(
    "Option C: Type",
    ("Long Call","Long Put","Short Call","Short Put"), label_visibility ="collapsed" )
    
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
    fig = px.line(df_price.round(2), x="第t期", y=["A_Price","B_Price","C_Price"], title="Option Price", height=300, width=500, template="plotly_white")#.update_layout(showlegend=False)
    st.plotly_chart(fig)

# Delta
c1, c2 = st.columns([2,0.5])
with c1:
    fig = px.line(df_price.round(4), x="第t期", y=["A_Delta","B_Delta","C_Delta"], title="Option Delta", labels={'value': "Delta"},height=300, width=500, template="plotly_white")#.update_layout(showlegend=False)
    st.plotly_chart(fig)
with c2:
    st.latex(r"""
    Delta \space of \space Call=\mathcal{N}(d_1) 
    """)
    st.latex(r"""
    Delta \space of \space Put=\mathcal{N}(d_1)-1
    """)
# Gamma
c1, c2 = st.columns([2,0.5])
with c1:
    fig = px.line(df_price.round(4), x="第t期", y=["A_Gamma","B_Gamma","C_Gamma"], title="Option Gamma", labels={'value': "Gamma"}, height=300, width=500, template="plotly_white")#.update_layout(showlegend=False)
    st.plotly_chart(fig)
with c2:
    st.latex(r"""
    Gamma= \frac{\mathcal{N}^{\prime}(d_1)}{S_0 \sigma \sqrt{T}}
    """)
# Vega
c1, c2 = st.columns([2,0.5])
with c1:
    fig = px.line(df_price.round(4), x="第t期", y=["A_Vega","B_Vega","C_Vega"], title="Option Vega", labels={'value': "Vega"}, height=300, width=500, template="plotly_white")#.update_layout(showlegend=False)
    st.plotly_chart(fig)
with c2:
    st.latex(r"""
    Vega= S_0 \sqrt{T} \mathcal{N}(d_1)
    """)
# Theta
c1, c2 = st.columns([2,0.5])
with c1:
    fig = px.line(df_price.round(4), x="第t期", y=["A_Theta","B_Theta","C_Theta"], title="Option Theta", labels={'value': "Theta"}, height=300, width=500, template="plotly_white")#.update_layout(showlegend=False)
    st.plotly_chart(fig)
with c2:
    st.latex(r"""
    Theta \space of \space Call= \frac{-S_0 \mathcal{N}^{\prime}(d_1) \sigma}{2\sqrt{T}} - rKe^{-rT} \mathcal{N}(d_2) \newline
    """)
    st.latex(r"""
    Theta \space of \space Put= \frac{-S_0 \mathcal{N}^{\prime}(d_1) \sigma}{2\sqrt{T}} + rKe^{-rT} \mathcal{N}(-d_2) \newline
    """)


