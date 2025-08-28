import os
import requests
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

# Load environment variables (Render will inject these)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PREDICTION_API_BASE = os.getenv("PREDICTION_API_BASE", "https://football-prediction-api.onrender.com")

# --- Commands ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message when user starts the bot"""
    await update.message.reply_text(
        "⚽ Welcome to your AI Football Betting Bot!\n"
        "Use /today to get top 8 picks for today's games."
    )

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch today's top picks from the API"""
    try:
        url = f"{PREDICTION_API_BASE}/today"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if "picks" in data and len(data["picks"]) > 0:
                msg = "📊 Top 8 Picks Today:\n\n"
                for pick in data["picks"][:8]:
                    msg += f"🏟 {pick['fixture']} → {pick['bet']}\n"
                await update.message.reply_text(msg)
            else:
                await update.message.reply_text("No picks available for today.")
        else:
            await update.message.reply_text("⚠️ Error fetching picks from API.")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to fetch picks: {e}")

# --- MAIN APP ---
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))

    print("✅ Bot is up and running...")
    app.run_polling()

if __name__ == "__main__":
    main()
