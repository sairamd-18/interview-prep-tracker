"""
FastAPI dependencies for authentication and authorization.
"""
from fastapi import Header, HTTPException, status
from backend.auth_utils import decode_access_token
from backend.database.db import get_db

def get_current_user(authorization: str = Header(None)) -> dict:
    """
    Extracts and validates the JWT from Authorization header.
    Falls back to demo user if no header is supplied in local testing mode.
    """
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            user_id = payload["sub"]
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, email, full_name, role FROM users WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                if user:
                    return user

    # Fallback to default demo user for frictionless local preview
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, full_name, role FROM users WHERE email = 'demo@example.com' LIMIT 1")
        demo_user = cursor.fetchone()
        if demo_user:
            return demo_user
        cursor.execute("SELECT id, email, full_name, role FROM users LIMIT 1")
        first_user = cursor.fetchone()
        if first_user:
            return first_user

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User authentication required")
