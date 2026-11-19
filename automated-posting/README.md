# Automated Multi-Platform Posting System

FastAPI service that accepts one message (maximum 200 characters, exactly one valid CTA URL) and attempts to publish it independently to five configured destinations: Mastodon, Bluesky, Telegram, Discord, and WordPress.

## Important implementation notes

- The required endpoint is `POST /posting` on port `4000`.
- The platform list is internal; clients cannot select destinations.
- Each integration is isolated. A failed destination does not stop the others.
- Missing credentials are reported as `failed` for that platform. This is expected until you configure the account.
- `success` means at least one platform accepted the post; inspect each result for per-platform outcome.
- Telegram returns a public post URL only when a public channel username is configured. A private chat is not publicly accessible.
- Discord messages are not assumed to be publicly accessible. The response uses `public_access: false`; the configured channel URL is returned when its IDs are provided.
- Dates/times in results are recorded in Asia/Kolkata time when the API call completes. They represent the local attempt/completion time, not a verified platform timestamp.
- The task says “publicly accessible”; platform privacy settings and community membership can affect actual visibility. Confirm visibility in the platform itself.

## 1. Requirements

- Windows 10/11, macOS, or Linux
- Python 3.10+ (Python 3.11 recommended)
- Internet connection
- Git and a GitHub account for submission
- API credentials/accounts for destinations you intend to test live

Check installation:

```bash
python --version
pip --version
git --version
```

## 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
cd path\to\automated-posting
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once in the current PowerShell window, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configure API credentials

Copy `.env.example` to `.env`.

PowerShell:

```powershell
Copy-Item .env.example .env
```

Command Prompt:

```bat
copy .env.example .env
```

Open `.env` and fill credentials. Do not commit `.env` to GitHub.

### A. Mastodon

1. Create/sign in to an account on a Mastodon instance, for example mastodon.social.
2. Open Preferences → Development → New application.
3. Give the app a name and enable the `write:statuses` scope.
4. Save and copy the access token.
5. Set `MASTODON_BASE_URL` to your instance root (no trailing `/`) and `MASTODON_ACCESS_TOKEN` in `.env`.

The integration calls `POST /api/v1/statuses` with `visibility=public`.

### B. Bluesky

1. Sign in to Bluesky.
2. Open Settings → Privacy and Security → App Passwords.
3. Create an app password. Do not use your main password.
4. Put your handle/email in `BLUESKY_IDENTIFIER` and the generated password in `BLUESKY_APP_PASSWORD`.

The integration creates a session and writes an `app.bsky.feed.post` record through the AT Protocol.

### C. Telegram

1. In Telegram, open the verified `@BotFather` account and send `/newbot`.
2. Follow the prompts and copy the bot token.
3. Create a Telegram channel that you administer.
4. Add your bot as an administrator with permission to post messages.
5. Set `TELEGRAM_BOT_TOKEN`.
6. Set `TELEGRAM_CHAT_ID` to the public channel username such as `@my_public_channel` (or a numeric chat ID for a private destination).
7. If it is a public channel, set `TELEGRAM_CHANNEL_USERNAME` to `my_public_channel` (without `@`). For a private destination leave it blank.

### D. Discord

1. In Discord, open the server and channel you administer.
2. Edit Channel → Integrations → Webhooks → New Webhook.
3. Copy the webhook URL and set `DISCORD_WEBHOOK_URL`.
4. Optionally set `DISCORD_GUILD_ID` and `DISCORD_CHANNEL_ID` for a channel link.
5. The result deliberately reports `public_access: false`, because a Discord channel normally requires server membership. Do not claim it is public on the open web.

### E. WordPress

1. Use a WordPress site you own/administer and ensure HTTPS and REST API are enabled.
2. In wp-admin, open Users → Profile.
3. Find Application Passwords, enter a label such as `FastAPI posting`, and generate one.
4. Copy it immediately. Set site URL, WordPress login username, and application password in `.env`.
5. The WordPress user needs permission to publish posts (normally Author or Administrator).
6. The integration creates a published post at `/wp-json/wp/v2/posts`.

