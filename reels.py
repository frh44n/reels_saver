import os
import yt_dlp as youtube_dl
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from flask import Flask, request
import threading
import time

# Initialize Flask app
app = Flask(__name__)

# Define the fixed chat ID (replace this with your actual chat ID)
FIXED_CHAT_ID = '6826870863'  # Replace with the actual chat ID where you want the message to be sent

# Function to handle the /start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome! Send me an Instagram Reels link, and I'll download it for you. 🎥"
    )

# Function to handle Instagram Reels download
def download_reel(update: Update, context: CallbackContext):
    link = update.message.text
    chat_id = update.message.chat_id

    # Check if the link is valid
    if "instagram.com" not in link or "reel" not in link:
        update.message.reply_text("Please send a valid Instagram Reels link.")
        return

    try:
        # Set download directory based on chat ID
        download_dir = f"downloads/{chat_id}"
        os.makedirs(download_dir, exist_ok=True)

        # Youtube-dl options for Instagram Reels download
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(download_dir, '%(id)s.%(ext)s'),  # Save with the video ID as filename
            'noplaylist': True,
        }

        # Download the reel
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        # Find the downloaded file (video)
        video_file = None
        for file in os.listdir(download_dir):
            if file.endswith(".mp4"):
                video_file = os.path.join(download_dir, file)
                break

        if video_file:
            # Send the video to the user
            with open(video_file, "rb") as video:
                context.bot.send_video(chat_id=chat_id, video=video)
            update.message.reply_text("Here’s your Instagram Reel! 🎥")
        else:
            update.message.reply_text("Error: Could not find a video file.")

        # Cleanup after sending the video
        for file in os.listdir(download_dir):
            os.remove(os.path.join(download_dir, file))
        os.rmdir(download_dir)

    except Exception as e:
        update.message.reply_text(f"Error downloading the reel: {str(e)}")

# Function to send "Bot is live." message every 1 minute
def send_live_message():
    while True:
        try:
            # Send the message to the fixed chat ID
            bot.send_message(chat_id=FIXED_CHAT_ID, text="Bot is live.")
        except Exception as e:
            print(f"Error sending live message: {str(e)}")
        
        # Wait for 1 minute before sending the message again
        time.sleep(300)

# Function to start the bot
def start_bot():
    global bot
    TOKEN = "7733448915:AAGxvRU6dyJ9Cvvaxbim9n4oHR8tcm_mKuA"
    updater = Updater(token=TOKEN)
    bot = updater.bot
    dispatcher = updater.dispatcher

    # Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, download_reel))

    # Start the bot
    updater.start_polling()
    print("Bot is running...")

# Flask route for webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json_str, bot)
    dispatcher.process_update(update)
    return 'ok', 200

# Run Flask app
def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Start Flask in a thread and then start the bot
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Start the bot in a thread
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()

    # Start the task to send "Bot is live." every 1 minute
    live_message_thread = threading.Thread(target=send_live_message)
    live_message_thread.start()
