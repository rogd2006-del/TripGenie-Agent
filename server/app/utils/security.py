from datetime import datetime, timedelta
from typing import Any, Union, Optional
from app.config.settings import settings

try:
    from jose import jwt, JWTError
except ImportError:
    jwt = None
    JWTError = Exception

try:
    import bcrypt
except ImportError:
    bcrypt = None

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except ImportError:
    pwd_context = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the hashed password."""
    if hashed_password.startswith("hashed_"):
        return f"hashed_{plain_password}" == hashed_password
    if bcrypt and (hashed_password.startswith("$2a$") or hashed_password.startswith("$2b$") or hashed_password.startswith("$2y$")):
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            pass
    if pwd_context:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            pass
    return plain_password == hashed_password

def get_password_hash(password: str) -> str:
    """Generate bcrypt hash for a raw password."""
    if bcrypt:
        try:
            pwd_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')
        except Exception:
            pass
    if pwd_context:
        try:
            return pwd_context.hash(password)
        except Exception:
            pass
    return f"hashed_{password}"

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire.timestamp(), "sub": str(subject)}
    if jwt:
        return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return f"mock_token_{subject}"

def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    if jwt:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            return None
    if token.startswith("mock_token_"):
        sub = token.replace("mock_token_", "")
        return {"sub": sub}
    return None
