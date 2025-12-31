from config import bot
import handlers
from keep_alive import keep_alive

if __name__ == "__main__":
    print("🤖 Bot is Starting...")
    keep_alive()  # Server start
    bot.infinity_polling()
