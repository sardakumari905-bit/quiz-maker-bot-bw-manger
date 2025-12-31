import pymongo
import certifi
from config import MONGO_URI

# कनेक्ट करना
try:
    client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client['QuizBotDB']
    quizzes_col = db['quizzes']
    print("✅ Database Connected!")
except Exception as e:
    print(f"❌ Error: {e}")

# Temporary memory for creation process
user_state = {}

# --- Save Function (Updated for Polls) ---
def save_new_quiz(user_id, title, desc, question, options, correct_id):
    # options: एक लिस्ट होगी ['Opt1', 'Opt2', 'Opt3', 'Opt4']
    # correct_id: सही जवाब का नंबर (0, 1, 2, या 3)
    
    quiz_id = f"quiz_{user_id}_{str(title).replace(' ', '')[:5]}"
    
    data = {
        "_id": quiz_id,
        "user_id": user_id,
        "title": title,
        "desc": desc,
        "question": question,
        "options": options,           # नई चीज़
        "correct_option_id": correct_id # नई चीज़
    }
    quizzes_col.insert_one(data)
    return quiz_id

def get_quiz_by_id(quiz_id):
    return quizzes_col.find_one({"_id": quiz_id})
