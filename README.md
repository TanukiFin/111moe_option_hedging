
https://ntustfinance-option-hedging.streamlit.app/

# 本地啟動
```
streamlit run Home.py
```

# 檔案說明

* Home.py 首頁
* data 放置各式所需的數據，csv檔
* pictures 放置各式所需的圖片，png檔
* pages 其他各頁面
 
![image](https://github.com/TanukiFin/111moe_option_hedging/assets/73293068/a0b7b30c-976b-4997-9ac1-b686b76a1afd)


* myfunction 自己編寫的funtion，方便pages各頁面使用
  * bsmodel.py
    <div align="left">

    | name  | 說明 | input | output |
    | ---------- | -----------| ---------- | -----------|
    | call  | class   | S, K, r, sigma, T | price, delta, gamma, vega, theta, greek   |
    | put   | class   | S, K, r, sigma, T | price, delta, gamma, vega, theta, greek   |
    | get_greeks   | function   | df_St, K_list, CP, r=0.05, sigma=0.3, T=1, steps=20 |   |
    | get_GBM_St   | function   | steps=20, r=0.05, sigma=0.3, T=1 |  |
    | get_default_St   | function   | St_sce, r=0.05, sigma=0.3, T=1, steps=20 | |

    </div>
    
  * hedging.py
    <div align="left">

    | name  | 說明 | input | output |
    | ---------- | -----------| ---------- | -----------|
    | get_delta_hedge  | Delta避險   | df_price, r=0.05, sigma=0.3, T=1, sell_price=3 |  df  |
    | get_delta_hedge_2week   | Delta不同頻率避險   | df_price, freq=2, r=0.05, sigma=0.3, T=1, sell_price=3 |  df  |
    | get_gamma_hedge   | Delta-Gamma避險   | df_price, r=0.05, sigma=0.3, T=1, sell_price=3 | df  |
    | get_vega_hedge   | Delta-Gamma-Vega避險  | df_price, r=0.05, sigma=0.3, T=1, sell_price=3 | df |
    |get_warrent_delta_hedge| 華南永昌權證的Delta避險|df_price|df|
    |get_warrent_gamma_hedge| 華南永昌權證的Delta-Gamma避險|df_price|df|

    </div>


# 參考資料
Streamlit中文教學
[LINK](https://medium.com/@yt.chen/%E6%A9%9F%E5%99%A8%E5%AD%B8%E7%BF%92-%E8%B3%87%E6%96%99%E7%A7%91%E5%AD%B8%E6%A1%86%E6%9E%B6%E6%87%89%E7%94%A8-streamlit%E5%85%A5%E9%96%80-1-d07478cd4d8)

官方語法文件
[LINK](https://docs.streamlit.io/library/api-reference)

部署應用程式
[LINK](https://blog.jiatool.com/posts/streamlit/)



