
https://ntustfinance-option-hedging.streamlit.app/
* 若發生錯誤，可嘗試重整同一頁面

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

  <div align="left">
   
  | 頁碼  | 名稱 | 內容 | 
  | ---------- | -----------| ---------- | 
  | 1  | Greek Letters  | 觀察隨著時間t、股價St變化，Greeks的變化 |
  | 2   | Delta Hedging - Example   | 透過預設的股價情境，觀察不同避險方式的結果 |
  | 3   | Delta Hedging - GBM   | 隨機模擬一條股價路徑，觀察不同避險方式的結果 | 
  | 4   | 績效指標   | 隨機多條股價路徑，觀察不同避險方式的統計結果(平均、標準差等) | 
  | 5   | Delta-Gamma Hedging   | 隨機模擬一條股價路徑，調整避險B選擇權的參數，觀察Delta-Gamma避險結果 |
  | 6   | 華南永昌案例背景   | 當時市場情況的數據 |
  | 7   | 華南永昌模擬避險   | 模擬Delta、Delta-Gamma避險產生的結果 |
   
  </div>

* myfunction 自己編寫的funtion，方便pages各頁面使用
  * bsmodel.py
    <div align="left">

    | name  | 說明 | input | output |
    | ---------- | -----------| ---------- | -----------|
    | call  | class   | S, K, r, sigma, T | price, delta, gamma, vega, theta, greek   |
    | put   | class   | S, K, r, sigma, T | price, delta, gamma, vega, theta, greek   |
    | get_greeks   | 模擬資料使用(p1~5)   | df_St, K_list, CP, r=0.05, sigma=0.3, T=1, steps=20 | A、B、C三個選擇權的Delta、Gamma、Vega、Theta | 
    | get_greeks_vol  | 可調整sigma，華南永昌案例使用(6,7)    | df_St, K_list, CP, r=0.05, sigma=0.3, T=1, steps=20 |  A、B、C三個選擇權的Delta、Gamma、Vega、Theta |
    | get_GBM_St   | 根據輸入參數，用GBM模型隨機模擬股價   | steps=20, r=0.05, sigma=0.3, T=1 | t, St |
    | get_default_St   | 選擇情境，返回預設好的股價   | St_sce, T=1, steps=20 | t, St  | 

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


# 流程圖

![image](https://raw.githubusercontent.com/TanukiFin/111moe_option_hedging/main/pictures/1.png)

![image](https://raw.githubusercontent.com/TanukiFin/111moe_option_hedging/main/pictures/2%203.png)

![image](https://raw.githubusercontent.com/TanukiFin/111moe_option_hedging/main/pictures/5.png)


# 參考資料
Streamlit中文教學
[LINK](https://medium.com/@yt.chen/%E6%A9%9F%E5%99%A8%E5%AD%B8%E7%BF%92-%E8%B3%87%E6%96%99%E7%A7%91%E5%AD%B8%E6%A1%86%E6%9E%B6%E6%87%89%E7%94%A8-streamlit%E5%85%A5%E9%96%80-1-d07478cd4d8)

官方語法文件
[LINK](https://docs.streamlit.io/library/api-reference)

部署應用程式
[LINK](https://blog.jiatool.com/posts/streamlit/)



