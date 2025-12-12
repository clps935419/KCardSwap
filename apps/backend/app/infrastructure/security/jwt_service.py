"""
JWT Service - Token generation and validation
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID
import os

from jose import JWTError, jwt

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


class JWTService:
    """Service for JWT token operations"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        self.refresh_token_expire = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    def create_access_token(self, user_id: UUID, email: str) -> str:
        """Create access token"""
        expire = datetime.utcnow() + self.access_token_expire
        to_encode = {
            "sub": str(user_id),
            "email": email,
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: UUID) -> tuple[str, datetime]:
        """Create refresh token and return token + expiration"""
        expire = datetime.utcnow() + self.refresh_token_expire
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "type": "refresh"
        }
        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return token, expire
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return payload
        Returns None if token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != token_type:
                return None
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                return None
            
            return payload
        except JWTError:
            return None
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode token without verification (for debugging)"""
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_signature": False})
        except JWTError:
            return None
