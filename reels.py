from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, Dispatcher
from telegram.ext.callbackcontext import CallbackContext
from flask import Flask, request
import instaloader
import os
from database import init_db, get_or_create_user, increment_video_count
from config import Config
from telegram import Bot

# Initialize the database
init_db()

# Set up Instaloader
L = instaloader.Instaloader()

# Initialize Flask app
app = Flask(__name__)

# Initialize Bot and Dispatcher
bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to Instagram Reels Downloader Bot!\n"
        "Please send me the link to the Instagram reel you want to download."
    )

def download_reel(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    url = update.message.text

    try:
        # Extract Instagram post ID from the URL
        post_id = url.split("/")[-2]

        # Download the Instagram reel
        L.download_post(L.check_profile_id(post_id), target='reels')

        # Find the downloaded video file
        for file in os.listdir('reels'):
            if file.endswith('.mp4'):
                video_path = os.path.join('reels', file)
                break

        # Send the video to the user
        context.bot.send_video(chat_id=chat_id, video=open(video_path, 'rb'))

        # Clean up
        os.remove(video_path)
        os.rmdir('reels')

        # Update the user's video count in the database
        get_or_create_user(chat_id)
        increment_video_count(chat_id)

    except Exception as e:
        update.message.reply_text(f"Failed to download reel: {e}")

# Add handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_reel))

@app.route('/' + Config.TELEGRAM_BOT_TOKEN, methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT)
