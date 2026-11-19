from datetime import datetime
from zoneinfo import ZoneInfo
import httpx
from app.config import settings
from app.schemas import PlatformResult
from app.platforms.base import BasePlatform

class BlueskyPlatform(BasePlatform):
    name = "Bluesky"
    PDS = "https://bsky.social"

    async def publish(self, message: str) -> PlatformResult:
        if not settings.bluesky_identifier or not settings.bluesky_app_password:
            raise RuntimeError("Bluesky credentials are not configured.")
        async with httpx.AsyncClient(timeout=25) as client:
            login = await client.post(
                f"{self.PDS}/xrpc/com.atproto.server.createSession",
                json={"identifier": settings.bluesky_identifier, "password": settings.bluesky_app_password},
            )
            login.raise_for_status()
            session = login.json()
            now_utc = datetime.now(ZoneInfo("UTC")).isoformat().replace("+00:00", "Z")
            post = await client.post(
                f"{self.PDS}/xrpc/com.atproto.repo.createRecord",
                headers={"Authorization": f"Bearer {session['accessJwt']}"},
                json={
                    "repo": session["did"],
                    "collection": "app.bsky.feed.post",
                    "record": {"$type": "app.bsky.feed.post", "text": message, "createdAt": now_utc},
                },
            )
            post.raise_for_status()
            result = post.json()
        rkey = result["uri"].rsplit("/", 1)[-1]
        handle = session.get("handle", settings.bluesky_identifier)
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        return PlatformResult(
            platform=self.name, status="success",
            posted_url=f"https://bsky.app/profile/{handle}/post/{rkey}",
            public_access=True, date=now.date().isoformat(), time=now.strftime("%H:%M:%S")
        )
