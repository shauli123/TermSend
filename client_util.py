import client_network
import sqlite3
import socket
import hashlib
import base64
from cryptography.fernet import Fernet
from datetime import datetime

private_key = None
current_username = None
current_password = None

CLIENT_DB_PATH = 'client.db'

def fetch_and_get_all_msgs(token):
    global private_key
    global current_username
    global current_password

    if private_key is None:
        return []

    new_msgs = client_network.receive_msgs(token, private_key)
    
    
    hashed = hashlib.sha256(f"{current_username}.{current_password}".encode()).digest()
    key = Fernet(base64.urlsafe_b64encode(hashed))
    
    with sqlite3.connect(CLIENT_DB_PATH) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS msgs (
                sender TEXT NOT NULL,
                receiver TEXT NOT NULL,
                user TEXT NOT NULL,
                content BLOB NOT NULL,
                thread_id INTEGER NOT NULL,
                date TEXT
            );""")

        if new_msgs:
            for msg in new_msgs:
                cursor.execute("""
                    INSERT INTO msgs (user, sender, content, date, receiver, thread_id) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (current_username, msg['sender'], key.encrypt(msg['content'].encode()), msg['date'], current_username, msg['thread_id']))
            conn.commit()

        cursor.execute("SELECT sender, receiver, content, date, thread_id FROM msgs WHERE user=?", (current_username,))
        rows = cursor.fetchall()

        all_messages = []
        for row in rows:
            all_messages.append({
                "sender": row[0],
                "receiver": row[1],
                "content": key.decrypt(row[2]).decode('utf-8'),
                "date": row[3],
                "thread_id": row[4]
            })
        
        unique_messages = [dict(t) for t in {tuple(d.items()) for d in all_messages}]
        unique_messages.sort(key=lambda x: x["date"])
        
        return unique_messages

def insert_msg_to_db(sender, receiver, content, thread_id, date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
    with sqlite3.connect(CLIENT_DB_PATH) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
           CREATE TABLE IF NOT EXISTS msgs (
               sender TEXT NOT NULL,
               receiver TEXT NOT NULL,
               user TEXT NOT NULL,
               content BLOB NOT NULL,
               thread_id INTEGER NOT NULL,
               date TEXT
           );""")
        
        hashed = hashlib.sha256(f"{current_username}.{current_password}".encode()).digest()
        key = Fernet(base64.urlsafe_b64encode(hashed))
        cursor.execute("""
            INSERT INTO msgs (user, sender, content, date, receiver, thread_id) 
            VALUES (?, ?, ?, ?, ?, ?)
            """, (current_username, sender, key.encrypt(content.encode()), date, receiver, thread_id))
        conn.commit()
        
def check_connection(host: str, port: int, sock_family, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        with socket.socket(sock_family, socket.SOCK_STREAM) as s:
            s.connect((host, port))
        return True
    except (socket.timeout, socket.error):
        return False
