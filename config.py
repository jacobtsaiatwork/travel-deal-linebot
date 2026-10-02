import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# 若在 app/ 子目錄則取上一層，若在根目錄則取當前目錄
BASE_DIR = Path(__file__).resolve().parent
if BASE_DIR.name == "app":
    BASE_DIR = BASE_DIR.parent
load_dotenv(BASE_DIR / ".env")

class Settings(BaseModel):
    line_channel_id: str = os.getenv("LINE_CHANNEL_ID", "")
    line_channel_secret: str = os.getenv("LINE_CHANNEL_SECRET", "")
    line_channel_access_token: str = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    port: int = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "0.0.0.0")
    app_env: str = os.getenv("APP_ENV", "development")
    deals_data_path: Path = BASE_DIR / "mock_deals.json"

    @property
    def is_mock_mode(self) -> bool:
        """若未設定 LINE 金鑰，自動啟用 Mock 模式供本地端測試"""
        return (
            not self.line_channel_secret
            or self.line_channel_secret == "your_channel_secret_here"
            or not self.line_channel_access_token
            or self.line_channel_access_token == "your_channel_access_token_here"
        )

settings = Settings()
