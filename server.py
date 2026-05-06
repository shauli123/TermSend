# Encryption imports
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.fernet import Fernet
import base64
import hashlib
import encryption as crypt
# Server imports
import socket
import core.protocol as proto
from core import network
import server_manager
import threading

pub_pem, priv_pem = crypt.generate_server_keys()

def handle_client(sock: socket.socket, server: server_manager.SeverManager, addr):
    # Send Public Key
    network.send_msg(sock, pub_pem.encode('utf-8'))
    
    # Get fernet key
    enc_fernet_key = network.recv_msg(sock)
    fernet_key = crypt.rsa_decrypt(enc_fernet_key, priv_pem)
    cipher = Fernet(fernet_key)
    
    # Get Request
    msg = proto.Message(network.recv_msg(sock), cipher, proto.Side.CLIENT)
    
    # Response with response
    res = handle_request(msg).encode()
    network.send_msg(sock, cipher.encrypt(res))
    
    sock.close()
   
def handle_request(request: proto.Message) -> str:
    return "NULL"


def main():
    server = server_manager.SeverManager()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(('', 5050))
        server_sock.listen()
        print("[LISTENING] Server_sock is listening on 5050")

        while True:
            conn, addr = server_sock.accept()
            thread = threading.Thread(target=handle_client, args=(conn, server, addr))
            thread.start()
        
if __name__ == "__main__":
    main()