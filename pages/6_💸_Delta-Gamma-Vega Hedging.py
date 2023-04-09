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

st.set_page_config(
    page_title="Delta-Gamma hedging",
    page_icon="📈",
    layout="wide",
)

st.header("Delta-Gamma-Vega hedging")


# 側邊
with st.sidebar:
    st.markdown("**Option A**")
    st.text("券商賣100個單位的Call\n履約價=50")
    K_A = 50
    CP_A = "Call"
    # B
    st.markdown("**Option B: Strike Price**")
    K_B = st.slider("Option B: Strike Price", 30, 70, 48, 1, label_visibility ="collapsed" )
    CP_B = st.sidebar.selectbox(
    "Option B: Type",
    ("Call","Put"), label_visibility ="collapsed" )
    # C
    st.markdown("**Option C: Strike Price**")
    K_C = st.slider("Option C: Strike Price", 30, 70, 52, 1, label_visibility ="collapsed" )
    CP_C = st.sidebar.selectbox(
    "Option C: Type",
    ("Call","Put"), label_visibility ="collapsed" )
    

# 打開網頁時，隨機跑一個股價 ==============================================================================
if 'openweb' not in st.session_state:
    st.session_state.openweb = True
    df_St = bsmodel.get_GBM_St()
    st.session_state.df_St = df_St
    print("=== START ===")

st.markdown("**GBM Simulates St Param**")
c1, c2 = st.columns(2)
with c1: 
    inputsteps = st.slider("steps", 10, 70, 20, 5)
with c2:
    inputsigma = st.slider("sigma", 0.1, 1.0, 0.3, 0.1)
# 按Simulate St 股價才會變動
if st.button("Simulate St"):
    df_St = bsmodel.get_GBM_St(inputsteps)
    st.session_state.df_St = df_St # 暫存df

df_price = bsmodel.get_greeks(st.session_state.df_St, K_list=[K_A,K_B,K_C], CP = [CP_A, CP_B, CP_C])   

# 股價 & Greek Letters圖 ==================================================================================
c1, c2 = st.columns(2)
with c1:
    fig = px.line(df_price.round(2), x="t", y="St", title="Stock Price",height=300, width=400, template="plotly_white").update_layout(showlegend=False)
    st.plotly_chart(fig)
with c2:
    fig = px.line(df_price.round(2), x="t", y=["A_Price","B_Price","C_Price"], title="Option Price", 
                  height=300, width=400, template="plotly_white")#.update_layout(showlegend=False)
    fig.update_layout(legend=dict( orientation="h",
                        yanchor="bottom", y=1.02,
                        xanchor="right", x=1))
    st.plotly_chart(fig)

# 損益圖 ==================================================================================
df_delta = bsmodel.get_delta_hedge(df_price)
df_gamma = bsmodel.get_gamma_hedge(df_price)
df_vega = bsmodel.get_vega_hedge(df_price)

df_all_hedge = pd.DataFrame(columns=["t","No Hedging","Delta Hedging","Delta-Gamma Hedging"])
df_all_hedge["t"] = df_delta["t"]
df_all_hedge["No Hedging"] = df_delta["Option_Profit"]
df_all_hedge["Delta Hedging"] = df_delta["Total_Profit"]
df_all_hedge["Delta-Gamma Hedging"] = df_gamma["Total_Profit"]
df_all_hedge["Delta-Gamma-Vega Hedging"] = df_vega["Total_Profit"]

hedge_list = []
c1, c2, c3, c4 = st.columns([1,1,1.5,1.5])
with c1: 
    if st.checkbox("No Hedging",value=True):
        hedge_list.append("No Hedging")
with c2: 
    if st.checkbox("Delta Hedging",value=True):
        hedge_list.append("Delta Hedging")
with c3: 
    if st.checkbox("Delta-Gamma Hedging",value=True):
        hedge_list.append("Delta-Gamma Hedging")
with c4: 
    if st.checkbox("Delta-Gamma-Vega Hedging",value=True):
        hedge_list.append("Delta-Gamma-Vega Hedging")



#fig = px.line(df_all_hedge.round(2), x="t", y=["No Hedging","Delta Hedging","Delta-Gamma Hedging","Delta-Gamma-Vega Hedging"], title="Delta-Gamma-Vega Hedging", \
#               labels={"value":"profit"},height=300, width=500, template="plotly_white") 
fig = px.line(df_all_hedge.round(2), x="t", y=hedge_list, title="Delta-Gamma-Vega Hedging", \
               labels={"value":"profit"},height=400, width=700, template="plotly_white") 

st.plotly_chart(fig)

#st.dataframe(df_all_hedge)

