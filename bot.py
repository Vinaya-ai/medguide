import os
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Load the medicine database
data = pd.read_csv("data/medicines.csv")

def search_medicine(name):
    result = data[data['Drug Name'].str.lower() == name.lower()]
    if result.empty:
        return "❌ Medicine not found in database. Try another name."
    info = result.iloc[0]
    return f"""
💊 *{info['Drug Name']}*
Class: {info['Class']}
Use: {info['Indication']}
Dosage: {info['Dosage']}
Side Effects: {info['Side Effects']}
💡 *Tip:* {info['Special Instructions']}
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to MedGuide! Send me a medicine name to learn its use, dosage, and safety tips.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    reply = search_medicine(query)
    await update.message.reply_text(reply, parse_mode="Markdown")

def main():
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
