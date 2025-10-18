import yt_dlp
import subprocess
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8283970030:AAE_RSjA0F_6wQFFk0sG2iT366PQfci1l_w"

# ======== ВИДЕО ЖҮКТЕУ ФУНКЦИЯСЫ ========
def download_video(url):
    try:
        output_file = "video.mp4"
        ydl_opts = {
            "format": "best[height<=720]",
            "outtmpl": output_file,
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            duration = info.get("duration", 0)

        # Егер видео 10 минуттан ұзақ болса, қысқарту
        if duration > 600:
            print("⚙️ Видео ұзақ, 10 минутқа дейін қысқартылып жатыр...")
            command = [
                "ffmpeg", "-y", "-i", output_file, "-t", "600",
                "-c:v", "libx264", "-c:a", "aac", "compressed.mp4"
            ]
        else:
            print("⚙️ Видео қысқартусыз сақталуда...")
            command = [
                "ffmpeg", "-y", "-i", output_file,
                "-c:v", "libx264", "-c:a", "aac",
                "-b:v", "1500k", "-b:a", "128k", "compressed.mp4"
            ]

        # ffmpeg арқылы өңдеу
        result = subprocess.run(command, capture_output=True, text=True, timeout=1200)

        if result.returncode != 0:
            print("FFMPEG ERROR:", result.stderr)
            raise Exception("⚠️ ffmpeg қатесі — файл өңделмеді.")

        if not os.path.exists("compressed.mp4"):
            raise Exception("⚠️ Қысқартылған файл табылмады.")

        return "compressed.mp4"

    except subprocess.TimeoutExpired:
        raise Exception("⚠️ Видео тым ұзақ немесе интернет баяу.")
    except Exception as e:
        raise Exception(f"Қате: {e}")

# ======== /start ========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Сәлем! 👋\n"
        "Мен видео жүктейтін ботпын.\n\n"
        "Тек YouTube, TikTok, немесе Instagram сілтемесін жіберіңіз — "
        "мен оны 720p форматында жіберем 🎬"
    )

# ======== СІЛТЕМЕ ӨҢДЕУ ========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if any(x in url for x in ["youtube.com", "youtu.be", "tiktok.com", "instagram.com", "reel"]):
        try:
            await update.message.reply_text("⏬ Видео жүктелуде, күте тұрыңыз...")
            filepath = download_video(url)

            # 20MB-тан асса, қосымша қысқарту
            if os.path.getsize(filepath) > 20 * 1024 * 1024:
                await update.message.reply_text("⚙️ Видео үлкен, 720p-ға дейін қысқартылуда...")
                subprocess.run([
                    "ffmpeg", "-y", "-i", filepath,
                    "-vf", "scale=-1:720", "-b:v", "1500k", "-preset", "veryfast", "compressed.mp4"
                ], check=True)

                if os.path.exists(filepath):
                    os.remove(filepath)
                filepath = "compressed.mp4"

            with open(filepath, "rb") as video:
                await update.message.reply_video(video)

            os.remove(filepath)

        except Exception as e:
            await update.message.reply_text(str(e))

    else:
        await update.message.reply_text("❗ Тек YouTube, TikTok немесе Instagram сілтемесін жіберіңіз.")

# ======== MAIN ========
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот іске қосылды!")
    app.run_polling()

if __name__ == "__main__":
    main()
