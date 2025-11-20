import sqlite3
import os

def setup_database():
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop old messages table if exists
    cursor.execute('DROP TABLE IF EXISTS messages')

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            preferred_language TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            role TEXT
        )
    ''')

    # Create conversations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER,
            start_time DATETIME,
            end_time DATETIME,
            FOREIGN KEY (userid) REFERENCES users(id)
        )
    ''')

    # Create messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            sender TEXT NOT NULL,
            text_content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            feedback_type TEXT,
            feedback_comment TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    ''')

    # Create health_knowledge_base table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            title TEXT NOT NULL,
            content_english TEXT,
            content_hindi TEXT,
            keywords TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert sample data
    # Users
    cursor.execute('INSERT OR IGNORE INTO users (username, email, password, preferred_language, role) VALUES (?, ?, ?, ?, ?)',
                   ('john_doe', 'john@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'English', 'user'))
    cursor.execute('INSERT OR IGNORE INTO users (username, email, password, preferred_language, role) VALUES (?, ?, ?, ?, ?)',
                   ('jane_smith', 'jane@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Hindi', 'admin'))

    # Add another admin user
    cursor.execute('INSERT OR IGNORE INTO users (username, email, password, preferred_language, role) VALUES (?, ?, ?, ?, ?)',
                   ('admin_user', 'admin@wellbot.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'English', 'admin'))

    # Conversations
    cursor.execute('INSERT OR IGNORE INTO conversations (userid, start_time, end_time) VALUES (?, ?, ?)',
                   (1, '2023-10-01 10:00:00', '2023-10-01 10:30:00'))
    cursor.execute('INSERT OR IGNORE INTO conversations (userid, start_time, end_time) VALUES (?, ?, ?)',
                   (2, '2023-10-02 14:00:00', '2023-10-02 14:45:00'))

    # Messages
    cursor.execute('INSERT OR IGNORE INTO messages (conversation_id, sender, text_content, feedback_type, feedback_comment) VALUES (?, ?, ?, ?, ?)',
                   (1, 'user', 'Hello, I need health advice.', None, None))
    cursor.execute('INSERT OR IGNORE INTO messages (conversation_id, sender, text_content, feedback_type, feedback_comment) VALUES (?, ?, ?, ?, ?)',
                   (1, 'bot', 'Sure, what symptoms are you experiencing?', 'positive', 'Very helpful'))
    cursor.execute('INSERT OR IGNORE INTO messages (conversation_id, sender, text_content, feedback_type, feedback_comment) VALUES (?, ?, ?, ?, ?)',
                   (2, 'user', 'क्या मुझे फ्लू के लिए क्या करना चाहिए?', None, None))

    # Health Knowledge Base - Insert all entries from kb.json
    import json
    try:
        with open('kb.json', 'r', encoding='utf-8') as f:
            kb_data = json.load(f)

        # Clear existing entries first
        cursor.execute('DELETE FROM health_knowledge_base')

        # Define category mapping based on keywords
        def get_category(entry):
            title = entry.get('condition', '').lower()
            symptoms = ' '.join(entry.get('symptoms_en', [])).lower()

            if any(word in symptoms for word in ['fever', 'cough', 'cold', 'headache', 'pain', 'nausea']):
                return 'Symptoms'
            elif any(word in symptoms for word in ['diet', 'food', 'nutrition', 'meal']):
                return 'Nutrition'
            elif any(word in symptoms for word in ['exercise', 'walk', 'fitness', 'workout']):
                return 'Exercise'
            elif any(word in symptoms for word in ['stress', 'anxiety', 'depression', 'mental', 'mood']):
                return 'Mental Health'
            else:
                return 'General Health'

        for entry in kb_data:
            category = get_category(entry)
            title = entry.get('condition', '')
            content_en = entry.get('answer_en', '')
            content_hi = entry.get('answer_hi', '')
            keywords = ', '.join(entry.get('symptoms_en', []))

            cursor.execute('INSERT INTO health_knowledge_base (category, title, content_english, content_hindi, keywords) VALUES (?, ?, ?, ?, ?)',
                           (category, title, content_en, content_hi, keywords))

    except FileNotFoundError:
        # Fallback to sample data if kb.json not found
        cursor.execute('INSERT OR IGNORE INTO health_knowledge_base (category, title, content_english, content_hindi, keywords) VALUES (?, ?, ?, ?, ?)',
                       ('General Health', 'Staying Hydrated', 'Drink at least 8 glasses of water daily to stay hydrated.', 'स्वास्थ्य बनाए रखने के लिए प्रतिदिन कम से कम 8 गिलास पानी पिएं।', 'hydration, water, health'))
        cursor.execute('INSERT OR IGNORE INTO health_knowledge_base (category, title, content_english, content_hindi, keywords) VALUES (?, ?, ?, ?, ?)',
                       ('Nutrition', 'Balanced Diet', 'Eat a variety of fruits, vegetables, proteins, and grains for a balanced diet.', 'संतुलित आहार के लिए फलों, सब्जियों, प्रोटीन और अनाज का विविधता से सेवन करें।', 'diet, nutrition, food'))
        cursor.execute('INSERT OR IGNORE INTO health_knowledge_base (category, title, content_english, content_hindi, keywords) VALUES (?, ?, ?, ?, ?)',
                       ('Exercise', 'Daily Walking', 'Walk for at least 30 minutes daily to maintain good health.', 'अच्छा स्वास्थ्य बनाए रखने के लिए प्रतिदिन कम से कम 30 मिनट टहलें।', 'exercise, walking, fitness'))

    conn.commit()
    conn.close()

def insert_user(username, email, password, preferred_language='en', role='user'):
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path, timeout=10.0)  # Add timeout to avoid locks
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT OR IGNORE INTO users (username, email, password, preferred_language, role) VALUES (?, ?, ?, ?, ?)',
                       (username, email, password, preferred_language, role))
        user_id = cursor.lastrowid
        if user_id == 0:  # User already exists, get existing ID
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            result = cursor.fetchone()
            if result:
                user_id = result[0]
            else:
                # This shouldn't happen, but handle it gracefully
                user_id = None
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        user_id = None
    finally:
        conn.close()
    return user_id

def insert_conversation(userid, start_time=None):
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if start_time is None:
        start_time = 'CURRENT_TIMESTAMP'
    else:
        start_time = f"'{start_time}'"
    cursor.execute(f'INSERT INTO conversations (userid, start_time) VALUES (?, {start_time})', (userid,))
    conversation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return conversation_id

def insert_message(conversation_id, sender, text_content, feedback_type=None, feedback_comment=None):
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO messages (conversation_id, sender, text_content, feedback_type, feedback_comment)
        VALUES (?, ?, ?, ?, ?)
    ''', (conversation_id, sender, text_content, feedback_type, feedback_comment))

    message_id = cursor.lastrowid  # ✅ Get the auto-generated ID
    conn.commit()
    conn.close()
    return message_id  # ✅ Return message_id to app.py

