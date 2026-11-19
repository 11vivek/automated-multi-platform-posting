from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urljoin
import httpx
from app.config import settings
from app.schemas import PlatformResult
from app.platforms.base import BasePlatform

class WordPressPlatform(BasePlatform):
    name = "WordPress"

    async def publish(self, message: str) -> PlatformResult:
        if not settings.wordpress_site_url or not settings.wordpress_username or not settings.wordpress_application_password:
            raise RuntimeError("WordPress site URL, username, or application password is not configured.")
        base = settings.wordpress_site_url.rstrip("/") + "/"
        endpoint = urljoin(base, "wp-json/wp/v2/posts")
        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.post(
                endpoint,
                auth=(settings.wordpress_username, settings.wordpress_application_password.replace(" ", "")),
                json={"title": settings.wordpress_post_title, "content": message, "status": "publish"},
            )
            response.raise_for_status()
            data = response.json()
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        return PlatformResult(
            platform=self.name, status="success", posted_url=data.get("link"),
            public_access=data.get("status") == "publish",
            date=now.date().isoformat(), time=now.strftime("%H:%M:%S")
        )
