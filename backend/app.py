from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime
import jwt
import hashlib
import os
import sqlite3

from advanced_nlu import SimpleNLU
from db_setup import (
    get_user_by_email, insert_user, get_or_create_conversation, insert_message,
    update_message_feedback, get_feedback_stats, get_common_queries,
    get_kb_entries, add_kb_entry, update_kb_entry, delete_kb_entry,
    count_total_users, count_total_conversations, count_total_messages, get_positive_feedback_ratio,
    get_query_trends, get_health_topics_stats, get_recent_feedback, get_feedback_trends
)

app = Flask(__name__)
CORS(app)

# Secret key for JWT
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Load knowledge base
with open('kb.json', 'r', encoding='utf-8') as f:
    knowledge_base = json.load(f)

nlu = SimpleNLU()

# ---------------- Helper: KB response based on message ----------------
def get_kb_reply(item, message, language="en"):
    msg_lower = message.lower()

    symptoms_keywords = ["symptom", "sign", "लक्षण", "संकेत"]
    selfcare_keywords = ["self-care", "care", "treatment", "देखभाल", "उपचार"]
    doctor_keywords = ["doctor", "seek doctor", "visit", "डॉक्टर", "संपर्क"]

    if any(word in msg_lower for word in symptoms_keywords):
        field = f"symptoms_{language}"
        reply = ", ".join(item.get(field, []))
    elif any(word in msg_lower for word in selfcare_keywords):
        field = f"self_care_{language}"
        reply = ", ".join(item.get(field, []))
    elif any(word in msg_lower for word in doctor_keywords):
        field = f"when_to_seek_doctor_{language}"
        reply = ", ".join(item.get(field, []))
    else:
        field = f"answer_{language}"
        reply = item.get(field, "")

    return reply

# ---------------- Fallback response ----------------
def generate_response(intent, entities, language):
    responses = {
        "greeting": {
            "en": "Hello! How can I assist with your wellness?",
            "hi": "नमस्ते! मैं आपकी सेहत में कैसे मदद कर सकता हूँ?"
        },
        "symptom_query": {
            "en": "I understand you're experiencing symptoms. Can you tell me more?",
            "hi": "मैं समझता हूँ कि आप कुछ लक्षण महसूस कर रहे हैं। कृपया और बताएं।"
        },
        "fallback": {
            "en": "I'm here to help with wellness and health questions. What would you like to know?",
            "hi": "मैं आपकी स्वास्थ्य और वेलनेस में मदद करने के लिए यहां हूँ। आप क्या जानना चाहेंगे?"
        }
    }
    if intent in responses:
        return responses[intent].get(language, responses[intent]["en"])
    return responses["fallback"][language]

# ---------------- JWT helpers ----------------
def generate_token(email):
    payload = {'email': email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)}
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['email']
    except:
        return None

# ---------------- Password hashing ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def correct_password(stored_password, input_password):
    hashed_input = hashlib.sha256(input_password.encode()).hexdigest()
    return stored_password == input_password or stored_password == hashed_input

# ---------------- AUTH ROUTES ----------------
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email, password = data.get("email"), data.get("password")
    if not email or not password:
        return jsonify({"error": "Email & password required"}), 400

    user = get_user_by_email(email)
    if user and correct_password(user[3], password):
        return jsonify({"token": generate_token(email)})

    # Auto-create user as admin (all users get full access)
    insert_user(email.split("@")[0], email, hash_password(password), role='admin')
    return jsonify({"token": generate_token(email)})

@app.route('/auth/validate', methods=['GET'])
def validate():
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"valid": False}), 401
    token = auth.split(" ")[1]
    if verify_token(token):
        return jsonify({"valid": True})
    return jsonify({"valid": False}), 401

