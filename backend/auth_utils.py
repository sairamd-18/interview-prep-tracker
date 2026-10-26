"""
Authentication utilities for password hashing and JWT handling.
Zero external crypto dependencies: uses built-in hashlib and hmac.
"""
import hmac
import hashlib
import json
import base64
import time
import os

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "super-secret-key-agentic-ai-tracker-2026")
TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 7  # 7 days

def hash_password(password: str, salt: str = None) -> str:
    """Hash password with PBKDF2-HMAC-SHA256."""
    if not salt:
        salt = base64.b64encode(os.urandom(16)).decode('utf-8')
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return f"{salt}${base64.b64encode(key).decode('utf-8')}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password."""
    try:
        salt, expected_hash = hashed_password.split('$', 1)
        calculated_hash = hash_password(plain_password, salt).split('$', 1)[1]
        return hmac.compare_digest(expected_hash, calculated_hash)
    except Exception:
        return False

def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def _base64url_decode(data: str) -> bytes:
    padding = '=' * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode((data + padding).encode('utf-8'))

def create_access_token(data: dict, expires_delta: int = TOKEN_EXPIRE_SECONDS) -> str:
    """Create a standard HS256 JWT token."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = data.copy()
    payload["exp"] = int(time.time()) + expires_delta
    payload["iat"] = int(time.time())
    
    header_b64 = _base64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    payload_b64 = _base64url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
    
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    signature_b64 = _base64url_encode(signature)
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def decode_access_token(token: str) -> dict:
    """Decode and verify an HS256 JWT token."""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature_b64 = parts
        
        # Verify signature
        signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
        expected_sig_b64 = _base64url_encode(expected_sig)
        
        if not hmac.compare_digest(signature_b64, expected_sig_b64):
            return None
            
        payload = json.loads(_base64url_decode(payload_b64).decode('utf-8'))
        
        # Check expiration
        if payload.get("exp") and payload["exp"] < time.time():
            return None
            
        return payload
    except Exception:
        return None
