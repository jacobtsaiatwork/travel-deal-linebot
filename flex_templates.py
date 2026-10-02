from typing import Any, Dict, List

def create_main_menu_flex() -> Dict[str, Any]:
    """主功能選單 Flex Message"""
    return {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#1E3A8A",
            "paddingAll": "20px",
            "contents": [
                {
                    "type": "text",
                    "text": "✈️ 旅遊比價與優惠雷達",
                    "weight": "bold",
                    "color": "#FFFFFF",
                    "size": "xl"
                },
                {
                    "type": "text",
                    "text": "即時匯整各大平台機票與住宿最殺折扣",
                    "color": "#93C5FD",
                    "size": "xs",
                    "margin": "sm"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "支援平台：Trip.com · Agoda · Klook · Expedia · Skyscanner",
                    "size": "xxs",
                    "color": "#6B7280",
                    "wrap": True
                },
                {"type": "separator"},
                {
                    "type": "text",
                    "text": "請選擇您想查詢的熱門旅遊地：",
                    "weight": "bold",
                    "size": "sm",
                    "color": "#374151"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "secondary",
                            "height": "sm",
                            "color": "#F3F4F6",
                            "action": {
                                "type": "postback",
                                "label": "🗼 東京比價",
                                "data": "action=view_deals&dest=tokyo",
                                "displayText": "查詢東京最優惠方案"
                            }
                        },
                        {
                            "type": "button",
                            "style": "secondary",
                            "height": "sm",
                            "color": "#F3F4F6",
                            "action": {
                                "type": "postback",
                                "label": "🏯 大阪比價",
                                "data": "action=view_deals&dest=osaka",
                                "displayText": "查詢大阪最優惠方案"
                            }
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "secondary",
                            "height": "sm",
                            "color": "#F3F4F6",
                            "action": {
                                "type": "postback",
                                "label": "🐘 曼谷比價",
                                "data": "action=view_deals&dest=bangkok",
                                "displayText": "查詢曼谷最優惠方案"
                            }
                        },
                        {
                            "type": "button",
                            "style": "secondary",
                            "height": "sm",
                            "color": "#F3F4F6",
                            "action": {
                                "type": "postback",
                                "label": "🔥 全網特惠",
                                "data": "action=view_deals&dest=all",
                                "displayText": "查看今日全網特惠"
                            }
                        }
                    ]
                },
                {"type": "separator"},
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#2563EB",
                    "height": "sm",
                    "action": {
                        "type": "postback",
                        "label": "🔔 管理我的每日推播設定",
                        "data": "action=my_subscriptions",
                        "displayText": "查看我的訂閱設定"
                    }
                }
            ]
        }
    }

def _build_flight_bubble(deal: dict, dest_name: str, dest_id: str) -> dict:
    """單張機票比價卡片 Bubble"""
    comparisons_contents = []
    for comp in deal.get("comparisons", []):
        comparisons_contents.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": f"{'⭐ ' if comp['is_best'] else '   '}{comp['platform']}",
                    "size": "xs",
                    "color": "#1F2937" if comp['is_best'] else "#6B7280",
                    "weight": "bold" if comp['is_best'] else "regular",
                    "flex": 6
                },
                {
                    "type": "text",
                    "text": f"NT$ {comp['price']:,}",
                    "size": "xs",
                    "color": "#DC2626" if comp['is_best'] else "#4B5563",
                    "weight": "bold" if comp['is_best'] else "regular",
                    "align": "end",
                    "flex": 4
                }
            ]
        })

    return {
        "type": "bubble",
        "size": "kilo",
        "hero": {
            "type": "image",
            "url": deal.get("image_url", "https://images.unsplash.com/photo-1503899036084-c55cdd92da26"),
            "size": "full",
            "aspectRatio": "16:9",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": "✈️ 超值機票",
                            "weight": "bold",
                            "color": "#2563EB",
                            "size": "xxs",
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": f"🔥 激省 {deal.get('discount_percent', 0)}%",
                            "weight": "bold",
                            "color": "#DC2626",
                            "size": "xxs",
                            "align": "end"
                        }
                    ]
                },
                {
                    "type": "text",
                    "text": deal.get("title", ""),
                    "weight": "bold",
                    "size": "sm",
                    "wrap": True,
                    "maxLines": 2
                },
                {
                    "type": "text",
                    "text": f"航司：{deal.get('airline', '')}\n日期：{deal.get('dates', '')}",
                    "size": "xxs",
                    "color": "#6B7280",
                    "wrap": True
                },
                {"type": "separator", "margin": "sm"},
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "sm",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"NT$ {deal.get('best_price', 0):,}",
                            "size": "lg",
                            "color": "#DC2626",
                            "weight": "bold",
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": f"NT$ {deal.get('original_price', 0):,}",
                            "size": "xs",
                            "color": "#9CA3AF",
                            "decoration": "line-through",
                            "align": "start",
                            "margin": "sm",
                            "gravity": "bottom"
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#F9FAFB",
                    "cornerRadius": "md",
                    "paddingAll": "8px",
                    "spacing": "xs",
                    "margin": "sm",
                    "contents": comparisons_contents
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#DC2626",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": f"👉 前往 {deal.get('best_platform', '訂購')} 搶購",
                        "uri": deal.get("booking_url", "https://tw.trip.com")
                    }
                },
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "postback",
                        "label": f"🔔 訂閱 {dest_name} 每日優惠",
                        "data": f"action=subscribe&dest={dest_id}",
                        "displayText": f"我想訂閱 {dest_name} 每日推播"
                    }
                }
            ]
        }
    }

