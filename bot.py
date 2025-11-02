import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Load medicine data
data = pd.read_csv("data/medicines.csv")

def search_medicine(name):
    """Search for a medicine name and return its info."""
    result = data[data['Drug Name'].str.lower() == name.lower()]
    if result.empty:
        return "❌ Medicine not found in database. Please check spelling."
    
    info = result.iloc[0]
    return f"""💊 *{info['Drug Name']}*
Class: {info['Class']}
Use: {info['Indication']}
Dosage: {info['Dosage']}
Side Effects: {info['Side Effects']}
Note: {info['Special Instructions']}
"""

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to MedGuide! Send me any medicine name to get its basic info and safe use tips.")

# Respond to messages
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    reply_text = search_medicine(query)
    await update.message.reply_text(reply_text, parse_mode="Markdown")

def main():
    TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"  # Replace with your Telegram bot token
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    print("🤖 Bot is running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
