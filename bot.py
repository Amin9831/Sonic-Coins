import math
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import os

TOKEN = os.getenv("BOT_TOKEN")

data = {}

FIELDS = [
    "goals",
    "assists",
    "cl",
    "wc",
    "matches",
    "saver",
    "motm"
]

QUESTIONS = {
    "goals": "⚽ چند گل زده؟",
    "assists": "🎯 چند پاس گل؟",
    "cl": "🏆 CL (1 / 2 / 4 / 8)",
    "wc": "🌍 WC (1 / 2 / 4 / 8)",
    "matches": "🎮 چند بازی؟",
    "saver": "🛡 چند بار نجات تیم؟",
    "motm": "⭐ چند بار MOTM؟"
}


async def typing(update):
    await update.message.chat.send_action(action="typing")
    await asyncio.sleep(1)


def calc_votes(p):
    g = p["stats"]["goals"]
    a = p["stats"]["assists"]
    cl = p["stats"]["cl"]
    wc = p["stats"]["wc"]
    m = p["stats"]["matches"]
    s = p["stats"]["saver"]
    motm = p["stats"]["motm"]

    raw = (
        g * 4 +
        a * 3 +
        (8 / cl) * 10 +
        (8 / wc) * 15 +
        s * 5 +
        motm * 2
    )

    if m == 0:
        return 0

    return round(raw / math.sqrt(m))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id

    data[user] = {
        "players": [],
        "mode": "name",
        "field_index": 0
    }

    await typing(update)

    await update.message.reply_text(
        "🏆 مراسم توپ طلا آغاز شد...\n"
        "👤 اسم بازیکن اول رو بگو:"
    )


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    text = update.message.text

    if user not in data:
        await update.message.reply_text("اول /start رو بزن")
        return

    user_data = data[user]

    if user_data["mode"] == "name":
        await typing(update)

        user_data["players"].append({
            "name": text,
            "stats": {}
        })

        user_data["mode"] = "stats"
        user_data["field_index"] = 0

        await update.message.reply_text(
            f"📊 آمار {text}:\n\n{QUESTIONS[FIELDS[0]]}"
        )
        return

    if user_data["mode"] == "stats":
        await typing(update)

        idx = user_data["field_index"]
        player = user_data["players"][-1]

        try:
            player["stats"][FIELDS[idx]] = int(text)
        except:
            await update.message.reply_text("❌ فقط عدد بفرست")
            return

        idx += 1
        user_data["field_index"] = idx

        if idx < len(FIELDS):
            await update.message.reply_text(QUESTIONS[FIELDS[idx]])
            return

        if len(user_data["players"]) < 5:
            user_data["mode"] = "name"
            await update.message.reply_text("👤 بازیکن بعدی:")
            return

        await show_result(update, user)


async def show_result(update: Update, user):
    players = data[user]["players"]

    results = []
    for p in players:
        votes = calc_votes(p)
        results.append((p["name"], votes))

    results.sort(key=lambda x: x[1], reverse=True)

    await update.message.reply_text("🚨 نتایج در حال آماده‌سازی...")

    await asyncio.sleep(2)

    ranking = ""

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

    for i, (name, votes) in enumerate(results):
        msg = f"{medals[i]} {name} — {votes} رأی"
        await update.message.reply_text(msg)
        ranking += msg + "\n"
        await asyncio.sleep(2)

    winner, votes = results[0]

    await update.message.reply_text(
        f"🏆 برنده توپ طلا: {winner}\n"
        f"🗳 تعداد رأی: {votes}\n\n"
        "✨ این نام در تاریخ ثبت شد..."
    )

    data[user] = {}


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()
