import os
import aiohttp
import asyncio
from datetime import datetime
from telegram.ext import ApplicationBuilder, CommandHandler

# Get Bot Token and API URL from Render environment settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PREDICTION_API_BASE = os.getenv("PREDICTION_API_BASE", "https://football-prediction-api.onrender.com")

async def start(update, context):
    await update.message.reply_text(
        "⚽ Welcome to your AI Football Betting Bot!\n"
        "Use /today to get top 8 picks for today's games."
    )

async def today(update, context):
    await update.message.reply_text("⏳ Fetching today’s top value picks...")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{PREDICTION_API_BASE}/value-signals", params={"threshold": 5.0}) as resp:
                signals = await resp.json()
        except Exception as e:
            await update.message.reply_text(f"Error fetching picks: {e}")
            return

    today_str = datetime.now().strftime("%Y-%m-%d")
    todays = [s for s in signals if s.get("kickoff", "").startswith(today_str)]
    todays.sort(key=lambda x: x["edge_percentage"], reverse=True)
    top8 = todays[:8]

    if not top8:
        await update.message.reply_text("📭 No picks available for today.")
        return

    msg = ["🌞 Top 8 Value Bets:"]
    for i, s in enumerate(top8, 1):
        msg.append(
            f"{i}. {s['fixture']} ({s['league']})\n"
            f"   • {s['market']}\n"
            f"   • AI {s['ai_probability']*100:.1f}% | "
            f"Edge +{s['edge_percentage']:.1f}% | "
            f"Kelly {s['kelly_stake_pct']:.1f}%"
        )

    await update.message.reply_text("\n".join(msg))

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))
    app.run_polling()

if __name__ == "__main__":
    main()
