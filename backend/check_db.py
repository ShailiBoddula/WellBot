import sqlite3

conn = sqlite3.connect('chat_history.db')
c = conn.cursor()

c.execute('SELECT COUNT(*) FROM users')
users = c.fetchone()[0]
print('Users:', users)

c.execute('SELECT COUNT(*) FROM conversations')
conversations = c.fetchone()[0]
print('Conversations:', conversations)

c.execute('SELECT COUNT(*) FROM messages')
messages = c.fetchone()[0]
print('Messages:', messages)

c.execute('SELECT userid, COUNT(*) FROM conversations GROUP BY userid ORDER BY COUNT(*) DESC LIMIT 5')
print('Top users by conversations:')
for row in c.fetchall():
    print(row)

c.execute('SELECT COUNT(*) FROM conversations WHERE end_time IS NULL')
open_conversations = c.fetchone()[0]
print('Open conversations:', open_conversations)

c.execute('SELECT userid, COUNT(*) FROM conversations WHERE end_time IS NULL GROUP BY userid ORDER BY COUNT(*) DESC LIMIT 5')
print('Open conversations per user:')
for row in c.fetchall():
    print(row)

conn.close()