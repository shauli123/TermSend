import client_network
import sqlite3
import os

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

def print_banner():
    C1 = "\033[38;5;45m"
    C2 = "\033[38;5;208m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    logo = [
        (r"  _____                     ", r"____                _ "),
        (r" |_   _|__ _ __ _ __ ___  ", r"/ ___|  ___ _ __   __| |"),
        (r"   | |/ _ \ '__| '_ ` _ \ ", r"\___ \ / _ \ '_ \ / _` |"),
        (r"   | |  __/ |  | | | | | |", r" ___) |  __/ | | | (_| |"),
        (r"   |_|\___|_|  |_| |_| |_|", r"|____/ \___|_| |_|\__,_|")
    ]

    slogan = ">> Secure TUI Messaging: Simple. Encrypted. RSA-Hardened. <<"

    try:
        columns = os.get_terminal_size().columns
    except OSError:
        columns = 80

    for part1, part2 in logo:
        full_line = part1 + part2
        padding = (columns - len(full_line)) // 2
        print(" " * padding + f"{C1}{BOLD}{part1}{C2}{part2}{RESET}")

    print(f"{C1}{BOLD}{slogan.center(columns)}{RESET}")
    
def main():
    print_banner()

if __name__ == '__main__':
    main()