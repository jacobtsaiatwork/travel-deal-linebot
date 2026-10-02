from typing import Optional, List
from pathlib import Path
from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    PushMessageRequest,
    FlexMessage,
    FlexContainer
)

try:
    from .config import settings, BASE_DIR
    from .store import store, UserSubscription
    from .bot_handler import handler, get_messaging_api
    from .flex_templates import (
        create_main_menu_flex,
        create_deals_carousel_flex,
        create_subscription_flex
    )
except (ImportError, ValueError):
    from config import settings, BASE_DIR
    from store import store, UserSubscription
    from bot_handler import handler, get_messaging_api
    from flex_templates import (
        create_main_menu_flex,
        create_deals_carousel_flex,
        create_subscription_flex
    )

app = FastAPI(
    title="Travel Deals LINE Bot API",
    description="旅遊比價、個人化優惠推播與 LIFF 城市選擇器服務",
    version="1.1.0"
)

# 掛載靜態資源 (供 LIFF 使用)
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

class PreferencePayload(BaseModel):
    user_id: str
    destinations: List[str]
    push_enabled: bool = True

@app.get("/")
async def root():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
      <head><title>旅遊比價 LINE Bot 服務</title><meta charset='utf-8'></head>
      <body style='font-family: sans-serif; text-align: center; padding: 50px; background: #f8fafc;'>
        <h1 style='color: #1e3a8a;'>✈️ 旅遊比價與個人化特惠推播 LINE 機器人</h1>
        <p style='color: #475569;'>服務正常運行中 (Status: Healthy)</p>
        <div style='margin-top: 25px;'>
          <a href='/liff' style='background: #2563eb; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold;'>🌍 開啟 LIFF 視覺化城市選單</a>
          <a href='/docs' style='margin-left: 15px; background: #475569; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold;'>📖 查看 Swagger API 文件</a>
        </div>
      </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mock_mode": settings.is_mock_mode,
        "liff_configured": bool(settings.line_liff_id),
        "destinations_count": len(store.get_deals_data().get("destinations", [])),
        "message": "旅遊比價 LINE Bot 服務正常運行中"
    }

@app.get("/liff")
async def serve_liff():
    """提供 LIFF 手機原生視覺化城市選單頁面"""
    liff_html = BASE_DIR / "static" / "liff" / "index.html"
    if not liff_html.exists():
        liff_html = BASE_DIR / "liff.html"
    if liff_html.exists():
        return FileResponse(str(liff_html))
    raise HTTPException(status_code=404, detail="LIFF HTML not found")

@app.get("/api/liff-config")
async def get_liff_config():
    return {"liff_id": settings.line_liff_id}

@app.get("/api/destinations-tree")
async def get_destinations_tree():
    """回傳按地區分類的目的地樹狀資料"""
    return store.get_regions_and_destinations()

@app.get("/api/user-preferences/{user_id}")
async def get_user_preferences(user_id: str):
    sub = store.get_user_subscription(user_id)
    return sub

@app.post("/api/user-preferences")
async def save_user_preferences(payload: PreferencePayload):
    """LIFF 網頁提交儲存使用者的關注城市與推播設定"""
    sub = store.update_user_preferences(
        user_id=payload.user_id,
        destinations=payload.destinations,
        push_enabled=payload.push_enabled
    )
    return {"status": "success", "subscription": sub}

@app.post("/callback")
async def callback(request: Request, x_line_signature: Optional[str] = Header(None)):
    """LINE 官方 Webhook 入口"""
    body = (await request.body()).decode("utf-8")

    if settings.is_mock_mode:
        print("[Mock Mode] 收到 Webhook 請求 (未驗證簽章)")
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
    """定時推播觸發介面：向訂閱者發送今日特惠"""
    subscribers = store.get_all_subscribers()
    if not subscribers:
        return {"status": "no_subscribers", "message": "目前尚無訂閱用戶"}

    api = get_messaging_api()
    pushed_count = 0
    records = []

    for sub in subscribers:
        if not sub.push_enabled:
            continue

        target_dest_ids = [destination_id] if destination_id else sub.destinations
        target_dests = []
        for d_id in target_dest_ids:
            d = store.find_destination(d_id)
            if d:
                target_dests.append(d)

        if not target_dests:
            continue

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
    text = message.strip().lower()
    store.get_user_subscription(user_id)

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
    elif text in ["訂閱", "設定", "我的訂閱", "推播"]:
        sub = store.get_user_subscription(user_id)
        all_dests = store.get_deals_data().get("destinations", [])
        return {
            "type": "flex",
            "alt_text": "🔔 我的每日推播設定",
            "content": create_subscription_flex(sub.destinations, all_dests)
        }
    elif "已設定的城市比價優惠" in text or "我訂閱的城市優惠" in text:
        sub = store.get_user_subscription(user_id)
        target_dests = [store.find_destination(d_id) for d_id in sub.destinations if store.find_destination(d_id)]
        return {
            "type": "flex",
            "alt_text": "✈️ 您關注的城市最新特惠比價",
            "content": create_deals_carousel_flex(target_dests)
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
            "message": f"未辨識關鍵字「{message}」，可輸入：東京、大阪、曼谷、沖繩、首爾、特惠、選單、訂閱"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
