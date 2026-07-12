import client_network
import os
import exceptions
import ipaddress
import socket
from rich.console import Console
from rich.markdown import Markdown
import client_util

        
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
                    try:
                        ipaddress.IPv6Address(ip)
                    except ValueError:
                        print("Not a valid ip! Try again!")
                    else:
                        client_network.SERVER_IP = ip
                        client_network.SOCK_FAMILY = socket.AF_INET6
                        break
                else:
                    client_network.SERVER_IP = ip
                    client_network.SOCK_FAMILY = socket.AF_INET
                    break
                    
            port = -1
            while not 0 <= port <= 65535:
                tmp = input("Enter the server's port: ")
                try:
                    port = int(tmp)
                except:
                    print("Try again!")
                    
            client_network.SERVER_PORT = port
        if client_util.check_connection(client_network.SERVER_IP, client_network.SERVER_PORT, client_network.SOCK_FAMILY):
            is_ok = True
            print("Connected to server successfully!")
        else:
            print("Cannot connect to server! try again!")
            is_ok = False
        


def login_register_menu():
    token = None
    
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
                    token, client_util.private_key = client_network.login(username, password)
                    finished = True
        elif option == 2:
            username = input("Enter a username: ")
            password = input("Enter a password: ")
            
            try:
                token, client_util.private_key = client_network.login(username, password)
            except Exception as e:
                    print(f"Error: {e}")
            else:
                finished = True

                    
    print(f"Logged in into {username}.")
    client_util.current_username = username
    client_util.current_password = password
    return token

def send_msg(token):
    receiver = input("Enter the recipient: ")
    
    thread_id = int(input("Enter Thread ID (if it is a new msg enter -1): "))
    if thread_id == -1:
        thread_id = None
        
    print("Enter your message (you can use md) (type a blank new line to finish):")
    text = []
    while True:
        line = input()
        if line == "":
            break
        text.append(line)
    text = "\n".join(text)

    while True:
        try:
            res = client_network.send_msg(token, receiver, text, thread_id)
            if receiver != client_util.current_username:
                client_util.insert_msg_to_db(client_util.current_username, receiver, text, res['thread_id'])
        except exceptions.UserDoesntExist as e:
            print("Recipient Doesnt Exist! Try Again!")
            receiver = input("Enter the recipient: ")
        else:
            break
        
def print_msg(msg: dict):
    print(f"Sender: {msg['sender']}")
    print(f"Recipient: {msg['receiver']}")
    print(f"Date: {msg['date']}")
    print(f"Thread ID: {msg['thread_id']}")
    Console().print(Markdown(msg['content']))
    print('-'*30)

def show_all_messages(token):
    msgs = client_util.fetch_and_get_all_msgs(token)
    for msg in msgs:
        print_msg(msg)

def show_msgs_from_user(token):
    sender = input("Enter the sender to search: ")
    msgs = client_util.fetch_and_get_all_msgs(token)
    
    for msg in msgs:
        if msg['sender'] == sender:
            print_msg(msg)

def show_all_msgs_with_str(token):
    string = input("Enter the string to search: ")
    msgs = client_util.fetch_and_get_all_msgs(token)
    
    for msg in msgs:
        if string in msg['content']:
            print_msg(msg)
            
def show_recent_msgs(token):
    msgs = client_util.fetch_and_get_all_msgs(token)
    amount = 0

    while True:
        try:
            amount = int(input("Enter how many recent message to show: "))
        except ValueError as e:
            print("NaN! Try again!")
        else:
            if(len(msgs) < amount):
                print(f"There are only {len(msgs)}! Try Again!")
            else:
                break
    msgs = msgs[::-1]     
    for msg in msgs[:amount]:
        print_msg(msg)
        
def show_all_msgs_in_thread(token):
    try:
        id = int(input("Enter the Thread ID to search: "))
    except:
        print("Not a number, try again later!")
        
    msgs = client_util.fetch_and_get_all_msgs(token)
    
    for msg in msgs:
        if msg['thread_id'] == id:
            print_msg(msg)
            
def main():
    option_list = {
        1: send_msg,
        2: show_all_messages,
        3: show_msgs_from_user,
        4: show_all_msgs_with_str,
        5: show_recent_msgs,
        6: show_all_msgs_in_thread,
        7: None
    }
    print_banner()
    choose_server()
    token = login_register_menu()
    while True:
        print("Choose an option:")
        print("\t1. Send a message.")
        print("\t2. Show all messages.")
        print("\t3. Show all messages from a specific user.")
        print("\t4. Show all messages containing a string.")
        print("\t5. Show recent messages.")
        print("\t6. Show replay thread.")
        print("\t7. Exit the program.")
       
        option = 0
        while option not in option_list.keys():
            try:
                option = int(input("Enter your choice: "))
            except ValueError as e:
                print("Try again!")
        
        if option_list[option] == None:
            break
        
        try:
            option_list[option](token)
        except exceptions.TokenError as e:
            print("Your session has expired! Please Re-login!")
            token = login_register_menu()
        except Exception as e:
            print(f"An error occurred!\nError: {e}.\nplease try again later! ")
        

if __name__ == '__main__':
    main()