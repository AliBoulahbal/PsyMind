import base64, hashlib, json
from cryptography.fernet import Fernet
from app.core.config import settings

def _fernet():
    raw=hashlib.sha256(settings.pii_encryption_key.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(raw))

def encrypt_identity(data:dict)->str:
    return _fernet().encrypt(json.dumps(data,separators=(",",":")).encode()).decode()

def decrypt_identity(value:str)->dict:
    return json.loads(_fernet().decrypt(value.encode()).decode())
