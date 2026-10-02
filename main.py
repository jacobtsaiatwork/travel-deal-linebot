from typing import Optional, List
from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    PushMessageRequest,
    FlexMessage,
    FlexContainer
)

try:
    from .config import settings
    from .store import store
    from .bot_handler import handler, get_messaging_api
    from .flex_templates import (
        create_main_menu_flex,
        create_deals_carousel_flex,
        create_subscription_flex
    )
except (ImportError, ValueError):
    from config import settings
    from store import store
    from bot_handler import handler, get_messaging_api
    from flex_templates import (
        create_main_menu_flex,
        create_deals_carousel_flex,
        create_subscription_flex
    )

app = FastAPI(
    title="Travel Deals LINE Bot API",
    description="旅遊比價與個人化每日優惠推播 LINE 機器人服務",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mock_mode": settings.is_mock_mode,
        "message": "旅遊比價 LINE Bot 服務正常運行中"
    }

@app.post("/callback")
async def callback(request: Request, x_line_signature: Optional[str] = Header(None)):
    """LINE 官方 Webhook 入口"""
    body = (await request.body()).decode("utf-8")

    if settings.is_mock_mode:
        print("[Mock Mode] 收到 Webhook 請求 (未驗證簽章)")
        # 在 Mock 模式下仍可印出收到的請求
        return JSONResponse(content={"status": "mock_received"})

    if not x_line_signature:
        raise HTTPException(status_code=400, detail="Missing X-Line-Signature")

    try:
        handler.handle(body, x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        print(f"處理 Webhook 異常: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(content={"status": "success"})

@app.post("/api/push-deals")
async def trigger_daily_push(
    background_tasks: BackgroundTasks,
    destination_id: Optional[str] = None
):
    """
    定時推播觸發介面：向訂閱者發送今日特惠。
    可由外部排程 (如 Cron、Cloud Scheduler) 每日定時呼叫。
    """
    subscribers = store.get_all_subscribers()
    if not subscribers:
        return {"status": "no_subscribers", "message": "目前尚無訂閱用戶"}

    api = get_messaging_api()
    pushed_count = 0
    records = []

    for sub in subscribers:
        if not sub.push_enabled:
            continue

        # 篩選該用戶感興趣的目的地
        target_dest_ids = [destination_id] if destination_id else sub.destinations
        target_dests = []
        for d_id in target_dest_ids:
            d = store.find_destination(d_id)
            if d:
                target_dests.append(d)

        if not target_dests:
            continue

        # 生成比價輪播卡片
        deals_flex = create_deals_carousel_flex(target_dests)

        if api:
            try:
                container = FlexContainer.from_dict(deals_flex)
                api.push_message(
                    PushMessageRequest(
                        to=sub.user_id,
                        messages=[
                            FlexMessage(
                                alt_text="✈️ 您的今日旅遊特惠雷達來囉！",
                                contents=container
                            )
                        ]
                    )
                )
                pushed_count += 1
                records.append({"user_id": sub.user_id, "status": "sent"})
            except Exception as e:
                records.append({"user_id": sub.user_id, "status": "failed", "error": str(e)})
        else:
            # Mock 模式紀錄
            pushed_count += 1
            records.append({
                "user_id": sub.user_id,
                "status": "mock_sent",
                "destinations": [d["name"] for d in target_dests]
            })

    return {
        "status": "completed",
        "mock_mode": settings.is_mock_mode,
        "total_pushed": pushed_count,
        "details": records
    }

@app.get("/api/destinations")
async def list_destinations():
    """查詢當前支援的目的地與最新特惠概況"""
    data = store.get_deals_data()
    summary = []
    for d in data.get("destinations", []):
        summary.append({
            "id": d["id"],
            "name": d["name"],
            "country": d["country"],
            "flight_deal_count": len(d.get("flight_deals", [])),
            "hotel_deal_count": len(d.get("hotel_deals", []))
        })
    return {"destinations": summary}

@app.post("/api/simulate-chat")
async def simulate_chat(message: str, user_id: str = "test_user_001"):
    """
    本地模擬聊天端點：免串接 LINE 即可測試不同文字輸入獲得的 Flex Message 與資料
    """
    text = message.strip().lower()
    store.get_user_subscription(user_id) # 確保有資料

    if text in ["選單", "menu", "主選單", "開始"]:
        return {
            "type": "flex",
            "alt_text": "✈️ 旅遊比價與優惠選單",
            "content": create_main_menu_flex()
        }
    elif text in ["特惠", "優惠", "今日特惠", "今日優惠"]:
        data = store.get_deals_data()
        return {
            "type": "flex",
            "alt_text": "🔥 今日全網熱門旅遊特惠比價",
            "content": create_deals_carousel_flex(data.get("destinations", []))
        }
    elif text in ["訂閱", "設定", "我的訂閱"]:
        sub = store.get_user_subscription(user_id)
        all_dests = store.get_deals_data().get("destinations", [])
        return {
            "type": "flex",
            "alt_text": "🔔 我的每日推播設定",
            "content": create_subscription_flex(sub.destinations, all_dests)
        }
    else:
        dest = store.find_destination(text)
        if dest:
            return {
                "type": "flex",
                "alt_text": f"✈️ {dest['name']} 即時比價優惠",
                "content": create_deals_carousel_flex([dest])
            }
        return {
            "type": "text",
            "message": f"未辨識關鍵字「{message}」，可輸入：東京、大阪、曼谷、特惠、選單、訂閱"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
