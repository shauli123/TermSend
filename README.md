# TermSend

**TermSend** is a mail-like, tui based messging system that uses: sockets, encryption and sqllite.

TermSend is built in Python

**Screenshot:**

![](https://cdn.hackclub.com/019e1b53-636c-738b-bdc3-43ae2fb8b7b5/image.png)

## Table of Contents

*   [Features](#features)
*   [Guide](#guide)
    *   [Setting up the environment (Server & Python Client)](#setting-up-the-environment)
    *   [Setting up Server](#setting-up-server)
    *   [Running & using client](#running--using-client)
*   [Setting up the environment](#setting-up-the-environment)

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