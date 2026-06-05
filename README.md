# 金融工具作業

這份專案是由原本的 GDP dashboard template 改成「金融工具作業：量化交易初探」期末展示版本。

## 專題重點

- 用 Python 模擬規則化交易，對應課堂中的清單、迴圈、判斷與條件中斷。
- 可使用內建示範股價，也可上傳歷史股價 CSV。
- 交易策略包含短期/長期均線、止盈、止損與分批進場。
- 頁面會顯示資產曲線、買賣點、交易紀錄、勝率、最大回撤與最終資產。

## CSV 格式

上傳 CSV 至少需要日期與收盤價欄位：

```csv
Date,Close,Volume
2026-01-02,620,42000000
2026-01-03,628,39000000
```

也支援中文欄位名稱：`日期`、`收盤價`、`成交量`。資料夾內已附一份 `data/sample_stock_prices.csv` 可用來測試上傳功能。

## 本機執行

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Streamlit Cloud 部署

1. 將此資料夾內容上傳到 GitHub repository。
2. Streamlit Cloud 選擇該 repository。
3. Main file path 設定為 `streamlit_app.py`。
4. 確認 `requirements.txt` 在 repository 根目錄。

## 資料存放與相容性

- 內建示範資料由程式產生，部署到雲端後不依賴本機檔案。
- `data/sample_stock_prices.csv` 是可上傳測試資料，可一起放在 GitHub repository。
- 使用者上傳的 CSV 只存在當次瀏覽器 session，不會寫入伺服器硬碟，適合 Streamlit Cloud 的臨時執行環境。
- 介面使用 Streamlit 原生元件與 Plotly 圖表，可在手機、平板、筆電與桌機瀏覽器開啟。

## 原問題紀錄

原本 repository 是 Streamlit 的 GDP 範例模板。若部署後出現「有背景但沒有內容」，常見原因是主程式仍停留在模板、套件未安裝完整、入口檔設定錯誤，或頁面內容被樣式蓋住。此版本已改為固定入口檔 `streamlit_app.py`，並補上頁面內容、資料 fallback 與必要套件。
