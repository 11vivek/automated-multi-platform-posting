from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Automated Multi-Platform Posting API"

    # Mastodon
    mastodon_base_url: str = ""
    mastodon_access_token: str = ""

    # Bluesky
    bluesky_identifier: str = ""
    bluesky_app_password: str = ""

    # Telegram: bot must be an administrator of the target channel
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    telegram_channel_username: str = ""

    # Discord incoming webhook URL
    discord_webhook_url: str = ""
    discord_guild_id: str = ""
    discord_channel_id: str = ""

    # WordPress self-hosted site with REST API enabled
    wordpress_site_url: str = ""
    wordpress_username: str = ""
    wordpress_application_password: str = ""
    wordpress_post_title: str = "Automated update"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
