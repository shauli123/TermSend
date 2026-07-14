# TermSend

**TermSend** is a mail-like, tui & gui based self-hosted messaging system that uses: sockets, encryption and sqllite.

TermSend is built in Python 3.11+

**Demo Video:**
[Watch the video](https://youtu.be/CFBe1q23t8Q)


**Screenshot:**
![](https://cdn.hackclub.com/019e1b53-636c-738b-bdc3-43ae2fb8b7b5/image.png)


## Table of Contents

*   [Features](#features)
*   [Guide](#guide)
    *   [Setting up the environment (Server & Python Client)](#setting-up-the-environment)
    *   [Setting up Server](#setting-up-server)
    *   [Running & using client](#running--using-client)
    *   [Using GUI client](#using-gui-client)

## Features:

*   Log-in and Sign-Up
*   Sending encrypted messages using RSA
*   Receving & decrypting messages using RSA
*   JWT Auth
*   Search Messages
*   Custom Servers

## Guide

### **Setting up the environment**

Run the following commands:

```
# Clone the repo
git clone https://github.com/shauli123/TermSend.git
cd TermSend
```

```
# Create venv (Windows)
python -m venv venv
venv\Scripts\activate
```

```
# Create venv (Linux/MacOS)
python3 -m venv venv
source venv/bin/activate
```

```
# Installing the requirements
pip install -r requirements.txt
```

### **Setting up server**
In server.py change the SERVER_PORT to whatever port you would like!

Then to run the server run:
```
# On Windows
python server.py

# On Linux/Mac
python3 server.py
```

### **Running & using client**
Run client.py using python
then this menu will pop-up

#### Connecting to server
```
Choose an option:
        1. Stay on localhost:5050 server.
        2. Connect to a different server.
Enter your choice: 
```
if the default server runs on your pc(for testing) press 1.
else connect to the server you will be using by pressing 2 nad entering the server ip & port

#### Login / Signup
if connected successfully you will be prompted with this menu:
```
Choose an option:
        1. Sign Up to a new account.
        2. Sign In to an existing account.
Enter your choice: 
```

you can create a new account or login to an already existing account.
if you sign up you will be auto logged in.
when something went wrong an error will pop-up and ask you to fill again.

#### Using the client
this is the action menu do as you want
```
Choose an option:
        1. Send a message.
        2. Show all messages.
        3. Show all messages from a specific user.
        4. Show all messages containing a string.
        5. Show recent messages.
        6. Exit the program.
Enter your choice:
```
for each option if it needs more data it will ask for it
for example option 3 asks for a username

### Using GUI Client
so it is pretty easy and it has stages like the tui client
#### Stage 1 - Server connection
Enter your TermSend server ip & port and press connect!
If you got an error do as prompted!

#### Stage 2 - Login/Signup
After you connected to the server you need to login/signup
To login: Enter your username and password as normal and press login
To signup: Enter your new username and password and press signup
if you got an error do as prompted!

#### Stage 3 - Using the system
Now you will see that you are in the system and there is 2 tabs:
* Main - the main tab is used to see & search msgs and threads and reply to them
* Send - the send tab lets you send a new msg in a new thread!

