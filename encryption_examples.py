from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.fernet import Fernet
import base64
import hashlib

def client_encrypt_message(plain_text, receiver_public_key_pem):
    """
    Encryption before sending using the receiver key
    """
    public_key = serialization.load_pem_public_key(
        receiver_public_key_pem.encode('utf-8')
    )
    
    encrypted_blob = public_key.encrypt(
        plain_text.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_blob

def client_decrypt_message(encrypted_blob, my_private_key_pem):
    """
    decrypt message after you got it
    """
    private_key = serialization.load_pem_private_key(
        my_private_key_pem.encode('utf-8'),
        password=None 
    )
    
    decrypted_bytes = private_key.decrypt(
        encrypted_blob,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_bytes.decode('utf-8')

def generate_and_save_keys(username):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return public_pem.decode('utf-8'), private_key

# use to backup key to server
def encrypt_private_key_for_backup(private_key_pem, user_password):
    key = hashlib.sha256(user_password.encode()).digest()
    f = Fernet(base64.urlsafe_b64encode(key))
    
    return f.encrypt(private_key_pem.encode())


def decrypt_private_key_from_backup(encrypted_key, user_password):
    key = hashlib.sha256(user_password.encode()).digest()
    f = Fernet(base64.urlsafe_b64encode(key))
    
    return f.decrypt(encrypted_key).decode()