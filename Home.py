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

# no footer
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
""",unsafe_allow_html=True)


# 內文
st.header("Option")
st.text("still building...")


# 頁尾
c1, c2 = st.columns(2)
with c1:
    st.info('**Power by: [@tanuki](https://twitter.com/g_dalice)**', icon="💡")
with c2:
    st.info('**GitHub: @tanukifin**', icon="💻")

