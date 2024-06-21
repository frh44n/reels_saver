from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, Dispatcher
from flask import Flask, request
import instaloader
import os
import logging
from database import init_db, get_or_create_user, increment_video_count, create_custom_table, get_all_users
from config import Config

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the database
init_db()

# Set up Instaloader
L = instaloader.Instaloader()

def login_instagram():
    session_file = f"/tmp/.instaloader-{Config.INSTAGRAM_USERNAME}"
    try:
        L.load_session_from_file(Config.INSTAGRAM_USERNAME, session_file)
        logger.info("Loaded session from file")
    except FileNotFoundError:
        logger.info("Session file not found, logging in")
        L.login(Config.INSTAGRAM_USERNAME, Config.INSTAGRAM_PASSWORD)
        L.save_session_to_file(session_file)

login_instagram()

# Initialize Flask app
app = Flask(__name__)

# Initialize Bot and Dispatcher
bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=4, use_context=True)  # Use workers > 0 for webhook mode

def start(update: Update, context: CallbackContext):
    logger.info(f"Received /start command from {update.message.chat_id}")
    update.message.reply_text(
        "Welcome to Instagram Reels Downloader Bot!\n"
        "Please send me the link to the Instagram reel you want to download."
    )

def download_reel(update: Update, context: CallbackContext):
    logger.info(f"Received a reel download request from {update.message.chat_id} with URL: {update.message.text}")
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
        logger.error(f"Failed to download reel: {e}")
        update.message.reply_text(f"Failed to download reel: {e}")

def create_table_command(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if chat_id in Config.AUTHORIZED_USERS:
        try:
            create_custom_table()
            update.message.reply_text("Table created successfully!")
        except Exception as e:
            logger.error(f"Failed to create table: {e}")
            update.message.reply_text(f"Failed to create table: {e}")
    else:
        update.message.reply_text("You are not authorized to execute this command.")

def list_users_command(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if chat_id in Config.AUTHORIZED_USERS:
        try:
            users = get_all_users()
            user_list = "\n".join([f"User ID: {user[0]}, Downloads: {user[1]}" for user in users])
            update.message.reply_text(f"Users:\n{user_list}")
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            update.message.reply_text(f"Failed to list users: {e}")
    else:
        update.message.reply_text("You are not authorized to execute this command.")

# Add handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("createtable", create_table_command))
dispatcher.add_handler(CommandHandler("list_users", list_users_command))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, download_reel))

@app.route('/' + Config.TELEGRAM_BOT_TOKEN, methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

if __name__ == '__main__':
    # Set webhook when starting the application
    WEBHOOK_URL = f"https://reels-saver.onrender.com/{Config.TELEGRAM_BOT_TOKEN}"
    bot.set_webhook(url=WEBHOOK_URL)

    app.run(host='0.0.0.0', port=Config.PORT)