# ---------------- CHAT ROUTE ----------------
@app.route('/chat', methods=['POST'])
def chat():
    # Validate token
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error": "Token required"}), 401
    token = auth.split(" ")[1]
    email = verify_token(token)
    if not email:
        return jsonify({"error": "Invalid/Expired token"}), 401

    data = request.get_json()
    message = data.get("message", "").strip()
    language = data.get("language", "en")

    if not message:
        return jsonify({"reply": "Please enter a message"}), 400

    # DB conversation logging
    user = get_user_by_email(email)
    convo_id = get_or_create_conversation(user[0])
    insert_message(convo_id, "user", message)

    # Parse intent/entities
    parsed = nlu.parse(message)
    intent = parsed.get("intent", "fallback")
    entities = parsed.get("entities", {})

    # --- KB lookup ---
    msg_lower = message.lower()
    found = None
    for item in knowledge_base:
        keywords_en = item.get("symptoms_en", []) + [item.get("condition","").lower()]
        keywords_hi = item.get("symptoms_hi", []) + [item.get("condition_hi","").lower()]
        if language == "hi" and any(word in msg_lower for word in keywords_hi):
            found = item
            break
        elif language == "en" and any(word in msg_lower for word in keywords_en):
            found = item
            break

    # --- Generate reply ---
    if found:
        reply = get_kb_reply(found, message, language)
    else:
        reply = generate_response(intent, entities, language)

    # Add disclaimer
    disclaimer = (
        "\n\n⚠️ Please note: This is not medical advice. Consult a healthcare professional for personalized guidance."
        if language == "en"
        else "\n\n⚠️ कृपया ध्यान दें: यह चिकित्सा सलाह नहीं है। व्यक्तिगत मार्गदर्शन के लिए स्वास्थ्य देखभाल पेशेवर से परामर्श करें।"
    )
    reply += disclaimer

    message_id = insert_message(convo_id, "assistant", reply)
    return jsonify({"reply": reply, "message_id": message_id}), 200

# ---------------- FEEDBACK ROUTES ----------------
@app.route('/feedback', methods=['POST'])
def submit_feedback():
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error": "Token required"}), 401
    token = auth.split(" ")[1]
    email = verify_token(token)
    if not email:
        return jsonify({"error": "Invalid/Expired token"}), 401

    data = request.get_json()
    message_id = data.get("message_id")
    feedback_type = data.get("feedback_type")  # 'positive' or 'negative'
    feedback_comment = data.get("feedback_comment", "")

    if not message_id or not feedback_type:
        return jsonify({"error": "message_id and feedback_type required"}), 400

    update_message_feedback(message_id, feedback_type, feedback_comment)
    return jsonify({"message": "Feedback submitted successfully"}), 200

