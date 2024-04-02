from myfunction import bsmodel, hedging
import pandas as pd

# 2種股價取得方式
df_St = bsmodel.get_default_St(St_sce="大漲")
df_St = bsmodel.get_GBM_St(steps=20, r=0.05, sigma=0.3, T=1)

# 計算選擇權價格、Greekes 一次必須三個
df_price = bsmodel.get_greeks(df_St , K_list=[50, 48, 50], CP = ["Call", "Call", "Call"])   

# 計算避險損益 - 模擬數據
df_delta = hedging.get_delta_hedge(df_price, r=0.05, sigma=0.3, T=1, sell_price=8)
df_delta5 = hedging.get_delta_hedge_2week(df_price, freq=5, r=0.05, sigma=0.3, T=1, sell_price=8)
df_delta10 = hedging.get_delta_hedge_2week(df_price, freq=10, r=0.05, sigma=0.3, T=1, sell_price=8)
df_delta20 = hedging.get_delta_hedge_2week(df_price, freq=20, r=0.05, sigma=0.3, T=1, sell_price=8)

# 計算避險損益 - 華南永昌數據
df_St  = pd.read_csv("data/華南永昌案例數據_計算.csv", index_col="Date")
df_St.index = pd.to_datetime(df_St.index)
df_price = bsmodel.get_greeks_vol(df_St, [10000,96000,10000], ["Short Put","Long Put","Long Put"], r=0.01045, sigma=df_St["A_IV"].tolist(), conversion=1)

df_delta = hedging.get_warrent_delta_hedge(df_price)
df_gamma = hedging.get_warrent_gamma_hedge(df_price)

print(df_delta)