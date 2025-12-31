from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineQueryResultArticle, InputTextMessageContent
from config import bot
import database

# --- 1. START & RESTART ---
@bot.message_handler(commands=['start', 'restart'])
def send_welcome(message):
    uid = message.chat.id
    if uid in database.user_state: del database.user_state[uid]
    bot.send_message(uid, "🤖 **Ultra Poll Bot Ready!**\n\nनया क्विज़ बनाने के लिए /createquiz दबाएं।", reply_markup=ReplyKeyboardRemove())

# --- 2. CREATE QUIZ (STEP-BY-STEP) ---
@bot.message_handler(commands=['createquiz'])
def create_q(message):
    uid = message.chat.id
    database.user_state[uid] = {"step": 1, "options": []}
    bot.send_message(uid, "📝 **Quiz का Title (नाम) क्या है?**")

@bot.message_handler(func=lambda m: True)
def handle_text(m):
    uid = m.chat.id
    text = m.text
    if uid not in database.user_state: return

    state = database.user_state[uid]
    step = state["step"]

    # Step 1: Title -> Desc
    if step == 1:
        state["title"] = text
        state["step"] = 2
        bot.send_message(uid, "📄 **Description (विवरण) भेजें:**")

    # Step 2: Desc -> Question
    elif step == 2:
        state["desc"] = text
        state["step"] = 3
        bot.send_message(uid, "❓ **अपना प्रश्न (Question) भेजें:**")

    # Step 3: Question -> Option A
    elif step == 3:
        state["question"] = text
        state["step"] = 4
        bot.send_message(uid, "mw **पहला ऑप्शन (Option A) भेजें:**")

    # Step 4,5,6: Options Collect karna
    elif step in [4, 5, 6]:
        state["options"].append(text)
        state["step"] += 1
        opts = {4: "B", 5: "C", 6: "D"}
        bot.send_message(uid, f"mw **अगला ऑप्शन (Option {opts[state['step']-1]}) भेजें:**")

    # Step 7: Last Option -> Ask Correct Answer
    elif step == 7:
        state["options"].append(text)
        state["step"] = 8
        
        # बटन दिखाना ताकि यूजर आसानी से सही जवाब चुन सके
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Option A", "Option B")
        markup.add("Option C", "Option D")
        bot.send_message(uid, "✅ **सही जवाब कौन सा है?** चुनें:", reply_markup=markup)

    # Step 8: Save & Finish
    elif step == 8:
        mapper = {"Option A": 0, "Option B": 1, "Option C": 2, "Option D": 3}
        if text not in mapper:
            bot.send_message(uid, "❌ कृपया बटन का उपयोग करें!")
            return

        quiz_id = database.save_new_quiz(
            uid, state["title"], state["desc"], state["question"], state["options"], mapper[text]
        )
        del database.user_state[uid]
        bot.send_message(uid, "✅ **Quiz बन गया!**", reply_markup=ReplyKeyboardRemove())
        send_panel(uid, quiz_id)

# --- 3. PANEL SENDER ---
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

# --- 4. POLL SENDER (ASLI JADU) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('start_'))
def handle_poll(call):
    quiz_id = call.data.split('_')[1]
    quiz = database.get_quiz_by_id(quiz_id)
    
    if quiz:
        bot.answer_callback_query(call.id, "🚀 Launching Poll...")
        # यह Telegram का Native Poll भेजता है
        bot.send_poll(
            chat_id=call.message.chat.id,
            question=quiz['question'],
            options=quiz['options'],
            type='quiz',
            correct_option_id=quiz['correct_option_id'],
            is_anonymous=False,
            explanation="🎉 सही जवाब!"
        )

# --- 5. GROUP SHARING ---
@bot.inline_handler(func=lambda q: True)
def inline_share(q):
    try:
        qid = q.query
        data = database.get_quiz_by_id(qid)
        if data:
            r = InlineQueryResultArticle(
                id='1', title=f"Send: {data['title']}", description=data['desc'],
                input_message_content=InputTextMessageContent(f"Guys! Let's play: {data['title']}\n\n👇 Click below to start!")
            )
            bot.answer_inline_query(q.id, [r])
    except: pass
