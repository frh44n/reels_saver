from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher
from telegram.ext.callbackcontext import CallbackContext
from flask import Flask, request
import instaloader
import os
from database import init_db, get_or_create_user, increment_video_count
from config import Config

# Initialize the database
init_db()

# Set up Instaloader
L = instaloader.Instaloader()

# Initialize Flask app
app = Flask(__name__)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Send me reels link to download it.")

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

def main():
    # Set up Telegram updater and dispatcher
    updater = Updater(Config.TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, download_reel))

    # Set webhook
    updater.start_webhook(listen="0.0.0.0", port=Config.PORT, url_path=Config.TELEGRAM_BOT_TOKEN)
    updater.bot.set_webhook(Config.WEBHOOK_URL + Config.TELEGRAM_BOT_TOKEN)

    # Start Flask app
    app.run(host='0.0.0.0', port=Config.PORT)

@app.route('/' + Config.TELEGRAM_BOT_TOKEN, methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return 'ok'

if __name__ == '__main__':
    main()
