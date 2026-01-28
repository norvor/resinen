import os
import json
from cryptography.fernet import Fernet
from fastapi import HTTPException

# Load Key from .env or generate a temporary one (for dev only)
# IN PROD: You MUST set ENCRYPTION_KEY in your .env file
# Run this in python to get a key: Fernet.generate_key().decode()
key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher_suite = Fernet(key)

def encrypt_data(data: dict) -> str:
    """Converts Dict -> JSON String -> Encrypted Bytes -> String"""
    try:
        json_str = json.dumps(data)
        encrypted_bytes = cipher_suite.encrypt(json_str.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"Encryption Error: {e}")
        raise HTTPException(status_code=500, detail="Encryption failed")

def decrypt_data(token: str) -> dict:
    """Converts Encrypted String -> Bytes -> Decrypted JSON String -> Dict"""
    try:
        decrypted_bytes = cipher_suite.decrypt(token.encode('utf-8'))
        return json.loads(decrypted_bytes.decode('utf-8'))
    except Exception as e:
        print(f"Decryption Error: {e}")
        # If decryption fails (e.g. key changed), return empty dict or raise error
        return {}