def update_conversation_end_time(conversation_id):
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('UPDATE conversations SET end_time = CURRENT_TIMESTAMP WHERE id = ?', (conversation_id,))
    conn.commit()
    conn.close()

def get_user_by_email(email):
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_or_create_conversation(user_id):
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Get the latest conversation for this user that hasn't ended
    cursor.execute('SELECT id FROM conversations WHERE userid = ? AND end_time IS NULL ORDER BY start_time DESC LIMIT 1', (user_id,))
    conversation = cursor.fetchone()
    if conversation:
        conversation_id = conversation[0]
    else:
        # Create new conversation
        cursor.execute('INSERT INTO conversations (userid, start_time) VALUES (?, CURRENT_TIMESTAMP)', (user_id,))
        conversation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return conversation_id

def update_message_feedback(message_id, feedback_type, feedback_comment=None):
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('UPDATE messages SET feedback_type = ?, feedback_comment = ? WHERE id = ?', (feedback_type, feedback_comment, message_id))
    conn.commit()
    conn.close()

def get_feedback_stats():
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT feedback_type, COUNT(*) as count
        FROM messages
        WHERE sender = 'assistant' AND feedback_type IS NOT NULL
        GROUP BY feedback_type
    ''')
    stats = cursor.fetchall()
    conn.close()
    return dict(stats)

def get_common_queries():
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT text_content, COUNT(*) as count
        FROM messages
        WHERE sender = 'user'
        GROUP BY text_content
        ORDER BY count DESC
        LIMIT 10
    ''')
    queries = cursor.fetchall()
    conn.close()
    return queries

def get_kb_entries():
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM health_knowledge_base')
    entries = cursor.fetchall()
    conn.close()
    return entries

def add_kb_entry(category, title, content_english, content_hindi, keywords):
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO health_knowledge_base (category, title, content_english, content_hindi, keywords) VALUES (?, ?, ?, ?, ?)',
                   (category, title, content_english, content_hindi, keywords))
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return entry_id

