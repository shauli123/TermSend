import sqlite3
import hashlib
from pathlib import Path
import jwt
import datetime
import exceptions
import base64
from cryptography.fernet import Fernet

class SeverManager():
    SERVER_DB_PATH = "server.db"
    JWT_SECRET_KEY = "TermSendSh11-Secret-Key-32-Bytes"

    def __init__(self):
        self.create_users_table()
        self.create_pending_messages_table()
    
    # DB Init Functions
    def create_users_table(self):
        with sqlite3.connect(self.SERVER_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                public_key TEXT NOT NULL,
                encrypted_private_key TEXT NOT NULL
            );""")
            conn.commit()
        
    def create_pending_messages_table(self):
        with sqlite3.connect(self.SERVER_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_messages (
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            content TEXT NOT NULL,
            date TEXT DEFAULT (datetime('now', 'localtime')), 
            FOREIGN KEY (sender) REFERENCES users(username),
            FOREIGN KEY (receiver) REFERENCES users(username)
            );""")
            conn.commit()

    
    # User related functions
    def user_exists(self, username: str) -> bool:
        cursor =  sqlite3.connect(self.SERVER_DB_PATH).cursor()
        cursor.execute("""SELECT * FROM users WHERE username=?""", (username,))
        exists = len(cursor.fetchall()) > 0
        cursor.close()
        return exists
    
    def register_user(self, username: str, password: str, public_key: str, encrypted_private_key: str):
        with sqlite3.connect(self.SERVER_DB_PATH) as conn:
            cursor = conn.cursor()
            if not self.user_exists(username):
                hashed_pass = hashlib.sha256()
                hashed_pass.update(password.encode())
                hashed_pass = hashed_pass.hexdigest()
                cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (username, hashed_pass, public_key, encrypted_private_key))
                conn.commit()
            else:
                raise exceptions.UserAlreadyExists("Username already exists!")
            cursor.close()
    
    def create_jwt(self, username: str) -> str:
        payload = {
            "user": username,
            "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1, minutes=30)
        }
        return jwt.encode(payload, self.JWT_SECRET_KEY, algorithm="HS256")

    def get_jwt_user(self, token: str):
        try:
            decoded_payload = jwt.decode(token, self.JWT_SECRET_KEY, algorithms=["HS256"])
            if self.user_exists(decoded_payload["user"]):
                return decoded_payload["user"]
            else:
                raise exceptions.TokenError("Invalid token!")
        except jwt.ExpiredSignatureError:
            raise exceptions.TokenError("Login had expired! Re-log to continue!")
        except jwt.InvalidTokenError:
            raise exceptions.TokenError("Invalid token!")
            
    def login_user(self, username: str, password: str) -> str:
        with sqlite3.connect(self.SERVER_DB_PATH) as conn:
            cursor = conn.cursor()
            if self.user_exists(username):
                hashed_pass = hashlib.sha256()
                hashed_pass.update(password.encode())
                hashed_pass = hashed_pass.hexdigest()
                cursor.execute("SELECT 1 FROM users WHERE username = ? AND password_hash = ?;", (username, hashed_pass))
                result = cursor.fetchone()
                if result:
                    cursor.close()
                    return self.create_jwt(username)
                else:
                    raise exceptions.InvalidCredentials("Incorrect password or username!")
            else:
                raise exceptions.InvalidCredentials("Incorrect password or username!")
    
    def get_public_key_user(self, username: str):
        with sqlite3.connect(self.SERVER_DB_PATH) as conn:
            cursor = conn.cursor()
            if self.user_exists(username):
                cursor.execute("SELECT public_key FROM users WHERE username=?", (username,))
                public_key = cursor.fetchone()[0]
                return public_key
            else:
                raise exceptions.UserDoesntExist("The user you are trying to get his public key!")
    
    def get_private_key_user(self, token: str):
        with sqlite3.connect(self.SERVER_DB_PATH) as conn:
            cursor = conn.cursor()
            username = self.get_jwt_user(token)
            cursor.execute("SELECT encrypted_private_key FROM users WHERE username=?", (username,))
            private_key = cursor.fetchone()[0]
            return private_key


    # Msg related functions
    def pend_message(self, token: str, receiver: str, message: str):
        with sqlite3.connect(self.SERVER_DB_PATH) as conn:
            cursor = conn.cursor()
            sender = self.get_jwt_user(token)
            if self.user_exists(receiver):
                cursor.execute("""
                INSERT INTO pending_messages (sender, receiver, content)
                VALUES (?, ?, ?)
                """, (sender, receiver, message))
                conn.commit()
            else:
                raise exceptions.UserDoesntExist("The user you are trying to send to doesn't exist!")

    def get_pending_messages(self, token: str):
        with sqlite3.connect(self.SERVER_DB_PATH) as conn:
            username = self.get_jwt_user(token)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM pending_messages WHERE receiver = ?", (username,))
            messages = [dict(row) for row in cursor.fetchall()]
            
            if messages:
                cursor.execute("DELETE FROM pending_messages WHERE receiver = ?", (username,))
                conn.commit()
        
            return messages

if __name__ == '__main__':
    # Testing the server!
    server = SeverManager()
    
    print("--- Starting Server Manager Test ---\n")

    
    