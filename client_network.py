import encryption as crypt
import socket
import json
import exceptions
import core.protocol as proto
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from core import network
import base64

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5050

SOCK_FAMILY = socket.AF_INET

def send_request(msg: str):
    with socket.socket(SOCK_FAMILY, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_IP, SERVER_PORT))
        # Get public key
        server_pub_pem = network.recv_msg(sock).decode('utf-8')
        server_pub_key = serialization.load_pem_public_key(server_pub_pem.encode('utf-8'))
        
        # Make fernet key and send it
        fernet_key = Fernet.generate_key()
        enc_fernet_key = server_pub_key.encrypt(
            fernet_key,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        network.send_msg(sock, enc_fernet_key)
        
        # Send Req
        cipher = Fernet(fernet_key)
        network.send_msg(sock, cipher.encrypt(msg.encode()))
        
        return proto.Message(network.recv_msg(sock), cipher, proto.Side.SERVER) 
        
def route_error(code: int, res: proto.Message):
    if code == proto.ServerStatus.INVALID_USER:
        raise exceptions.UserDoesntExist(res.json["error"])
    elif code == proto.ServerStatus.LOGIN_ERROR:
        raise exceptions.InvalidCredentials(res.json["error"])
    elif code == proto.ServerStatus.REGISTER_ERROR:
        raise exceptions.UserAlreadyExists(res.json["error"])
    elif code == proto.ServerStatus.TOKEN_ERROR:
        raise exceptions.TokenError(res.json["error"])
    elif code == proto.ServerStatus.UNSUPPORTED_COMMAND or code == proto.ServerStatus.SERVER_ERROR:
        raise exceptions.UserError("An error occurred, Please try again later")

def register(username: str, password: str):
    # genrate keys
    public_pem, private_pem = crypt.generate_server_keys()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=username.encode(),
        iterations=100000,
    )
    user_key = Fernet(base64.urlsafe_b64encode(kdf.derive(password.encode())))
    enc_private_pem = user_key.encrypt(private_pem.encode())
    
    # Send Request 
    req_json = {
        "username": username,
        "password": password,
        "public_key": public_pem,
        "encrypted_private_key":  base64.b64encode(enc_private_pem).decode('utf-8')
    }
    
    res = send_request(f"{proto.ServerCommands.REGISTER}|NONE|{json.dumps(req_json)}")
    if not (200 <= res.status < 300):
        route_error(res.status, res)

def login(username: str, password: str):
    req_json = {
        "username": username,
        "password": password,
    }
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=username.encode(),
        iterations=100000,
    )
    user_key = Fernet(base64.urlsafe_b64encode(kdf.derive(password.encode())))
    
    res = send_request(f"{proto.ServerCommands.LOGIN}|NONE|{json.dumps(req_json)}")
    if (200 <= res.status < 300):
        return res.json['jwt'], user_key.decrypt(base64.b64decode(res.json['enc_private_key']).decode()).decode()
    else:
        route_error(res.status, res)

def get_public_key(username: str):
    req_json = {
        "username": username
    }
    
    res = send_request(f"{proto.ServerCommands.GET_PUBLIC_KEY}|NONE|{json.dumps(req_json)}")
    if (200 <= res.status < 300):
        public_key = res.json['public_key']
        return public_key
    else:
        route_error(res.status, res)
        
def send_msg(token: str, receiver: str, msg: str):
    req_json = {
        "username": receiver
    }
    
    res = send_request(f"{proto.ServerCommands.GET_PUBLIC_KEY}|NONE|{json.dumps(req_json)}")
    
    if (200 <= res.status < 300):
        public_key = res.json['public_key']
        key_bytes = Fernet.generate_key()
        key = Fernet(key_bytes)
        
        
        enc_key = crypt.rsa_encrypt(key_bytes, public_key)
        enc_msg = key.encrypt(msg.encode())
        
        req_json = {
            "receiver": receiver,
            "message":  base64.b64encode(enc_msg).decode('utf-8'),
            "key": base64.b64encode(enc_key).decode('utf-8')
        }
        
        res = send_request(f'{proto.ServerCommands.SEND_MSG}|{token}|{json.dumps(req_json)}')
        
        if not (200 <= res.status < 300):
            route_error(res.status, res)
    else:
        route_error(res.status, res)

def receive_msgs(token: str, private_key: str):
    res = send_request(f"{proto.ServerCommands.RECEIVE_MSGS}|{token}|{{}}")
    if not (200 <= res.status < 300):
            route_error(res.status, res)
    else:
        msgs = res.json['messages']
        for i, msg in enumerate(msgs):
            key = Fernet(crypt.rsa_decrypt(base64.b64decode(msg["key"]), private_key))
            msgs[i]["content"] = key.decrypt(base64.b64decode(msg["content"])).decode()
            
    return msgs
            