For a self-hosted site, application passwords require a compatible WordPress installation and HTTPS.

## 5. Run the API

From the project root, with the virtual environment active:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
```

Expected local URL:

- API: `http://127.0.0.1:4000`
- Swagger UI: `http://127.0.0.1:4000/docs`
- Health check: `http://127.0.0.1:4000/health`

## 6. Test from Swagger UI

1. Open `http://127.0.0.1:4000/docs`.
2. Expand `POST /posting`.
3. Click **Try it out**.
4. Use this request:

```json
{
  "message": "Check out our latest business platform and grow your online visibility. https://example.com"
}
```

5. Click **Execute**.
6. Review the five independent results. Any platform without credentials will return `failed` with a configuration error.

## 7. Test with PowerShell

```powershell
$body = @{
  message = "Check out our latest business platform and grow your online visibility. https://example.com"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:4000/posting" -Method Post -ContentType "application/json" -Body $body
```

Or with curl:

```bash
curl -X POST "http://127.0.0.1:4000/posting" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Check out our latest business platform. https://example.com\"}"
```

## 8. Validation checks

Try these in Swagger/Postman. They should return HTTP `422`:

No URL:

```json
{"message": "Hello, this is a test"}
```

Two URLs:

```json
{"message": "Visit https://one.example and https://two.example"}
```

Over 200 characters:

```json
{"message": "This message is intentionally longer than the allowed 200 characters. Add enough text here to make sure that the validation rejects it, and then some more text to exceed the limit."}
```

Valid input:

```json
{"message": "Hello from FastAPI https://example.com"}
```

## 9. Run automated tests

Stop the server or open another terminal, activate `.venv`, then:

```bash
pytest -v
```

The tests verify health, maximum length, exactly one URL, and a successful API response using a mocked posting service. They do not publish real messages.

## 10. Suggested evidence for submission

Capture screenshots of:

1. Project tree in VS Code.
2. Successful server startup in terminal.
3. Swagger `/docs` showing `POST /posting`.
4. Valid request and response showing all five platform result entries.
5. Invalid request returning `422`.
6. `pytest -v` showing tests passed.
7. At least one real post visible on a platform account you control (hide personal details/tokens).

If only some APIs are configured, explain that clearly in README and include the real success plus independent failure results. Do not fabricate successful posts or URLs.

## 11. GitHub submission

From the project root:

```bash
git init
git add .
git status
```

Check that `.env` is NOT listed. If it appears, remove it from staging:

```bash
git rm --cached .env
```

Commit and push (replace the repository URL with your own):

```bash
git commit -m "Build FastAPI multi-platform posting system"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/automated-posting.git
git push -u origin main
```

Create the GitHub repository as **Public**. Confirm the README renders correctly and that `.env` and tokens are absent.

## 12. Submission email

The task sheet asks for an email to `hr@chivoxai.com`, subject `Your Name - Python Practical test review`, with full name, public GitHub link, contact number, city/state, and best time for discussion. It also asks for LinkedIn and Instagram profile links for application verification. Deadline stated in the task: **22 November 2026**.

## Official API documentation

- Mastodon: https://docs.joinmastodon.org/methods/statuses/
- Bluesky / AT Protocol: https://atproto.com/guides/writing-data and https://docs.bsky.app/
- Telegram Bot API: https://core.telegram.org/bots/api#sendmessage
- Discord Webhooks: https://discord.com/developers/docs/resources/webhook
- WordPress REST API: https://developer.wordpress.org/rest-api/reference/posts/
- WordPress Application Passwords: https://developer.wordpress.org/advanced-administration/security/application-passwords/

## Known limitations / honest reporting

This is a practical-test starter implementation, not a production scheduler. It makes one synchronous attempt per destination, does not retry, and does not persist a posting history. Discord webhook response handling is intentionally conservative and does not claim a public message permalink. Check each platform's terms, rate limits, moderation rules, and account permissions before live use.