def _build_hotel_bubble(deal: dict, dest_name: str, dest_id: str) -> dict:
    """單間飯店比價卡片 Bubble"""
    comparisons_contents = []
    for comp in deal.get("comparisons", []):
        comparisons_contents.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": f"{'⭐ ' if comp['is_best'] else '   '}{comp['platform']}",
                    "size": "xs",
                    "color": "#1F2937" if comp['is_best'] else "#6B7280",
                    "weight": "bold" if comp['is_best'] else "regular",
                    "flex": 6
                },
                {
                    "type": "text",
                    "text": f"NT$ {comp['price']:,}",
                    "size": "xs",
                    "color": "#059669" if comp['is_best'] else "#4B5563",
                    "weight": "bold" if comp['is_best'] else "regular",
                    "align": "end",
                    "flex": 4
                }
            ]
        })

    return {
        "type": "bubble",
        "size": "kilo",
        "hero": {
            "type": "image",
            "url": deal.get("image_url", "https://images.unsplash.com/photo-1540541338287-41700207dee6"),
            "size": "full",
            "aspectRatio": "16:9",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🏨 優惠住宿",
                            "weight": "bold",
                            "color": "#059669",
                            "size": "xxs",
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": f"🔥 激省 {deal.get('discount_percent', 0)}%",
                            "weight": "bold",
                            "color": "#DC2626",
                            "size": "xxs",
                            "align": "end"
                        }
                    ]
                },
                {
                    "type": "text",
                    "text": deal.get("title", ""),
                    "weight": "bold",
                    "size": "sm",
                    "wrap": True,
                    "maxLines": 2
                },
                {
                    "type": "text",
                    "text": f"評價：{deal.get('rating', '')}\n區域：{deal.get('area', '')}",
                    "size": "xxs",
                    "color": "#6B7280",
                    "wrap": True
                },
                {"type": "separator", "margin": "sm"},
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "sm",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"NT$ {deal.get('best_price', 0):,}",
                            "size": "lg",
                            "color": "#059669",
                            "weight": "bold",
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": "/ 晚起",
                            "size": "xxs",
                            "color": "#6B7280",
                            "gravity": "bottom",
                            "margin": "xs"
                        },
                        {
                            "type": "text",
                            "text": f"NT$ {deal.get('original_price', 0):,}",
                            "size": "xs",
                            "color": "#9CA3AF",
                            "decoration": "line-through",
                            "align": "end",
                            "margin": "sm",
                            "gravity": "bottom"
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#F9FAFB",
                    "cornerRadius": "md",
                    "paddingAll": "8px",
                    "spacing": "xs",
                    "margin": "sm",
                    "contents": comparisons_contents
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#059669",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": f"👉 前往 {deal.get('best_platform', '訂房')} 搶購",
                        "uri": deal.get("booking_url", "https://www.agoda.com")
                    }
                },
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "postback",
                        "label": f"🔔 訂閱 {dest_name} 每日推播",
                        "data": f"action=subscribe&dest={dest_id}",
                        "displayText": f"我想訂閱 {dest_name} 每日推播"
                    }
                }
            ]
        }
    }

def create_deals_carousel_flex(destinations_data: List[dict]) -> Dict[str, Any]:
    """生成優惠比價輪播卡片 (Carousel)"""
    bubbles = []
    for dest in destinations_data:
        dest_name = dest.get("name", "")
        dest_id = dest.get("id", "")
        for flight in dest.get("flight_deals", []):
            bubbles.append(_build_flight_bubble(flight, dest_name, dest_id))
        for hotel in dest.get("hotel_deals", []):
            bubbles.append(_build_hotel_bubble(hotel, dest_name, dest_id))

    # LINE Carousel 上限為 12 個 Bubble
    return {
        "type": "carousel",
        "contents": bubbles[:10]
    }

def create_subscription_flex(current_subscriptions: List[str], all_destinations: List[dict]) -> Dict[str, Any]:
    """個人化訂閱設定管理 Flex Message"""
    dest_buttons = []
    for dest in all_destinations:
        d_id = dest["id"]
        d_name = dest["name"]
        is_subbed = d_id in current_subscriptions
        
        dest_buttons.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "alignItems": "center",
            "contents": [
                {
                    "type": "text",
                    "text": f"{'✅ 已訂閱' if is_subbed else '⬜ 未訂閱'} {d_name}",
                    "size": "sm",
                    "color": "#1F2937" if is_subbed else "#6B7280",
                    "weight": "bold" if is_subbed else "regular",
                    "flex": 7
                },
                {
                    "type": "button",
                    "style": "secondary" if is_subbed else "primary",
                    "color": "#EF4444" if is_subbed else "#2563EB",
                    "height": "sm",
                    "flex": 3,
                    "action": {
                        "type": "postback",
                        "label": "退訂" if is_subbed else "訂閱",
                        "data": f"action={'unsubscribe' if is_subbed else 'subscribe'}&dest={d_id}",
                        "displayText": f"{'取消訂閱' if is_subbed else '訂閱'} {d_name}"
                    }
                }
            ]
        })

    return {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#2563EB",
            "paddingAll": "16px",
            "contents": [
                {
                    "type": "text",
                    "text": "🔔 每日旅遊優惠推播設定",
                    "weight": "bold",
                    "color": "#FFFFFF",
                    "size": "lg"
                },
                {
                    "type": "text",
                    "text": "系統將於每日早晨推播您關注城市的最新特惠與降價情報",
                    "color": "#BFDBFE",
                    "size": "xs",
                    "wrap": True,
                    "margin": "xs"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "點選下方按鈕即可快速開關訂閱：",
                    "size": "xs",
                    "color": "#6B7280"
                },
                {"type": "separator"},
                *dest_buttons
            ]
        }
    }
