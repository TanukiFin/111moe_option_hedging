# 圖: Delta與現貨應持有量的關係
df_spot = pd.DataFrame()
df_spot["t"] = df_delta["t"]
df_spot["A部位Delta"] = df_price["A_總Delta"]
df_spot["避險部位_現貨持有量"] = df_delta["現貨持有量"]
df_spot["Portfolio_Delta"] = round(df_price["A_總Delta"]+df_delta["現貨持有量"],2)
fig = px.line(df_spot, x="t", y=["A部位Delta","避險部位_現貨持有量","Portfolio_Delta"], title="Delta Hedging Delta與現貨應持有量的關係", \
               labels={"x":"t"},height=400, width=600, template="plotly_white",)
fig.update_layout(legend=dict( orientation="h",
    yanchor="bottom", y=1.02,
    xanchor="right", x=1))
#st.plotly_chart(fig)

# 圖: Delta Hedging 各部位損益
fig = px.line(df_delta.round(2), x="t", y=["A部位損益","現貨部位損益","總損益"], title="Delta Hedging 各部位損益(每期避險)", \
               labels={"value":"profit"},height=400, width=600, template="plotly_white") 
fig.update_layout(legend=dict( orientation="h",
    yanchor="bottom", y=1.02,
    xanchor="right", x=1))
#st.plotly_chart(fig)

# 圖: Delta Hedging 不同頻率的現貨持有量
df_spot = pd.DataFrame()
df_spot["t"] = df_delta["t"]
df_spot["Delta1"] = df_delta["現貨持有量"]
df_spot["Delta2"] = df_delta2["現貨持有量"]
df_spot["Delta5"] = df_delta5["現貨持有量"]
df_spot["Delta10"] = df_delta10["現貨持有量"]
df_spot["Delta20"] = df_delta20["現貨持有量"]
fig = px.line(df_spot, x="t", y=cname[0][1:] , title="Delta Hedging 不同頻率的現貨持有量", \
               labels={"x":"t","value":"現貨持有量"},height=400, width=600, template="plotly_white",)
fig.update_layout(legend=dict( orientation="h",
    yanchor="bottom", y=1.02,
    xanchor="right", x=1))
#st.plotly_chart(fig)