import telebot

# 1. अपना टेलीग्राम टोकन यहाँ डालें
API_TOKEN = 'YOUR_BOT_TOKEN_HERE'

# 2. अपना MongoDB लिंक यहाँ डालें (जो आपने अभी बनाया था)
# लिंक ऐसा होना चाहिए: mongodb+srv://neeraj:password...@cluster...
MONGO_URI = 'YOUR_MONGODB_CONNECTION_STRING_HERE'

bot = telebot.TeleBot(API_TOKEN)
