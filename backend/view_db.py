import sqlite3
import os
import sys
import io

# Set stdout to handle UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def view_database():
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    if not os.path.exists(db_path):
        print("Database file does not exist.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = ['users', 'conversations', 'messages', 'health_knowledge_base']

    for table in tables:
        print(f"\n=== {table.upper()} TABLE ===")
        try:
            cursor.execute(f'SELECT * FROM {table} ORDER BY id DESC LIMIT 10')
            rows = cursor.fetchall()
            if not rows:
                print(f"No records found in {table}.")
            else:
                # Get column names
                cursor.execute(f'PRAGMA table_info({table})')
                columns = [col[1] for col in cursor.fetchall()]
                print(f"Columns: {', '.join(columns)}")
                print("-" * 80)
                for row in rows:
                    for i, col in enumerate(columns):
                        value = row[i]
                        if isinstance(value, str):
                            value = value.encode('utf-8').decode('utf-8', errors='replace')
                        print(f"{col}: {value}")
                    print("-" * 80)
        except sqlite3.OperationalError as e:
            print(f"Error accessing {table}: {e}")

    conn.close()

if __name__ == "__main__":
    view_database()