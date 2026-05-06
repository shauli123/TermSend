import struct
import socket

def send_msg(sock: socket.socket, data: bytes):
    length = len(data)
    sock.sendall(struct.pack('>I', length) + data)

def recv_msg(sock: socket.socket):
    raw_msglen = recv_all(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    return recv_all(sock, msglen)

def recv_all(sock: socket.socket, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return bytes(data)