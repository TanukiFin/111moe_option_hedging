import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import datetime as dt
import matplotlib.pyplot as plt
import plotly.express as px

api_key="12a476fe-a758-47da-bd31-4c4942430f23"
api_key="d8ae61a9-6d58-491f-9128-7fecaddf0324"
v0_url = "https://api.helius.xyz/v0"
v1_url = "https://api.helius.xyz/v1"

st.set_page_config(
    page_title="BM GBM",
    page_icon="📈",
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
st.text("still building...")