# ---------------- ADMIN ROUTES ----------------
@app.route('/admin/stats', methods=['GET'])
def get_admin_stats():
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error": "Token required"}), 401
    token = auth.split(" ")[1]
    email = verify_token(token)
    if not email:
        return jsonify({"error": "Invalid/Expired token"}), 401

    user = get_user_by_email(email)
    if not user:
        return jsonify({"error": "Invalid user"}), 403

    try:
        total_users = count_total_users()
        total_conversations = count_total_conversations()
        total_messages = count_total_messages()
        positive_feedback = get_positive_feedback_ratio()
        feedback_stats = get_feedback_stats()
        common_queries = get_common_queries()

        # Get additional analytics data
        query_trends = get_query_trends()
        health_topics = get_health_topics_stats()
        recent_feedback = get_recent_feedback()
        feedback_trends = get_feedback_trends()

        return jsonify({
            "status": "success",
            "total_users": total_users,
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "positive_feedback": f"{positive_feedback}%",
            "feedback_stats": feedback_stats,
            "common_queries": common_queries,
            "query_trends": query_trends,
            "health_topics": health_topics,
            "recent_feedback": recent_feedback,
            "feedback_trends": feedback_trends
        })
    except Exception as e:
        print(f"Error fetching admin stats: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/admin/kb', methods=['GET'])
def get_kb():
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error": "Token required"}), 401
    token = auth.split(" ")[1]
    email = verify_token(token)
    if not email:
        return jsonify({"error": "Invalid/Expired token"}), 401

    user = get_user_by_email(email)
    if not user:
        return jsonify({"error": "Invalid user"}), 403

    entries = get_kb_entries()
    return jsonify({"entries": entries}), 200

@app.route('/admin/kb', methods=['POST'])
def add_kb():
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error": "Token required"}), 401
    token = auth.split(" ")[1]
    email = verify_token(token)
    if not email:
        return jsonify({"error": "Invalid/Expired token"}), 401

    user = get_user_by_email(email)
    if not user:
        return jsonify({"error": "Invalid user"}), 403

    data = request.get_json()
    category = data.get("category")
    title = data.get("title")
    content_english = data.get("content_english")
    content_hindi = data.get("content_hindi")
    keywords = data.get("keywords")

    if not all([category, title, content_english, content_hindi, keywords]):
        return jsonify({"error": "All fields required"}), 400

    entry_id = add_kb_entry(category, title, content_english, content_hindi, keywords)
    return jsonify({"message": "KB entry added", "id": entry_id}), 201

@app.route('/admin/kb/<int:entry_id>', methods=['PUT'])
def update_kb(entry_id):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error": "Token required"}), 401
    token = auth.split(" ")[1]
    email = verify_token(token)
    if not email:
        return jsonify({"error": "Invalid/Expired token"}), 401

    user = get_user_by_email(email)
    if not user:
        return jsonify({"error": "Invalid user"}), 403

    data = request.get_json()
    category = data.get("category")
    title = data.get("title")
    content_english = data.get("content_english")
    content_hindi = data.get("content_hindi")
    keywords = data.get("keywords")

    if not all([category, title, content_english, content_hindi, keywords]):
        return jsonify({"error": "All fields required"}), 400

    update_kb_entry(entry_id, category, title, content_english, content_hindi, keywords)
    return jsonify({"message": "KB entry updated"}), 200

@app.route('/admin/kb/<int:entry_id>', methods=['DELETE'])
def delete_kb(entry_id):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error": "Token required"}), 401
    token = auth.split(" ")[1]
    email = verify_token(token)
    if not email:
        return jsonify({"error": "Invalid/Expired token"}), 401

    user = get_user_by_email(email)
    if not user or user[6] != 'admin':
        return jsonify({"error": "Admin access required"}), 403

    delete_kb_entry(entry_id)
    return jsonify({"message": "KB entry deleted"}), 200

# ---------------- PROFILE ROUTES ----------------
@app.route('/profile', methods=['PUT'])
def update_profile():
    return jsonify({"message": "Profile updated"})

@app.route('/user/stats', methods=['GET'])
def get_user_stats():
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error": "Token required"}), 401
    token = auth.split(" ")[1]
    email = verify_token(token)
    if not email:
        return jsonify({"error": "Invalid/Expired token"}), 401

    user = get_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 401

    user_id = user[0]

    # Get user's personal stats
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get user's conversations count
    cursor.execute('SELECT COUNT(*) FROM conversations WHERE userid = ?', (user_id,))
    conversations_count = cursor.fetchone()[0]

    # Get user's messages count
    cursor.execute('''
        SELECT COUNT(*) FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        WHERE c.userid = ?
    ''', (user_id,))
    messages_count = cursor.fetchone()[0]

    # Get user's feedback stats
    cursor.execute('''
        SELECT feedback_type, COUNT(*) as count
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        WHERE c.userid = ? AND m.sender = 'assistant' AND m.feedback_type IS NOT NULL
        GROUP BY feedback_type
    ''', (user_id,))
    feedback_stats = dict(cursor.fetchall())

    # Get user's common queries
    cursor.execute('''
        SELECT text_content, COUNT(*) as count
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        WHERE c.userid = ? AND m.sender = 'user'
        GROUP BY text_content
        ORDER BY count DESC
        LIMIT 5
    ''', (user_id,))
    common_queries = cursor.fetchall()

    conn.close()

    return jsonify({
        "conversations_count": conversations_count,
        "messages_count": messages_count,
        "feedback_stats": feedback_stats,
        "common_queries": common_queries,
        "is_admin": user[6] == 'admin' if len(user) > 6 else False
    }), 200

@app.route('/profile', methods=['GET'])
def get_profile():
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error": "Token missing"}), 401

    token = auth.split(" ")[1]
    email = verify_token(token)
    if not email:
        return jsonify({"error": "Invalid token"}), 401

    user = get_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "email": user[2],
        "name": user[1],
        "language": "en"  # can store user language if needed
    }), 200

# ---------------- MAIN ----------------
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
