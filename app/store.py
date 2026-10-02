import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
try:
    from .config import settings
except (ImportError, ValueError):
    from config import settings

class UserSubscription(BaseModel):
    user_id: str
    destinations: List[str] = ["tokyo", "osaka"]
    push_enabled: bool = True

class DealStore:
    def __init__(self, deals_file: Path, subscribers_file: Optional[Path] = None):
        self.deals_file = deals_file
        self.subscribers_file = subscribers_file or (deals_file.parent / "subscribers.json")
        self._subscribers: Dict[str, UserSubscription] = {}
        self._load_subscribers()

    def _load_subscribers(self):
        if self.subscribers_file.exists():
            try:
                with open(self.subscribers_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for uid, sub in data.items():
                        self._subscribers[uid] = UserSubscription(**sub)
            except Exception as e:
                print(f"[DealStore] 讀取訂閱失敗: {e}")

    def _save_subscribers(self):
        try:
            with open(self.subscribers_file, "w", encoding="utf-8") as f:
                json.dump({k: v.model_dump() for k, v in self._subscribers.items()}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[DealStore] 儲存訂閱失敗: {e}")

    def get_user_subscription(self, user_id: str) -> UserSubscription:
        if user_id not in self._subscribers:
            self._subscribers[user_id] = UserSubscription(user_id=user_id)
            self._save_subscribers()
        return self._subscribers[user_id]

    def update_user_preferences(self, user_id: str, destinations: List[str], push_enabled: bool = True) -> UserSubscription:
        sub = self.get_user_subscription(user_id)
        sub.destinations = destinations
        sub.push_enabled = push_enabled
        self._subscribers[user_id] = sub
        self._save_subscribers()
        return sub

    def subscribe_destination(self, user_id: str, destination_id: str) -> UserSubscription:
        sub = self.get_user_subscription(user_id)
        if destination_id not in sub.destinations:
            sub.destinations.append(destination_id)
            self._save_subscribers()
        return sub

    def unsubscribe_destination(self, user_id: str, destination_id: str) -> UserSubscription:
        sub = self.get_user_subscription(user_id)
        if destination_id in sub.destinations:
            sub.destinations.remove(destination_id)
            self._save_subscribers()
        return sub

    def get_all_subscribers(self) -> List[UserSubscription]:
        return list(self._subscribers.values())

    def get_deals_data(self) -> dict:
        if not self.deals_file.exists():
            return {"destinations": [], "regions": []}
        with open(self.deals_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_regions_and_destinations(self) -> dict:
        data = self.get_deals_data()
        return {
            "regions": data.get("regions", []),
            "destinations": data.get("destinations", [])
        }

    def find_destination(self, keyword: str) -> Optional[dict]:
        data = self.get_deals_data()
        keyword_lower = keyword.strip().lower()
        for dest in data.get("destinations", []):
            if (
                dest["id"].lower() == keyword_lower
                or keyword_lower in dest["name"].lower()
                or keyword_lower in dest["country"].lower()
                or keyword_lower in dest.get("tagline", "").lower()
            ):
                return dest
        return None

store = DealStore(settings.deals_data_path)
