import client_network
import sqlite3
import os
import exceptions
import ipaddress
import socket

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

def check_connection(host: str, port: int, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
        return True
    except (socket.timeout, socket.error):
        return False
    
def choose_server():
    is_ok = False
    while not is_ok:
        print("Choose an option:")
        print("\t1. Stay on localhost:5050 server.")
        print("\t2. Connect to a different server.")
        option = 0
        while option not in [1,2]:
                try:
                    option = int(input("Enter your choice: "))
                except ValueError as e:
                    print("Try again!")
        
        if option == 2:
            while True:
                ip = input("Enter the server's ip: ")
                try:
                    ipaddress.IPv4Address(ip)
                except ValueError:
                    print("Not a valid ip! Try again!")
                else:
                    client_network.SERVER_IP = ip
                    break
                    
            port = -1
            while not 0 <= port <= 65535:
                tmp = input("Enter the server's port: ")
                try:
                    port = int(tmp)
                except:
                    print("Try again!")
                    
            client_network.SERVER_PORT = port
        if check_connection(client_network.SERVER_IP, client_network.SERVER_PORT):
            is_ok = True
            print("Connected to server successfully!")
        else:
            print("Cannot connect to server! try again!")
            is_ok = False
        


def login_register_menu():
    token = None
    global private_key
    while not token:
        print("Choose an option:")
        print("\t1. Sign Up to a new account.")
        print("\t2. Sign In to an existing account.")
        option = 0
        while option not in [1,2]:
            try:
                option = int(input("Enter your choice: "))
            except ValueError as e:
                print("Try again!")
        
        finished = False
        if option == 1:
            while not finished:
                username = input("Enter a username: ")
                password = input("Enter a password: ")
                
                try:
                    client_network.register(username, password)
                except Exception as e:
                    print(f"Error: {e}")
                else:
                    token, private_key = client_network.login(username, password)
                    finished = True
        elif option == 2:
            username = input("Enter a username: ")
            password = input("Enter a password: ")
            
            try:
                token, private_key = client_network.login(username, password)
            except Exception as e:
                    print(f"Error: {e}")
            else:
                finished = True

                    
    print(f"Logged in into {username}.")
    return token


def main():
    print_banner()
    choose_server()
    token = login_register_menu()
    while True:
        # print("Choose an option:")
        # print("\t1. Send a message.")
        # print("\t2. Show all messages.")
        # print("\t3. Show all messages from a specific user.")
        # print("\t4. Show all messages containing a string.")
        # print("\t5. Exit the program.")
        pass

        

if __name__ == '__main__':
    main()