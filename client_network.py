import encryption as crypt
import socket
import json
import core.protocol as proto
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.fernet import Fernet
from core import network

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5050

def send_request(msg: str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
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
        
        
def register(username: str, password: str):
    # genrate keys
    public_pem, private_pem = crypt.generate_server_keys()
    user_key = Fernet(f"{username};{password}".encode())
    enc_private_pem = user_key.encrypt(private_pem)

    req_json = {


    }
    
    send_request(f"{proto.ServerCommands.REGISTER}||{json.dumps(req_json)}")