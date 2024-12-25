import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import instaloader
from flask import Flask, request
import threading

# Initialize Flask app
app = Flask(__name__)

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
        # Initialize Instaloader
        loader = instaloader.Instaloader()

        # Set download directory based on chat ID
        download_dir = f"downloads/{chat_id}"
        os.makedirs(download_dir, exist_ok=True)

        # Download the reel
        loader.download_post(
            instaloader.Post.from_shortcode(loader.context, link.split("/")[-2]),
            target=download_dir,
        )

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

# Function to start the bot
def start_bot():
    TOKEN = "7733448915:AAGxvRU6dyJ9Cvvaxbim9n4oHR8tcm_mKuA"
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    # Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, download_reel))

    # Start the bot
    updater.start_polling()
    print("Bot is running...")

# Flask route for webhook (if needed for webhook-based deployment)
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json_str, bot)
    dispatcher.process_update(update)
    return 'ok', 200

# Run Flask app
def run_flask():
    port = int(os.environ.get('PORT', 5000))  # Get the PORT environment variable for Render or default to 5000
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Run the Telegram bot in a separate thread
    threading.Thread(target=start_bot).start()
    run_flask()
