import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import datetime
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="選擇權避險操作模組",
    page_icon="💸",
    layout="wide",
)

# no footer
def no_footer():
    st.markdown("""
    <style>
    .css-9s5bis.edgvbvh3
    {
        visibility: hidden;
    }
    .css-h5rgaw.egzxvld1
    {
        visibility: hidden;
    }
    </style>
    """,unsafe_allow_html=True) #用HTML unsafe_allow_html=True

# 顏色
# st.markdown("""<span style="color:blue">some *blue* text</span>.""",unsafe_allow_html=True)

# 內文
st.header("選擇權避險操作模組")
st.text("still building...")


# 頁尾
c1, c2, c3, c4 = st.columns(4)
c1.info('**Power by: NTUST Option Lab**', icon="💡")
c2.info('**GitHub**', icon="💻")
st.subheader("""使用教學""")
st.markdown("""
    <iframe src="https://docs.google.com/presentation/d/e/2PACX-1vRZLQ5Ty-qFwAkn_TtAhCDLAjLgwKCPoFY30jI9AGsu3Pux9e06w3do4rYY2zZUvYS1tJUmaMaOHsjM/embed?start=false&loop=false&delayms=3000" 
    align="middle" frameborder="0" width="960" height="569" allowfullscreen="true" 
    mozallowfullscreen="true" webkitallowfullscreen="true">
    </iframe>
    """, unsafe_allow_html=True)