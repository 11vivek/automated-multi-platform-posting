from datetime import datetime
from zoneinfo import ZoneInfo
import asyncio
from app.schemas import PlatformResult
from app.platforms.mastodon import MastodonPlatform
from app.platforms.bluesky import BlueskyPlatform
from app.platforms.telegram import TelegramPlatform
from app.platforms.discord import DiscordPlatform
from app.platforms.wordpress import WordPressPlatform

PLATFORMS = [
    MastodonPlatform(),
    BlueskyPlatform(),
    TelegramPlatform(),
    DiscordPlatform(),
    WordPressPlatform(),
]

async def publish_to_one(platform, message: str) -> PlatformResult:
    try:
        return await platform.publish(message)
    except Exception as exc:
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        # Keep the error useful without exposing tokens or webhook URLs.
        detail = str(exc)
        if len(detail) > 300:
            detail = detail[:297] + "..."
        return PlatformResult(
            platform=platform.name, status="failed", posted_url=None,
            public_access=False, date=now.date().isoformat(),
            time=now.strftime("%H:%M:%S"), error=detail or exc.__class__.__name__
        )

async def publish_to_all(message: str) -> list[PlatformResult]:
    # Each integration is isolated. One failure never stops the others.
    return await asyncio.gather(*(publish_to_one(p, message) for p in PLATFORMS))
