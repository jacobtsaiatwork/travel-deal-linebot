# ✈️ 旅遊比價與個人化特惠推播 LINE 機器人 (LINE Bot MVP)

本專案是一個能跨平台比價機票與飯店（支援 **Trip.com、Agoda、Klook、Hotels.com、Expedia、Skyscanner** 等平台），並透過 **LINE 官方帳號每日自動推播個人化折扣資訊** 的後端服務。

---

## 🌟 核心功能

1. **視覺化跨平台比價 (LINE Flex Message)**：
   - 輪播呈現各大目的地之最新機票、熱門星級住宿。
   - 標示歷史降價幅度（如 `🔥 激省 36%`）與各大平台比價價格。
   - 附帶「最低價 ⭐」推薦標籤與直達各平台搶購之分潤連結按鈕。
2. **個人化推播訂閱管理**：
   - 使用者可自由選擇關注的城市（如東京、大阪、曼谷）。
   - 支援快速點擊按鈕進行「訂閱」與「取消訂閱」。
3. **每日優惠排程推播介面**：
   - 提供 `POST /api/push-deals` 端點，可搭配系統 Cron、GitHub Actions 或 Cloud Scheduler 定時向訂閱者發送客製化優惠情報。
4. **內建 Mock 與本地模擬模式**：
   - 即使尚未申請 LINE 帳號，也可直接透過 `/api/simulate-chat` 或測試腳本體驗所有比價邏輯與卡片呈現。

---

## 📁 專案架構

```
travel-deal-linebot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 伺服器主入口 (Webhook & Push API)
│   ├── config.py            # 設定與環境變數管理
│   ├── bot_handler.py       # LINE 訊息/加入好友/按鈕回傳事件處理器
│   ├── flex_templates.py    # LINE Flex Message 視覺化比價卡片範本
│   └── store.py             # 訂閱用戶與比價資料庫管理
├── mock_deals.json          # 旅遊目的地、機票、飯店跨平台比價數據
├── test_local.py            # 本地自動化測試與規範檢查腳本
├── .env.example             # 環境變數設定範例
├── requirements.txt         # 專案依賴套件
└── README.md                # 說明文件
```

---

## 🚀 快速上手教學

### 步驟 1：安裝依賴套件

建議建立虛擬環境或直接使用 pip 安裝：

```bash
pip install -r requirements.txt
```

### 步驟 2：執行本地自動化測試

本測試會檢驗目的地比價讀取、用戶訂閱切換、LINE Flex Message 官方結構合規性以及 FastAPI 各端點：

```bash
python test_local.py
```

### 步驟 3：設定環境變數

複製 `.env.example` 為 `.env`：

```bash
cp .env.example .env
```

若您已有 LINE Developers 帳號，請填入：
- `LINE_CHANNEL_SECRET`
- `LINE_CHANNEL_ACCESS_TOKEN`

*(若暫時留空，系統將自動啟動 Mock 測試模式，不影響伺服器運行)*

### 步驟 4：啟動本地伺服器

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

啟動後可開啟瀏覽器檢視：
- **Swagger API 文件**：`http://localhost:8000/docs`
- **服務健康狀態**：`http://localhost:8000/health`
- **支援目的地與特惠清單**：`http://localhost:8000/api/destinations`

---

## 📱 串接真實 LINE 官方帳號步驟

### 1. 建立 Messaging API Channel
1. 前往 [LINE Developers Console](https://developers.line.biz/) 並登入。
2. 建立一個 **Provider**，並在下方建立一個 **Create a Messaging API channel**。
3. 在 **Basic settings** 分頁取得 `Channel Secret`。
4. 在 **Messaging API** 分頁最下方發行並取得 `Channel Access Token (long-lived)`。
5. 將上述兩串金鑰貼至專案的 `.env` 檔案中。

### 2. 本地埠穿透 (Expose to Internet)
LINE 伺服器需要公開的 HTTPS 網址才能發送 Webhook。推薦使用免費的 `ngrok`：

```bash
ngrok http 8000
```
你會獲得一組網址，例如：`https://abcd-1234.ngrok-free.app`。

### 3. 設定 Webhook URL
1. 回到 LINE Developers 後台的 **Messaging API** 分頁。
2. 將 **Webhook URL** 填入：  
   `https://abcd-1234.ngrok-free.app/callback`
3. 點擊 **Verify** 確認回傳 Success。
4. 開啟 **Use webhook** 開關。
5. 在 **Auto-reply messages** 設定中，將 LINE 官方預設的「自動回覆訊息」**停用 (Disabled)**，避免跟機器人搶回覆。

### 4. 體驗機器人功能
使用 LINE App 掃描 QR Code 加入好友，您可以嘗試傳送：
- `選單`：喚起旅遊比價與優惠雷達主導覽。
- `東京` 或 `大阪` 或 `曼谷`：直接查看該城市機票與飯店在各大平台的價格比較與直達連結。
- `特惠`：瀏覽全網所有熱門旅遊優惠輪播卡片。
- `訂閱`：查看並管理您每日關注的城市推播清單。

---

## ⏰ 如何觸發每日優惠推播？

每日早晨由外部排程發送 HTTP POST 請求給後端：

```bash
# 推播給所有訂閱者他們關注的城市
curl -X POST http://localhost:8000/api/push-deals

# 僅針對訂閱「東京」的用戶推播
curl -X POST "http://localhost:8000/api/push-deals?destination_id=tokyo"
```
系統會自動組裝精美的 Flex Message 輪播卡片發送給對應的用戶！
