import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
import yt_dlp

# Файл жолдары
TOKEN = "8283970030:AAE_RSjA0F_6wQFFk0sG2iT366PQfci1l_w"
COOKIE_FILE = "cookies.txt"  # Render-де немесе локалда ботпен бір папкада болу керек

# Видео жүктеу функциясы
def download_video(video_url: str, output_file: str):
    ydl_opts = {
        "format": "best[height<=720]",
        "outtmpl": output_file,
        "quiet": True,
        "cookiefile": COOKIE_FILE,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        duration = info.get("duration", 0)
    return duration

# /start командасы
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Сәлем! Видео сілтемесін жіберіңіз.")

# Сілтеме келгенде
def handle_message(update: Update, context: CallbackContext):
    url = update.message.text
    update.message.reply_text("⏬ Видео жүктелуде, күте тұрыңыз...")

    # Жүктеу
    output_file = "video.mp4"  # уақытша файл аты
    try:
        duration = download_video(url, output_file)
        # Видео жіберу
        with open(output_file, "rb") as f:
            update.message.reply_video(f)
        os.remove(output_file)  # уақытша файлды өшіру
    except Exception as e:
        update.message.reply_text(f"Қате: {e}")

# Ботты іске қосу
def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
