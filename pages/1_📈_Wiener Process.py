import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import datetime as dt
import matplotlib.pyplot as plt
import plotly.express as px
import warnings
warnings.filterwarnings("ignore")


st.set_page_config(
    page_title="選擇權避險操作模組",
    page_icon="💸",
    #layout="wide",
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

class getOneWienerProcess:
    def __init__(self):
        time = np.linspace(0,1,11) # [0,1,2,3,4,5,6,7,8,9,10,11]
        sigma = 1
        WP=[0] #W(0)=0
        dw = np.random.normal(0, scale=sigma, size=10) # scale=SD標準差, size=抽出樣本數
        for x in range(len(time)-1):
            WP.append(WP[x]+dw[x])
        self.fig = px.line(WP, markers=True, height=300, width=500, template="plotly_white")
        self.df=pd.DataFrame([time, dw, WP], index=["time","dw","WP"])

class getMultWienerProcess:
    def __init__(self, steps, numberOfSims):
        # steps = number of steps
        # number = number of sims
        T = 1 # time in years
        W0 = 0 # initial stock price
        dt = T/steps # calc each time step

        dw = np.random.normal(0, np.sqrt(dt), size=(steps,numberOfSims))
        dw = np.vstack([np.zeros(numberOfSims), dw]) 
        Wt = W0 + dw.cumsum(axis=0)

        time = np.linspace(0,T,steps+1)
        self.df=pd.DataFrame(Wt, index=time)
        self.fig = px.line(self.df, height=400, width=600, template="plotly_white").update_layout(showlegend=False)



# WEB
# 1. Wiener Process ==============================================================================
st.header("Wiener Process 維納過程")
st.markdown("""
又稱為標準布朗運動

The process followed by the variable we have been considering is known as a Wiener process. It is a particular type of Markov stochastic process with a mean change of zero and a variance rate of 1.0 per year. It has been used in physics to describe the motion of a particle that is subject to a large number of small molecular shocks and is sometimes referred to as Brownian motion.Expressed formally, a variable z follows a Wiener process if it has the following two properties:

我們一直在考慮的變量所遵循的過程稱為維納過程。 它是一種特殊類型的馬爾可夫隨機過程，平均變化為零，方差率為每年 1.0。 它在物理學中被用來描述一個粒子受到大量小分子衝擊的運動，有時也被稱為布朗運動。形式化地表達，一個變量 z 服從維納過程，如果它具有以下兩個性質
""")
st.latex(r"""
\Delta W_t \text{\textasciitilde} \mathcal{N}(0,\Delta t) 
""")
st.info("""
**四個定義**:
1. W(0)=0
2. 增量(△W)彼此獨立
3. 增量(△W)服從常態高斯分佈
4. 連續，但不可微分，鋸齒狀
""")

oneWPLine = getOneWienerProcess()
st.plotly_chart(oneWPLine.fig)
st.dataframe(oneWPLine.df)
st.code("""
time = np.linspace(0,1,11) #生成10步(加上t0=11個t)
sigma = 1 #定義三
WP=[0]  #定義一
dw = np.random.normal(0, scale=sigma, size=10) #產生10個遵循常態分配的隨機增量
for x in range(len(time)-1):
    WP.append(WP[x]+dw[x]) #隨機產生的增量，一期一期加
fig = px.line(WP, markers=True, height=400, width=700, template="plotly_white") #畫圖
""")

st.markdown("""---""")
st.markdown("**產生多條線 - numpy 進階應用**")
c1, c2 = st.columns(2)
with c1:
    steps = st.slider("number of steps", 10, 100, 10, 10)
with c2:
    numberOfSims = st.slider("number of sims", 5, 50, 10, 5)

mulWPLine = getMultWienerProcess(steps, numberOfSims)
st.plotly_chart(mulWPLine.fig)
#st.dataframe(mulWPLine.df)
st.code("""
steps = 3 # number of steps
T = 1 # time in years
numberOfSims = 5 # number of sims
W0 = 0 # initial stock price
dt = T/steps # calc each time step

dw = np.random.normal(0, np.sqrt(dt), size=(steps,numberOfSims))
dw = np.vstack([np.zeros(numberOfSims), dw]) 
Wt = W0 + dw.cumsum(axis=0)

time = np.linspace(0,T,steps+1)
df=pd.DataFrame(Wt, index=time)
fig = px.line(df, height=400, width=500, template="plotly_white").update_layout(showlegend=False)
""")