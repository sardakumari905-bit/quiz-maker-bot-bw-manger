import telebot

# 1. अपना टेलीग्राम बॉट टोकन यहाँ डालें (जो BotFather से मिला था)
# 'YOUR_BOT_TOKEN_HERE' को हटाकर अपना टोकन लिखें
API_TOKEN = '8320752947:AAH823cOM83JHwJfwsTJULxJaib16PRLtUo'

# 2. आपका MongoDB लिंक (जो आपने दिया था)
# यह एकदम सही है, इसमें कुछ मत बदलना
MONGO_URI = 'mongodb+srv://sardakumari905_db_user:p6yUp70gQGLwYTDN@cluster0.0r1bebe.mongodb.net/?appName=Cluster0'

# बॉट को स्टार्ट करना
bot = telebot.TeleBot(API_TOKEN)
