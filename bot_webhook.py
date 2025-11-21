# bot_webhook.py
import os
import logging
import aiohttp
from aiohttp import web
import pandas as pd
from telegram import Bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is required")

# Public base URL for webhook MUST be set in Render env as WEBHOOK_BASE_URL,
# e.g. https://medguide-bot.onrender.com  (no trailing slash)
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE_URL")
if not WEBHOOK_BASE:
    logger.warning("WEBHOOK_BASE_URL not set. You will need to set webhook manually after deploy.")

# Load medicine data
DATA_PATH = os.getenv("MEDICINES_CSV", "data/medicines.csv")
df = pd.read_csv(DATA_PATH)
# Normalize for matching
df["lookup_name"] = df["Generic Name"].str.lower().str.strip()

bot = Bot(token=TOKEN)

def format_reply(row):
    return (
        f"💊 *{row['Generic Name']}*\n"
        f"Class: {row.get('Drug Class','-')}\n"
        f"Use: {row.get('Use (patient-friendly)','-')}\n"
        f"Dosage: {row.get('Typical Adult Dose (simple)','-')}\n"
        f"⚠️ {row.get('One-line caution / safety note','-')}\n\n"
        f"🔎 When to see doctor: {row.get('When to see doctor / red flags','If unsure, consult a doctor')}"
    )

async def handle_update(request):
    """
    Route: POST /<TOKEN>
    Telegram will POST Update JSON here.
    """
    try:
        update = await request.json()
    except Exception as e:
        logger.exception("Invalid JSON")
        return web.Response(status=400, text="bad json")

    # quick guard: ignore non-message updates
    message = update.get("message") or update.get("edited_message") or update.get("channel_post")
    if not message:
        return web.Response(status=200, text="no message")

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "").strip()
    if not text:
        await bot.send_message(chat_id=chat_id, text="Please send a medicine name (text).")
        return web.Response(status=200, text="ok")

    q = text.lower().strip()
    # exact match on generic or brand examples (simple approach)
    row = df[df["lookup_name"] == q]

    if row.empty:
        # try contains (partial match)
        row = df[df["lookup_name"].str.contains(q, na=False)]

    if row.empty:
        # fallback: reply not found
        reply = "❌ I couldn't find that medicine in my list. Try typing the generic name (e.g., paracetamol) or check spelling."
        await bot.send_message(chat_id=chat_id, text=reply)
        return web.Response(status=200, text="ok")

    info = row.iloc[0]
    reply = format_reply(info)
    # send Markdown-formatted reply
    await bot.send_message(chat_id=chat_id, text=reply, parse_mode="Markdown")
    return web.Response(status=200, text="ok")

async def set_webhook_on_startup(app):
    """
    Optional: set webhook if WEBHOOK_BASE_URL provided.
    This will call setWebhook to Telegram with https://WEBHOOK_BASE/<TOKEN>
    """
    if WEBHOOK_BASE:
        webhook_url = f"{WEBHOOK_BASE}/{TOKEN}"
        logger.info("Setting webhook to: %s", webhook_url)
        res = await bot.set_webhook(webhook_url)
        logger.info("setWebhook result: %s", res)
    else:
        logger.info("WEBHOOK_BASE_URL not set; please call setWebhook manually.")

# Create aiohttp app and route to /<TOKEN>
app = web.Application()
app.router.add_post(f"/{TOKEN}", handle_update)

# set webhook during startup if base url available
app.on_startup.append(set_webhook_on_startup)

# basic health endpoint
async def health(request):
    return web.Response(text="MedGuide webhook alive")

app.router.add_get("/", health)
