
import json
import os
import random
import string
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@default_channel")
LINK_DB_FILE = "video_links.json"

def load_links():
    if os.path.exists(LINK_DB_FILE):
        with open(LINK_DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_links(data):
    with open(LINK_DB_FILE, "w") as f:
        json.dump(data, f)

def generate_id(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        video_id = args[0]
        links = load_links()
        if video_id in links:
            file_id = links[video_id]
            await update.message.reply_video(file_id)
        else:
            await update.message.reply_text("Video tidak ditemukan.")
    else:
        await update.message.reply_text("Kirim video ke saya, nanti saya kasih link-nya.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    if not video:
        await update.message.reply_text("Tolong kirim video.")
        return

    file_id = video.file_id
    links = load_links()

    if file_id in links.values():
        for key, value in links.items():
            if value == file_id:
                video_id = key
                break
    else:
        video_id = generate_id()
        links[video_id] = file_id
        save_links(links)

    bot_username = context.bot.username
    link = f"https://t.me/{bot_username}?start={video_id}"
    title = update.message.caption or "Video baru"

    await update.message.reply_text(f"{title}\n{link}")
    await context.bot.send_message(chat_id=CHANNEL_USERNAME, text=f"{title}\n{link}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
app.run_polling()
