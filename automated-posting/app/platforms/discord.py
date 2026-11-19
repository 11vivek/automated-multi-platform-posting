from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import httpx
from app.config import settings
from app.schemas import PlatformResult
from app.platforms.base import BasePlatform

class DiscordPlatform(BasePlatform):
    name = "Discord"

    async def publish(self, message: str) -> PlatformResult:
        if not settings.discord_webhook_url:
            raise RuntimeError("Discord webhook URL is not configured.")

        # wait=true makes Discord return the created message object, including its ID.
        parts = urlsplit(settings.discord_webhook_url)
        query = dict(parse_qsl(parts.query))
        query["wait"] = "true"
        webhook_url = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                webhook_url,
                json={"content": message, "allowed_mentions": {"parse": []}},
            )
            response.raise_for_status()
            data = response.json()

        channel_id = data.get("channel_id") or settings.discord_channel_id
        guild_id = settings.discord_guild_id
        posted_url = (
            f"https://discord.com/channels/{guild_id}/{channel_id}/{data['id']}"
            if guild_id and channel_id and data.get("id") else None
        )
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        return PlatformResult(
            platform=self.name, status="success", posted_url=posted_url,
            # A Discord server channel is not generally accessible to everyone on the public web.
            public_access=False, date=now.date().isoformat(), time=now.strftime("%H:%M:%S")
        )
