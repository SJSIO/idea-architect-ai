"""
JWT utilities for authentication.
"""

from datetime import datetime, timedelta
from jose import jwt, JWTError
from django.conf import settings


def create_jwt_token(user_id: str, email: str) -> str:
    """Create a JWT token for a user."""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_jwt_token(token: str) -> dict | None:
    """Decode and verify a JWT token. Returns payload or None if invalid."""
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def get_user_from_request(request) -> dict | None:
    """
    Extract user info from Authorization header.
    Returns dict with 'user_id' and 'email', or None if unauthorized.
    """
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header[7:]  # Remove 'Bearer ' prefix
    return decode_jwt_token(token)
