import urllib.parse
from typing import Optional
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    PushMessageRequest,
    FlexMessage,
    FlexContainer,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent,
    FollowEvent
)

try:
    from .config import settings
    from .store import store
    from .flex_templates import (
        create_main_menu_flex,
        create_deals_carousel_flex,
        create_subscription_flex
    )
except (ImportError, ValueError):
    from config import settings
    from store import store
    from flex_templates import (
        create_main_menu_flex,
        create_deals_carousel_flex,
        create_subscription_flex
    )

# 初始化 LINE SDK
handler = WebhookHandler(settings.line_channel_secret or "mock_secret")

def get_messaging_api() -> Optional[MessagingApi]:
    if settings.is_mock_mode:
        return None
    config = Configuration(access_token=settings.line_channel_access_token)
    api_client = ApiClient(config)
    return MessagingApi(api_client)

def reply_flex(reply_token: str, alt_text: str, flex_content: dict):
    """回傳 Flex 訊息"""
    api = get_messaging_api()
    if not api:
        print(f"[Mock Mode] 回覆 Flex: {alt_text}\n內容摘要: {flex_content.get('type')}")
        return

    try:
        container = FlexContainer.from_dict(flex_content)
        api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[FlexMessage(alt_text=alt_text, contents=container)]
            )
        )
    except Exception as e:
        print(f"[LINE API Error] reply_flex 失敗: {e}")

def reply_text(reply_token: str, text: str):
    """回傳純文字訊息"""
    api = get_messaging_api()
    if not api:
        print(f"[Mock Mode] 回覆純文字: {text}")
        return

    try:
        api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=text)]
            )
        )
    except Exception as e:
        print(f"[LINE API Error] reply_text 失敗: {e}")

# 註冊事件處理器
@handler.add(FollowEvent)
def handle_follow(event: FollowEvent):
    """當使用者加入好友時觸發"""
    user_id = event.source.user_id
    print(f"新用戶加入好友: {user_id}")
    # 初始化預設訂閱
    store.get_user_subscription(user_id)
    menu_flex = create_main_menu_flex()
    reply_flex(event.reply_token, "歡迎使用旅遊比價與優惠雷達！", menu_flex)

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event: MessageEvent):
    """處理使用者傳送的文字指令"""
    text = event.message.text.strip().lower()
    user_id = event.source.user_id

    # 1. 查詢主選單
    if text in ["選單", "menu", "主選單", "開始", "help", "指南"]:
        menu_flex = create_main_menu_flex()
        reply_flex(event.reply_token, "✈️ 旅遊比價與優惠選單", menu_flex)
        return

    # 2. 查詢今日全網優惠
    if text in ["特惠", "優惠", "今日特惠", "今日優惠", "deals", "促銷"]:
        data = store.get_deals_data()
        deals_flex = create_deals_carousel_flex(data.get("destinations", []))
        reply_flex(event.reply_token, "🔥 今日全網熱門旅遊特惠比價", deals_flex)
        return

    # 3. 查看個人化訂閱
    if text in ["訂閱", "我的訂閱", "設定", "推播", "推播設定"]:
        sub = store.get_user_subscription(user_id)
        all_dests = store.get_deals_data().get("destinations", [])
        sub_flex = create_subscription_flex(sub.destinations, all_dests)
        reply_flex(event.reply_token, "🔔 我的每日推播設定", sub_flex)
        return

    # 4. 關鍵字目的地搜尋（如：東京、曼谷、大阪）
    matched_dest = store.find_destination(text)
    if matched_dest:
        deals_flex = create_deals_carousel_flex([matched_dest])
        reply_flex(event.reply_token, f"✈️ {matched_dest['name']} 即時比價優惠", deals_flex)
        return

    # 5. 無法辨識時的友善回覆
    reply_text(
        event.reply_token,
        f"抱歉，我暫時找不到「{event.message.text}」的即時優惠。\n\n"
        "💡 您可以輸入：\n"
        "• 輸入「東京」、「大阪」或「曼谷」查看當地最新比價\n"
        "• 輸入「特惠」查看全網精選最殺折扣\n"
        "• 輸入「選單」開啟完整功能列表"
    )

@handler.add(PostbackEvent)
def handle_postback(event: PostbackEvent):
    """處理 Flex Message 按鈕回傳事件"""
    user_id = event.source.user_id
    query_params = dict(urllib.parse.parse_qsl(event.postback.data))
    action = query_params.get("action")
    dest_id = query_params.get("dest")

    all_dests = store.get_deals_data().get("destinations", [])

    if action == "view_deals":
        if dest_id == "all":
            deals_flex = create_deals_carousel_flex(all_dests)
            reply_flex(event.reply_token, "🔥 今日全網最殺旅遊比價", deals_flex)
        else:
            dest = store.find_destination(dest_id)
            if dest:
                deals_flex = create_deals_carousel_flex([dest])
                reply_flex(event.reply_token, f"✈️ {dest['name']} 比價優惠", deals_flex)

    elif action == "subscribe":
        sub = store.subscribe_destination(user_id, dest_id)
        dest = store.find_destination(dest_id)
        dest_name = dest["name"] if dest else dest_id
        # 回傳更新後的訂閱卡片
        sub_flex = create_subscription_flex(sub.destinations, all_dests)
        reply_flex(event.reply_token, f"✅ 已成功訂閱 {dest_name} 每日推播！", sub_flex)

    elif action == "unsubscribe":
        sub = store.unsubscribe_destination(user_id, dest_id)
        dest = store.find_destination(dest_id)
        dest_name = dest["name"] if dest else dest_id
        # 回傳更新後的訂閱卡片
        sub_flex = create_subscription_flex(sub.destinations, all_dests)
        reply_flex(event.reply_token, f"❌ 已取消訂閱 {dest_name}！", sub_flex)

    elif action == "my_subscriptions":
        sub = store.get_user_subscription(user_id)
        sub_flex = create_subscription_flex(sub.destinations, all_dests)
        reply_flex(event.reply_token, "🔔 我的每日推播設定", sub_flex)