def update_kb_entry(entry_id, category, title, content_english, content_hindi, keywords):
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('UPDATE health_knowledge_base SET category = ?, title = ?, content_english = ?, content_hindi = ?, keywords = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                   (category, title, content_english, content_hindi, keywords, entry_id))
    conn.commit()
    conn.close()

def delete_kb_entry(entry_id):
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM health_knowledge_base WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()

def count_total_users():
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    total = cursor.fetchone()[0]
    conn.close()
    return total

def count_total_conversations():
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(DISTINCT conversation_id) FROM messages')
    total = cursor.fetchone()[0]
    conn.close()
    return total

def count_total_messages():
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM messages')
    total = cursor.fetchone()[0]
    conn.close()
    return total

def get_positive_feedback_ratio():
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM messages WHERE feedback_type = "positive"')
    positive = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM messages WHERE feedback_type IS NOT NULL')
    total_feedback = cursor.fetchone()[0]
    conn.close()
    if total_feedback == 0:
        return 0
    return round((positive / total_feedback) * 100, 2)

def get_query_trends():
    """Get query trends over the last 7 days (weekly)"""
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get daily query counts for the last 7 days
    cursor.execute('''
        SELECT date(timestamp) as day,
                COUNT(*) as count
        FROM messages
        WHERE sender = 'user'
        GROUP BY day
        ORDER BY day
    ''')
    trends = cursor.fetchall()
    conn.close()

    # Convert to dict with day names
    day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    result = {}
    for day, count in trends:
        # Convert date to day name
        from datetime import datetime
        day_name = day_names[datetime.strptime(day, '%Y-%m-%d').weekday()]
        result[day_name] = count

    return result

def get_health_topics_stats():
    """Get statistics on health topics covered"""
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Analyze user messages for health topics
    cursor.execute('''
        SELECT text_content
        FROM messages
        WHERE sender = 'user'
    ''')
    user_messages = cursor.fetchall()
    conn.close()

    # Categorize messages by health topics
    topics = {
        'Symptoms': 0,
        'Self-care': 0,
        'Nutrition': 0,
        'Exercise': 0,
        'Mental Health': 0,
        'General Health': 0
    }

    symptom_keywords = ['symptom', 'pain', 'fever', 'cough', 'headache', 'nausea', 'tired', 'sick']
    selfcare_keywords = ['care', 'treatment', 'medicine', 'remedy', 'heal', 'recovery']
    nutrition_keywords = ['diet', 'food', 'eat', 'nutrition', 'meal', 'drink', 'water']
    exercise_keywords = ['exercise', 'walk', 'run', 'gym', 'fitness', 'workout', 'sport']
    mental_keywords = ['stress', 'anxiety', 'depression', 'mood', 'mental', 'mind', 'sleep']
    general_keywords = ['health', 'wellness', 'body', 'medical', 'doctor']

    total_messages = len(user_messages)

    for (message,) in user_messages:
        msg_lower = message.lower()

        if any(word in msg_lower for word in symptom_keywords):
            topics['Symptoms'] += 1
        elif any(word in msg_lower for word in selfcare_keywords):
            topics['Self-care'] += 1
        elif any(word in msg_lower for word in nutrition_keywords):
            topics['Nutrition'] += 1
        elif any(word in msg_lower for word in exercise_keywords):
            topics['Exercise'] += 1
        elif any(word in msg_lower for word in mental_keywords):
            topics['Mental Health'] += 1
        elif any(word in msg_lower for word in general_keywords):
            topics['General Health'] += 1

    # Convert to percentages
    if total_messages > 0:
        for topic in topics:
            topics[topic] = {
                'count': topics[topic],
                'percentage': round((topics[topic] / total_messages) * 100, 1)
            }

    return topics

def get_feedback_trends():
    """Get feedback trends over the last 7 days (positive and negative counts per day)"""
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get daily feedback counts for the last 7 days
    cursor.execute('''
        SELECT date(timestamp) as day, feedback_type, COUNT(*) as count
        FROM messages
        WHERE sender = 'assistant' AND feedback_type IS NOT NULL
        GROUP BY day, feedback_type
        ORDER BY day
    ''')
    trends = cursor.fetchall()
    conn.close()

    # Convert to dict with day names
    day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    result = {}
    for day, feedback_type, count in trends:
        from datetime import datetime
        day_name = day_names[datetime.strptime(day, '%Y-%m-%d').weekday()]
        if day_name not in result:
            result[day_name] = {'positive': 0, 'negative': 0}
        result[day_name][feedback_type] = count

    # Ensure all days are present
    for day in day_names:
        if day not in result:
            result[day] = {'positive': 0, 'negative': 0}

    return result

def get_recent_feedback():
    """Get recent feedback entries"""
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT m.feedback_type, m.feedback_comment, m.timestamp,
               u.text_content as user_message
        FROM messages m
        JOIN messages u ON m.conversation_id = u.conversation_id
            AND u.sender = 'user'
            AND u.timestamp < m.timestamp
        WHERE m.sender = 'assistant' AND m.feedback_type IS NOT NULL
        ORDER BY m.timestamp DESC
        LIMIT 10
    ''')
    feedback_data = cursor.fetchall()
    conn.close()

    recent_feedback = []
    for feedback_type, comment, timestamp, user_message in feedback_data:
        recent_feedback.append({
            'type': feedback_type,
            'comment': comment or f"{'Helpful' if feedback_type == 'positive' else 'Not helpful'} response about: {user_message[:50]}...",
            'timestamp': timestamp,
            'user_message': user_message[:50] + "..." if len(user_message) > 50 else user_message
        })

    return recent_feedback

if __name__ == "__main__":
    setup_database()
    print("Database setup complete with sample data.")