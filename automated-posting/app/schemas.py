from pydantic import BaseModel, Field, field_validator, model_validator
from urllib.parse import urlparse
import re

class PostingRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=200, description="Message containing exactly one CTA URL")

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be empty.")
        urls = re.findall(r'https?://[^\s<>"\']+', value)
        if len(urls) != 1:
            raise ValueError("Message must contain exactly one CTA link.")
        parsed = urlparse(urls[0].rstrip(".,);]"))
        if parsed.scheme not in ("http", "https") or not parsed.netloc or "." not in parsed.netloc:
            raise ValueError("CTA link must be a valid http or https URL.")
        # Reject malformed URL-like fragments and ensure the URL is the only CTA.
        return value

class PlatformResult(BaseModel):
    platform: str
    status: str
    posted_url: str | None = None
    public_access: bool = False
    date: str | None = None
    time: str | None = None
    error: str | None = None

class PostingResponse(BaseModel):
    success: bool
    results: list[PlatformResult]
