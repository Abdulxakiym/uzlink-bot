# UzLink Bot

Telegram logistics bot connecting truck drivers and consumers.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file next to `bot.py` with:

```
BOT_TOKEN=your_telegram_bot_token
ADMIN_TELEGRAM_ID=64743910
CALL_CENTER="+998 (77) 177-10-01"
RADIUS_KM=300
```

3. Run the bot:

```bash
python bot.py
```

A SQLite database will be created at `data/uzlink.sqlite3` on first run.

## Roles

- **Consumers**: register with personal data and passport photos, request trucks via "Find a car" flow and track delivery status.
- **Drivers**: register with license and vehicle info, receive and accept orders, share live location during delivery.

## Known limitations

- Geolocation sharing persists only during a single bot session.
- Reminders and background jobs require the bot to stay running.
