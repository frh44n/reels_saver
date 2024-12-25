from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import instaloader
import os

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
        # Set download directory
        download_dir = f"downloads/{chat_id}"
        os.makedirs(download_dir, exist_ok=True)

        # Download the reel
        loader.download_post(
            instaloader.Post.from_shortcode(loader.context, link.split("/")[-2]),
            target=download_dir,
        )

        # Find the downloaded file
        for file in os.listdir(download_dir):
            if file.endswith(".mp4"):
                # Send the file to the user
                video_path = os.path.join(download_dir, file)
                context.bot.send_video(chat_id=chat_id, video=open(video_path, "rb"))
                break

        # Cleanup
        for file in os.listdir(download_dir):
            os.remove(os.path.join(download_dir, file))
        os.rmdir(download_dir)

    except Exception as e:
        update.message.reply_text(f"Error downloading the reel: {str(e)}")

# Main function to set up the bot
def main():
    # Replace with your bot token
    TOKEN = "7733448915:AAGxvRU6dyJ9Cvvaxbim9n4oHR8tcm_mKuA"

    # Initialize the bot
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    # Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, download_reel))

    # Start the bot
    updater.start_polling()
    print("Bot is running...")
    updater.idle()

if __name__ == "__main__":
    main()
