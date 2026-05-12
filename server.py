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
import exceptions
import json
import base64

pub_pem, priv_pem = crypt.generate_server_keys()
SERVER_PORT = 5050

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
    res = handle_request(msg, server).encode()
    network.send_msg(sock, cipher.encrypt(res))
    
    sock.close()
   
def handle_request(request: proto.Message, server: server_manager.SeverManager) -> str:
    status_code, res_json = 0, {}
    
    try:
        # Register
        if request.command == proto.ServerCommands.REGISTER:
            try: 
                server.register_user(request.json["username"], request.json["password"], request.json["public_key"], request.json["encrypted_private_key"])
                status_code, res_json = proto.ServerStatus.OK, {}
            except exceptions.UserAlreadyExists as e:
                status_code, res_json = proto.ServerStatus.REGISTER_ERROR, {"error": str(e)}
        # Login
        elif request.command == proto.ServerCommands.LOGIN:
            try: 
                jwt = server.login_user(request.json["username"], request.json["password"])
                enc_private_key = server.get_private_key_user(jwt)
                status_code, res_json = proto.ServerStatus.OK, {"jwt": jwt, "enc_private_key": enc_private_key}
            except exceptions.InvalidCredentials as e:
                status_code, res_json = proto.ServerStatus.LOGIN_ERROR, {"error": str(e)}
            except exceptions.TokenError:
                status_code = proto.ServerStatus.SERVER_ERROR
        # Get Public Key
        elif request.command == proto.ServerCommands.GET_PUBLIC_KEY:
            try: 
                public_key = server.get_public_key_user(request.json["username"])
                status_code, res_json = proto.ServerStatus.OK, {"public_key": public_key}
            except exceptions.UserDoesntExist as e:
                status_code, res_json = proto.ServerStatus.INVALID_USER, {"error": str(e)}
        # Send msg
        elif request.command == proto.ServerCommands.SEND_MSG:
            try: 
                server.pend_message(request.jwt, request.json["receiver"], base64.b64decode(request.json["message"]))
                status_code, res_json = proto.ServerStatus.SENT, {}
            except exceptions.UserDoesntExist as e:
                status_code, res_json = proto.ServerStatus.INVALID_USER, {"error": str(e)}
            except exceptions.TokenError as e:
                status_code, res_json = proto.ServerStatus.TOKEN_ERROR, {"error": str(e)}
        # Recv msgs
        elif request.command == proto.ServerCommands.RECEIVE_MSGS:
            try: 
                msgs = server.get_pending_messages(request.jwt)
                status_code, res_json = proto.ServerStatus.OK, {'messages': msgs}
            except exceptions.TokenError as e:
                status_code, res_json = proto.ServerStatus.TOKEN_ERROR, {"error": str(e)}
        else:
            status_code = proto.ServerStatus.UNSUPPORTED_COMMAND
    except:
        status_code = proto.ServerStatus.SERVER_ERROR

    return f"{int(status_code)}|NONE|{json.dumps(res_json)}"

def main():
    server = server_manager.SeverManager()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(('', SERVER_PORT))
        server_sock.listen()
        print(f"[LISTENING] Server_sock is listening on {SERVER_PORT}")

        while True:
            conn, addr = server_sock.accept()
            thread = threading.Thread(target=handle_client, args=(conn, server, addr))
            thread.start()
        
if __name__ == "__main__":
    main()