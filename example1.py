from myfunction import bsmodel, hedging

df_St = bsmodel.get_default_St(St_sce="大漲")
df_price = bsmodel.get_greeks(df_St , K_list=[50, 48, 50], CP = ["Call", "Call", "Call"])   
df_delta = hedging.get_delta_hedge(df_price, r=0.05, sigma=0.3, T=1, sell_price=8)

print(df_delta)