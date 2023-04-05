import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import datetime
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Home",
    page_icon="👋",
)



# 內文
st.header("Option Greeks Hedging")
st.text("still building...")


# 頁尾
c1, c2 = st.columns(2)
with c1:
    st.info('**Power by: NTUST Finance**', icon="💡")
with c2:
    st.info('**GitHub: @tanukifin**', icon="💻")

