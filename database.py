import pymongo
import certifi
from config import MONGO_URI

# कनेक्ट करना
try:
    client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client['QuizBotDB']
    quizzes_col = db['quizzes']
    print("✅ Database Connected Successfully!")
except Exception as e:
    print(f"❌ Database Error: {e}")

# टेंपरेरी मेमोरी (क्विज़ बनाते समय के लिए)
user_state = {}

# --- नया सेव फंक्शन (Polls के लिए) ---
def save_new_quiz(user_id, title, desc, question, options, correct_id):
    quiz_id = f"quiz_{user_id}_{str(title).replace(' ', '')[:5]}"
    
    data = {
        "_id": quiz_id,
        "user_id": user_id,
        "title": title,
        "desc": desc,
        "question": question,
        "options": options,            # चारों ऑप्शन्स
        "correct_option_id": correct_id # सही जवाब का नंबर (0-3)
    }
    quizzes_col.insert_one(data)
    return quiz_id

def get_quiz_by_id(quiz_id):
    return quizzes_col.find_one({"_id": quiz_id})
