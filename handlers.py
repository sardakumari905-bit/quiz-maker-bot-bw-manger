from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineQueryResultArticle, InputTextMessageContent
from config import bot
import database

# --- 1. START / RESTART ---
@bot.message_handler(commands=['start', 'restart'])
def send_welcome(message):
    uid = message.chat.id
    if uid in database.user_state: del database.user_state[uid]
    
    bot.send_message(uid, "🤖 **Ultra Poll Bot Ready!**\n\nनया क्विज़ बनाने के लिए /createquiz दबाएं।", reply_markup=ReplyKeyboardRemove())

# --- 2. CREATE QUIZ FLOW ---
@bot.message_handler(commands=['createquiz'])
def create_q(message):
    uid = message.chat.id
    database.user_state[uid] = {"step": 1, "options": []} # लिस्ट तैयार
    bot.send_message(uid, "📝 **Quiz का Title क्या है?**")

@bot.message_handler(func=lambda m: True)
def handle_text(m):
    uid = m.chat.id
    text = m.text

    if uid not in database.user_state: return

    state = database.user_state[uid]
    step = state["step"]

    # Step 1: Title
    if step == 1:
        state["title"] = text
        state["step"] = 2
        bot.send_message(uid, "📄 **Description (विवरण) क्या है?**")

    # Step 2: Description
    elif step == 2:
        state["desc"] = text
        state["step"] = 3
        bot.send_message(uid, "❓ **प्रश्न (Question) क्या है?**")

    # Step 3: Question
    elif step == 3:
        state["question"] = text
        state["step"] = 4
        bot.send_message(uid, "mw **Option A (पहला ऑप्शन) भेजें:**")

    # Step 4: Option A
    elif step == 4:
        state["options"].append(text) # लिस्ट में डाला
        state["step"] = 5
        bot.send_message(uid, "mw **Option B (दूसरा ऑप्शन) भेजें:**")

    # Step 5: Option B
    elif step == 5:
        state["options"].append(text)
        state["step"] = 6
        bot.send_message(uid, "mw **Option C (तीसरा ऑप्शन) भेजें:**")

    # Step 6: Option C
    elif step == 6:
        state["options"].append(text)
        state["step"] = 7
        bot.send_message(uid, "mw **Option D (चौथा ऑप्शन) भेजें:**")

    # Step 7: Option D -> Ask Correct Answer
    elif step == 7:
        state["options"].append(text)
        state["step"] = 8
        
        # बटन वाला कीबोर्ड ताकि यूजर गलती न करे
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Option A", "Option B")
        markup.add("Option C", "Option D")
        
        bot.send_message(uid, "✅ **सही जवाब कौन सा है?**\nनीचे दिए बटन से चुनें:", reply_markup=markup)

    # Step 8: Save Everything
    elif step == 8:
        # सही जवाब को नंबर में बदलना (0,1,2,3)
        correct_map = {"Option A": 0, "Option B": 1, "Option C": 2, "Option D": 3}
        
        if text not in correct_map:
            bot.send_message(uid, "❌ कृपया नीचे दिए बटन्स का उपयोग करें!")
            return

        correct_id = correct_map[text]
        
        # डेटाबेस में सेव करना
        quiz_id = database.save_new_quiz(
            uid, state["title"], state["desc"], state["question"], state["options"], correct_id
        )
        
        del database.user_state[uid]
        
        # कीबोर्ड हटाना और फाइनल पैनल भेजना
        bot.send_message(uid, "✅ **Quiz Created Successfully!**", reply_markup=ReplyKeyboardRemove())
        send_panel(uid, quiz_id)

# --- 3. PANEL & SHARING ---
def send_panel(chat_id, quiz_id):
    quiz = database.get_quiz_by_id(quiz_id)
    bot_username = bot.get_me().username
    
    msg = f"🔥 **{quiz['title']}**\n📖 {quiz['desc']}\n\n👇 **Start** बटन दबाकर क्विज़ खेलें!"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🚀 Start Quiz", callback_data=f"start_{quiz_id}"))
    markup.add(InlineKeyboardButton("👥 Start in Group", switch_inline_query=quiz_id))
    
    share_url = f"https://t.me/share/url?url=https://t.me/{bot_username}?start={quiz_id}"
    markup.add(InlineKeyboardButton("🔗 Share Link", url=share_url))

    bot.send_message(chat_id, msg, reply_markup=markup)

# --- 4. START QUIZ (POLL SYSTEM) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('start_'))
def handle_poll(call):
    quiz_id = call.data.split('_')[1]
    quiz = database.get_quiz_by_id(quiz_id)
    
    if quiz:
        bot.answer_callback_query(call.id, "🚀 Quiz Launching...")
        
        # 🔥 ULTRA PRO FEATURE: NATIVE POLL 🔥
        bot.send_poll(
            chat_id=call.message.chat.id,
            question=quiz['question'],
            options=quiz['options'],
            type='quiz',                # Quiz Mode ON
            correct_option_id=quiz['correct_option_id'],
            is_anonymous=False,         # नाम दिखेगा (Group में अच्छा लगता है)
            explanation="Good Job! 🎯"   # जवाब देने के बाद दिखेगा
        )
    else:
        bot.answer_callback_query(call.id, "❌ Quiz Not Found")

# --- 5. INLINE QUERY (GROUP SHARING) ---
@bot.inline_handler(func=lambda q: True)
def inline_share(q):
    try:
        qid = q.query
        data = database.get_quiz_by_id(qid)
        if data:
            # Result में "Send Quiz" का ऑप्शन
            r = InlineQueryResultArticle(
                id='1', 
                title=f"Send: {data['title']}", 
                description=data['desc'],
                input_message_content=InputTextMessageContent(f"Guys! Let's play: {data['title']}\n\n👇 Click below to start!")
            )
            # साथ में बटन भी भेज सकते हैं, पर Telegram Policy कभी-कभी रोकती है
            # तो अभी सिंपल टेक्स्ट भेजते हैं, यूजर बॉट के लिंक पर क्लिक करेगा
            bot.answer_inline_query(q.id, [r])
    except: pass
