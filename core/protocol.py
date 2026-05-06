from cryptography.fernet import Fernet
import json

class Message():
    def __init__(self, encrypted_msg: bytes, key: str):
        f = Fernet(key.encode())
        self.msg = f.decrypt(encrypted_msg).decode()

        msg_parts = self.msg.split('|', 3)

        self.command = msg_parts[0]
        if msg_parts[1] == "NONE":
            self.jwt = None
        else:
            self.jwt = msg_parts[1]
        
        self.json = json.loads(msg_parts[2])

