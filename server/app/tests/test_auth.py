import pytest
from app.utils.security import get_password_hash, verify_password, create_access_token, decode_token

def test_password_hashing():
    pwd = "secretpassword123"
    hashed = get_password_hash(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_jwt_token_generation():
    user_id = "user-12345"
    token = create_access_token(user_id)
    payload = decode_token(token)
    assert payload is not None
    assert payload.get("sub") == user_id
