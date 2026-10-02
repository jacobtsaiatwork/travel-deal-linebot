# ✈️ 旅遊比價與個人化特惠推播 LINE 機器人 (Travel Deal Radar)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![LINE Messaging API](https://img.shields.io/badge/LINE-Messaging%20API-00C300.svg)](https://developers.line.biz/)
[![LINE LIFF](https://img.shields.io/badge/LINE-LIFF%20v2-00C300.svg)](https://developers.line.biz/zh-hant/docs/liff/)
[![Deploy to Render](https://img.shields.io/badge/Deploy-Render-black.svg)](https://render.com/)

專為旅遊愛好者設計的智慧比價與推播服務。跨平台即時匯整各大平台（**Trip.com、Agoda、Klook、Hotels.com、Expedia、Skyscanner**）的機票與住宿破盤折扣，結合 **LINE 官方帳號** 與 **LINE LIFF 行動端原生滑出式選單**，提供個人化每日推播！

---

## 🌟 核心功能特色

### 1. 跨平台特惠比價 (LINE Flex Message)
- **視覺化輪播卡片 (Carousel)**：圖文並茂呈現航線、星級住宿、降價幅度（如 `🔥 激省 45%`）與評分。
- **透明價格比對**：卡片內直接列出各大平台即時報價，並標示「⭐ 最低價平台」。
- **直達購買連結**：點擊「前往搶購」按鈕即可直通各平台訂購頁。

### 2. Skyscanner 風格「探索世界各地（查看全網哪裡最便宜）」
- **全網機票最低價排行榜**：彙整所有目的地航線，嚴格依最低價由小到大排序（例如 `🏆 TOP 1 釜山 NT$ 5,800 起`、`🥈 TOP 2 沖繩 NT$ 6,200 起`）。
- **LINE 內一鍵觸發**：在主選單點選「✈️ 探索世界各地 (看哪裡最便宜)」或傳送文字「**哪裡最便宜**」、「**探索世界各地**」、「**機票排行**」，秒速獲得排行輪播卡片！
- **LIFF 整合支援**：
  - 頂部醒目金黃色橫幅按鈕「🌏 探索世界各地」：點擊彈出全網最低價排行榜彈窗。
  - 導覽列「🔥 最低票價排行」按鈕：將所有城市依照機票起價由低至高即時排序，並標註 `TOP 1`、`TOP 2` 標籤。

### 3. LINE LIFF 視覺化城市選擇器 (`/liff`)
- **原生滑出式選單**：在 LINE 內滑出輕量 Vue 3 + Tailwind CSS 單頁應用。
- **5 大地區熱門分類**：
  - 🇹🇼 **台灣在地**：台北、宜蘭礁溪
  - 🇯🇵 **日本精選**：東京、大阪、沖繩、福岡
  - 🇰🇷 **韓國潮流**：首爾、釜山
  - 🌴 **東南亞度假**：曼谷、新加坡
  - ✈️ **歐美長程**：巴黎
- **即時模糊搜尋**：打「沖」、「溫泉」或「首爾」秒速篩選。
- **當下即時比價彈窗**：勾選感興趣的城市點擊儲存，**當下立即彈出全網最殺機票與飯店比價卡片**，附帶搶購連結！
- **雙向同步**：儲存時同步推送比價卡片至 LINE 對話框，並自動排入每日早晨推播。

### 4. 個人化定時推播引擎 (Push API)
- 支援 `POST /api/push-deals` 端點。
- 可搭配系統 Cron、GitHub Actions 或 Cloud Scheduler，每天早晨只為訂閱者推送符合其喜好的特惠情報。

---

## 📁 專案架構目錄

```text
travel-deal-linebot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 核心入口 (Webhook、LIFF 路由、推播 API)
│   ├── config.py            # 環境變數與路徑管理
│   ├── bot_handler.py       # LINE Webhook 事件路由 (Follow、Text、Postback)
│   ├── flex_templates.py    # LINE Flex Message 視覺化比價卡片範本
│   └── store.py             # 訂閱用戶與比價資料庫操作層
├── static/
│   └── liff/
│       └── index.html       # LIFF 行動端視覺化城市選擇器 (Vue 3 + Tailwind)
├── mock_deals.json          # 全球熱門目的地、航線與飯店跨平台比價資料庫
├── test_local.py            # 本地自動化測試 (格式驗證、邏輯測試)
├── Dockerfile               # 容器化建置檔
├── Procfile                 # 雲端平台啟動設定
├── render.yaml              # Render 基礎設施配置
├── requirements.txt         # Python 套件依賴清單
├── .env.example             # 環境變數設定範本
└── README.md                # 專案說明文件
```

---

## ⚙️ 環境變數設定 (`.env`)

| 變數名稱 | 必填 | 說明 | 取得位置 |
| :--- | :---: | :--- | :--- |
| `LINE_CHANNEL_SECRET` | 是 | LINE Messaging API 頻道密鑰 | LINE Developers ➔ Basic settings |
| `LINE_CHANNEL_ACCESS_TOKEN` | 是 | 長期存取權杖 (Long-lived) | LINE Developers ➔ Messaging API |
| `LINE_LIFF_ID` | 選填 | LINE LIFF 應用程式 ID | LINE Developers ➔ LIFF 分頁 |
| `PORT` | 否 | 伺服器連接埠 (預設 `8000`) | 自訂 |
| `APP_ENV` | 否 | 環境模式 (`production` / `development`) | 自訂 |

---

## 🚀 本地開發與測試

### 1. 安裝套件
```bash
pip install -r requirements.txt
```

### 2. 執行自動化測試
本腳本會測試資料庫檢索、訂閱流程、LINE Flex Message 官方規格合規性與 API 端點：
```bash
python test_local.py
```

### 3. 啟動本機伺服器
```bash
python -m uvicorn app.main:app --reload
```
啟動後可在瀏覽器開啟：
- **首頁導航**：`http://localhost:8000/`
- **LIFF 介面預覽**：`http://localhost:8000/liff`
- **Swagger API 文件**：`http://localhost:8000/docs`

---

## ☁️ 雲端部署 (Render) 與 LINE 串接

### 1. 部署到 Render
1. 將專案推上您的 GitHub Repository。
2. 登入 [Render.com](https://render.com/)，點選 **New + ➔ Web Service**。
3. 連結您的 GitHub 專案，在 **Environment Variables** 填入 `LINE_CHANNEL_SECRET`、`LINE_CHANNEL_ACCESS_TOKEN` 與 `LINE_LIFF_ID`。
4. 點擊 **Deploy Web Service**，建置完成後即可獲得永久 HTTPS 網址（例如 `https://travel-deal-linebot-xxxx.onrender.com`）。

### 2. 設定 LINE Webhook
1. 回到 [LINE Developers Console](https://developers.line.biz/) 的 **Messaging API** 分頁。
2. 在 **Webhook URL** 填入：  
   `https://您的Render網址.onrender.com/callback`
3. 點擊 **Verify** 確認回傳 **Success**，並開啟 **Use webhook** 開關。
4. 在 [LINE Official Account Manager](https://manager.line.biz/) ➔ **回應設定**：
   - **Webhook**：開啟
   - **自動回應訊息**：停用 (Disabled)

### 3. 設定 LINE LIFF 原生滑出式選單
1. 在 LINE Developers Console 點進 **LIFF** 分頁 ➔ 點擊 **Add**。
2. **Endpoint URL** 填入：`https://您的Render網址.onrender.com/liff`。
3. **Size** 選擇 **Full**。
4. **Scopes** 勾選 `profile` 與 `openid`。
5. 建立後取得 `LIFF ID`，填入 Render 環境變數的 `LINE_LIFF_ID` 即完成連動！

---

## 📡 API 端點一覽

| 方法 | 路徑 | 說明 |
| :--- | :--- | :--- |
| `GET` | `/` | 系統首頁與功能導覽 |
| `GET` | `/health` | 健康檢查端點 |
| `GET` | `/liff` | LIFF 視覺化城市選擇器網頁 |
| `POST`| `/callback` | LINE Messaging API Webhook 入口 |
| `GET` | `/api/destinations-tree` | 取得按地區分類的目的地樹狀資料 |
| `GET` | `/api/cheapest-flights` | Skyscanner 風格：取得全網所有機票最低價排序清單 |
| `GET` | `/api/user-preferences/{user_id}` | 查詢特定使用者的關注城市與推播設定 |
| `POST`| `/api/user-preferences` | 儲存/更新使用者的關注城市與推播設定 |
| `POST`| `/api/push-deals` | 觸發每日特惠排程推播 |
| `POST`| `/api/simulate-chat` | 本地對話模擬測試端點 |

---

## 📄 License
MIT License
