import sqlite3
import hashlib
from pathlib import Path
import jwt
import datetime
import exceptions

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
                username TEXT NOT NULL PRIMARY KEY UNIQUE,
                password_hash TEXT NOT NULL
            );
        """)
            conn.commit()
        
    def create_pending_messages_table(self):
        with sqlite3.connect(self.SERVER_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_messages (
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (sender) REFERENCES users(username),
            FOREIGN KEY (receiver) REFERENCES users(username)
            );""")
            conn.commit()

    
    # Checks if user exists
    def user_exists(self, username: str) -> bool:
        cursor =  sqlite3.connect(self.SERVER_DB_PATH).cursor()
        cursor.execute("""SELECT * FROM users WHERE username=?""", (username,))
        exists = len(cursor.fetchall()) > 0
        cursor.close()
        return exists
    
    def register_user(self, username: str, password: str):
        with sqlite3.connect(self.SERVER_DB_PATH) as conn:
            cursor = conn.cursor()
            if not self.user_exists(username):
                hashed_pass = hashlib.sha256()
                hashed_pass.update(password.encode())
                hashed_pass = hashed_pass.hexdigest()
                cursor.execute("INSERT INTO users VALUES (?, ?)", (username, hashed_pass))
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

    def validate_jwt(self, token: str):
        try:
            decoded_payload = jwt.decode(token, self.JWT_SECRET_KEY, algorithms=["HS256"])
            return decoded_payload["user"]
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
    
if __name__ == '__main__':
    server = SeverManager()
    
    try:
        server.register_user("Sm", "01")
    except exceptions.UserError as e:
        print(e)
        
    try:
        print(server.login_user("Sm", "02"))
    except exceptions.UserError as e:
        print(e)
        
    try:
        print(server.login_user("Sm", "01"))
    except exceptions.UserError as e:
        print(e)
    
    