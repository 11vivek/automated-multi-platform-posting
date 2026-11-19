from datetime import datetime
from zoneinfo import ZoneInfo
import httpx
from app.config import settings
from app.schemas import PlatformResult
from app.platforms.base import BasePlatform

class TelegramPlatform(BasePlatform):
    name = "Telegram"

    async def publish(self, message: str) -> PlatformResult:
        if not settings.telegram_bot_token or not settings.telegram_chat_id:
            raise RuntimeError("Telegram bot token or chat ID is not configured.")
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
                json={"chat_id": settings.telegram_chat_id, "text": message, "link_preview_options": {"is_disabled": False}},
            )
            response.raise_for_status()
            payload = response.json()
        if not payload.get("ok"):
            raise RuntimeError(payload.get("description", "Telegram API returned an unsuccessful response."))
        msg = payload["result"]
        username = settings.telegram_channel_username.lstrip("@")
        url = f"https://t.me/{username}/{msg['message_id']}" if username else None
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        return PlatformResult(
            platform=self.name, status="success", posted_url=url,
            public_access=bool(username), date=now.date().isoformat(), time=now.strftime("%H:%M:%S")
        )
