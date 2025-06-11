import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, MessageHandler, filters,
    ContextTypes, CommandHandler
)

# Patch for Termux
nest_asyncio.apply()

# Config
BOT_TOKEN = '7776491935:AAGGrhoNKPHobiVGtc2O3KQghrZK3oi3nUE'
ADMIN_ID = 965159279
CHANNEL_ID = -1001827062484  # Your public or linked channel

# Memory storage
movie_storage = {}

# Start command for private chat
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Send a movie name to search.")

# Admin uploads
async def handle_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ You're not authorized.")

    doc = update.message.document
    if not doc:
        return await update.message.reply_text("⚠️ Send as a document.")

    file_name = doc.file_name or "unnamed_file"
    file_id = doc.file_id

    movie_storage[file_name.lower()] = file_id
    await update.message.reply_text(f"✅ Stored: {file_name}")

# Users search by writing in the channel
async def handle_channel_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHANNEL_ID:
        return  # Ignore if not from the target channel

    if not update.message or not update.message.text:
        return

    query = update.message.text.strip().lower()
    results = [name for name in movie_storage if query in name]

    if results:
        for name in results:
            await context.bot.send_document(
                chat_id=CHANNEL_ID,
                document=movie_storage[name],
                caption=f"🎬 {name}"
            )

# Main
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_upload))
    app.add_handler(MessageHandler(filters.TEXT & filters.Chat(CHANNEL_ID), handle_channel_search))

    print("🤖 Bot started.")
    await app.run_polling()

# Run safely in Termux
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
