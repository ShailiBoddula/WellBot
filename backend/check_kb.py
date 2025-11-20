import sqlite3

def check_kb():
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()

    # Count entries
    cursor.execute('SELECT COUNT(*) FROM health_knowledge_base')
    count = cursor.fetchone()[0]
    print(f'Total KB entries: {count}')

    # Show sample entries
    cursor.execute('SELECT category, title FROM health_knowledge_base LIMIT 10')
    entries = cursor.fetchall()
    print('\nSample entries:')
    for category, title in entries:
        print(f'{category}: {title}')

    # Show categories distribution
    cursor.execute('SELECT category, COUNT(*) FROM health_knowledge_base GROUP BY category')
    categories = cursor.fetchall()
    print('\nCategories distribution:')
    for category, count in categories:
        print(f'{category}: {count} entries')

    conn.close()

if __name__ == "__main__":
    check_kb()