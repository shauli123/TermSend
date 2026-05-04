import sqlite3
import hashlib
from pathlib import Path

class SeverManager():
    server_db_path = "server.db"
    
    def __init__(self):
        self.create_users_table()
    
    def create_users_table(self):
        cursor =  sqlite3.connect(self.server_db_path).cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT NOT NULL PRIMARY KEY UNIQUE,
                password_hash TEXT NOT NULL
            );
        """)

    def user_exists(self, username: str) -> bool:
        cursor =  sqlite3.connect(self.server_db_path).cursor()
        cursor.execute("""SELECT * FROM users WHERE username=?""", (username,))
        exists = len(cursor.fetchall()) > 0
        cursor.close()
        return exists
    
    def register_user(self, username: str, password: str):
        with sqlite3.connect(self.server_db_path) as conn:
            cursor = conn.cursor()
            if not self.user_exists(username):
                hashed_pass = hashlib.sha256()
                hashed_pass.update(password.encode())
                hashed_pass = hashed_pass.hexdigest()
                cursor.execute("INSERT INTO users VALUES (?, ?)", (username, hashed_pass))
                conn.commit()
            else:
                raise ValueError("Username already exists")
            cursor.close()
    
if __name__ == '__main__':
    SeverManager().register_user("Sm", "01")