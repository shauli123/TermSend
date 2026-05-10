import client_network
import sqlite3

private_key = None
CLIENT_DB_PATH = 'client.db'

def fetch_and_get_all_msgs(token):
    if private_key is None:
        return []

    new_msgs = client_network.receive_msgs(token)

    with sqlite3.connect(CLIENT_DB_PATH) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS msgs (
                sender TEXT NOT NULL,
                content TEXT NOT NULL,
                date TEXT
            );""")

        if new_msgs:
            for msg in new_msgs:
                cursor.execute("""
                    INSERT INTO msgs (sender, content, date) 
                    VALUES (?, ?, ?)
                """, (msg['sender'], msg['content'], msg['date']))
            conn.commit()

        cursor.execute("SELECT sender, content, date FROM msgs")
        rows = cursor.fetchall()

        all_messages = []
        for row in rows:
            all_messages.append({
                "sender": row[0],
                "content": row[1],
                "date": row[2]
            })

        return all_messages

