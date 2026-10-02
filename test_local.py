import sys
import json
from pathlib import Path

# Windows 控制台 UTF-8 編碼支援
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# 加入當前目錄至 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.store import store
from app.flex_templates import (
    create_main_menu_flex,
    create_deals_carousel_flex,
    create_subscription_flex,
    create_everywhere_carousel_flex
)
from linebot.v3.messaging import FlexContainer

def test_store_and_destinations():
    print("👉 測試 1: 測試旅遊資料庫與目的地搜尋...")
    dests = store.get_deals_data().get("destinations", [])
    assert len(dests) >= 3, f"應至少有 3 個目的地，目前有 {len(dests)}"
    
    # 測試關鍵字搜尋
    tokyo = store.find_destination("東京")
    assert tokyo is not None, "搜尋「東京」應能找到資料"
    assert tokyo["id"] == "tokyo"
    
    bangkok = store.find_destination("bangkok")
    assert bangkok is not None, "搜尋「bangkok」應能找到資料"

    # 測試 Skyscanner 風格機票最低價排序
    ranked_flights = store.get_all_flight_deals_ranked()
    assert len(ranked_flights) >= 5, f"應至少有 5 筆全網機票，目前有 {len(ranked_flights)}"
    for i in range(len(ranked_flights) - 1):
        assert ranked_flights[i]["best_price"] <= ranked_flights[i+1]["best_price"], "機票應由低至高嚴格排序"
    print(f"  ✅ 目的地資料讀取正常，全網共 {len(ranked_flights)} 筆機票最低價排序正常 (No.1: {ranked_flights[0]['destination_name']} NT${ranked_flights[0]['best_price']:,})！")

def test_subscription_flow():
    print("👉 測試 2: 測試用戶個人化訂閱流程...")
    user_id = "test_user_line_123"
    
    # 預設訂閱
    sub = store.get_user_subscription(user_id)
    assert user_id == sub.user_id
    
    # 新增訂閱
    sub = store.subscribe_destination(user_id, "osaka")
    assert "osaka" in sub.destinations, "大阪應已被訂閱"
    
    # 取消訂閱
    sub = store.unsubscribe_destination(user_id, "osaka")
    assert "osaka" not in sub.destinations, "大阪應已被取消訂閱"
    print("  ✅ 個人化訂閱管理儲存與狀態切換正常！")

def test_flex_templates_validation():
    print("👉 測試 3: 驗證 LINE Flex Message 語法與官方規範...")
    all_dests = store.get_deals_data().get("destinations", [])
    
    # 1. 主選單
    menu_flex = create_main_menu_flex()
    c1 = FlexContainer.from_dict(menu_flex)
    assert c1 is not None
    print("  ✅ 主選單 Flex Message 合規")

    # 2. 比價輪播卡片 (Carousel)
    carousel_flex = create_deals_carousel_flex(all_dests)
    c2 = FlexContainer.from_dict(carousel_flex)
    assert c2 is not None
    assert len(carousel_flex["contents"]) > 0
    print(f"  ✅ 比價輪播卡片 (共 {len(carousel_flex['contents'])} 張比價 Bubble) 合規")

    # 3. 探索世界各地 (Skyscanner 風格全網最低價排行輪播卡片)
    ranked = store.get_all_flight_deals_ranked()
    everywhere_flex = create_everywhere_carousel_flex(ranked)
    c_everywhere = FlexContainer.from_dict(everywhere_flex)
    assert c_everywhere is not None
    assert len(everywhere_flex["contents"]) > 0
    print(f"  ✅ 探索世界各地 (全網最低排行，共 {len(everywhere_flex['contents'])} 張卡片) Flex Message 合規")

    # 4. 訂閱管理卡片
    sub_flex = create_subscription_flex(["tokyo"], all_dests)
    c3 = FlexContainer.from_dict(sub_flex)
    assert c3 is not None
    print("  ✅ 訂閱管理 Flex Message 合規")

def test_api_endpoints():
    print("👉 測試 4: 測試 FastAPI 端點與模擬聊天...")
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    
    # 健康檢查
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
    
    # 目的地清單
    resp = client.get("/api/destinations")
    assert resp.status_code == 200
    assert len(resp.json()["destinations"]) >= 3

    # Skyscanner 最低價機票清單
    resp = client.get("/api/cheapest-flights")
    assert resp.status_code == 200
    cheapest_data = resp.json()
    assert cheapest_data["total"] >= 5
    assert cheapest_data["flights"][0]["best_price"] <= cheapest_data["flights"][1]["best_price"]
    print("  ✅ /api/cheapest-flights 端點測試正常")
    
    # 模擬聊天：查詢「東京」
    resp = client.post("/api/simulate-chat?message=東京")
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "flex"
    assert "東京" in data["alt_text"]

    # 模擬聊天：查詢「探索世界各地」
    resp = client.post("/api/simulate-chat?message=探索世界各地")
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "flex"
    assert "探索世界各地" in data["alt_text"]

    # 模擬聊天：查詢「哪裡最便宜」
    resp = client.post("/api/simulate-chat?message=哪裡最便宜")
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "flex"
    assert "全網最低" in data["alt_text"]
    
    # 模擬推播觸發
    resp = client.post("/api/push-deals")
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"

    # 測試 LIFF 相關端點
    resp = client.get("/liff")
    assert resp.status_code == 200
    assert "旅遊目的地探索" in resp.text

    resp = client.get("/api/destinations-tree")
    assert resp.status_code == 200
    tree = resp.json()
    assert len(tree["regions"]) >= 4
    assert len(tree["destinations"]) >= 8

    # 測試儲存偏好
    resp = client.post("/api/user-preferences", json={
        "user_id": "test_liff_user",
        "destinations": ["tokyo", "seoul", "okinawa"],
        "push_enabled": True
    })
    assert resp.status_code == 200
    assert len(resp.json()["subscription"]["destinations"]) == 3
    print("  ✅ 所有 FastAPI API 端點、LIFF 前端與推播模擬測試通過！")

if __name__ == "__main__":
    print("========== 開始執行 LINE Bot 本地測試 ==========")
    test_store_and_destinations()
    test_subscription_flow()
    test_flex_templates_validation()
    test_api_endpoints()
    print("==================================================")
    print("🎉 全部 4 項核心測試均順利通過！系統可正常啟動與部署！")
