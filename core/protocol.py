from cryptography.fernet import Fernet
import json
from enum import StrEnum, IntEnum, Enum, auto
import exceptions

class Side(Enum):
    SERVER = auto()
    CLIENT = auto()

class ServerCommands(StrEnum):
    REGISTER = "REGISTER"
    LOGIN = "LOGIN"
    GET_PUBLIC_KEY = "GET_PUBLIC_KEY"
    SEND_MSG = "SEND_MSG"
    RECIEVE_MSGS = "RECIEVE_MSGS"
    
class ServerStatus(IntEnum):
    # Status OK
    OK = 200
    SENT = 201
    # User errors
    TOKEN_ERROR = 401
    REGISTER_ERROR = 400
    INVALID_USER = 404
    LOGIN_ERROR = 405
    # Genric Errors
    UNSUPPORTED_COMMAND = 100
    SERVER_ERROR = 505

class Message():
    def __init__(self, encrypted_msg: bytes, key: Fernet, sender: Side):
        self.msg = key.decrypt(encrypted_msg).decode()

        msg_parts = self.msg.split('|', 3)

        if sender == Side.CLIENT:
            if msg_parts[0] in ServerCommands:
                self.command = ServerCommands(msg_parts[0])
            else:
                raise exceptions.UnsupportedCommand("The command is unsupported!")
        else:
            if int(msg_parts[0]) in ServerStatus:
                self.status = ServerStatus(int(msg_parts[0]))
            else:
                raise exceptions.UnsupportedStatusCode("The status code is unsupported!")    

        if msg_parts[1] == "NONE":
            self.jwt = None
        else:
            self.jwt = msg_parts[1]
        
        self.json = json.loads(msg_parts[2])

