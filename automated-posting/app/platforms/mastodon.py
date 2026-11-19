from datetime import datetime
from zoneinfo import ZoneInfo
import httpx
from app.config import settings
from app.schemas import PlatformResult
from app.platforms.base import BasePlatform

class MastodonPlatform(BasePlatform):
    name = "Mastodon"

    async def publish(self, message: str) -> PlatformResult:
        if not settings.mastodon_base_url or not settings.mastodon_access_token:
            raise RuntimeError("Mastodon credentials are not configured.")
        base = settings.mastodon_base_url.rstrip("/")
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{base}/api/v1/statuses",
                data={"status": message, "visibility": "public"},
                headers={"Authorization": f"Bearer {settings.mastodon_access_token}"},
            )
            response.raise_for_status()
            data = response.json()
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        return PlatformResult(
            platform=self.name, status="success", posted_url=data.get("url"),
            public_access=data.get("visibility") == "public",
            date=now.date().isoformat(), time=now.strftime("%H:%M:%S")
        )
