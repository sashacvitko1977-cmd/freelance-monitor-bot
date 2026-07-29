# Freelance.ru Telegram Monitor

Async bot that checks the public Freelance.ru task feed every 10 seconds, filters projects, and sends new matches to Telegram. SQLite stores sent URLs for deduplication.

## Run

1. Create a bot with BotFather and set the destination `CHAT_ID`.
2. Copy `.env.example` to `.env` and set `BOT_TOKEN` and `CHAT_ID`.
3. Start the service:

```bash
docker compose up -d --build
```

Follow logs with `docker compose logs -f freelance-bot`.

## Filters

Edit `KEYWORDS`, `BLACKLIST`, and `MIN_PRICE` in `config.py`. Matching checks title, category, and description. With a positive `MIN_PRICE`, projects without a recognized price are ignored.

## Telegram commands

`/start` status, `/last` last 10 sent projects, `/stats` sent count, `/pause` pause monitoring, `/resume` resume monitoring.

## Implementation

The current public task feed is `https://freelance.ru/task` and is parsed from HTML with httpx and BeautifulSoup. If a JavaScript or Cloudflare challenge is returned, the optional Playwright fallback opens Chromium. Login variables are supported in `.env`; the public feed currently does not require authentication.

The bot does not attempt to bypass CAPTCHA or access restrictions. Check Freelance.ru rules and request frequency limits before production use.
