import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.security.auth import hash_password, verify_password, create_access_token, decode_token


class TestAuth:
    def test_password_hashing(self):
        password = "TestPassword123!"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("WrongPassword", hashed)

    def test_token_creation_and_decoding(self):
        user_id = "test-user-id"
        email = "test@example.com"
        roles = ["admin"]

        token = create_access_token(user_id, email, roles)
        assert token is not None

        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["email"] == email
        assert payload["roles"] == roles
        assert payload["type"] == "access"

    def test_invalid_token(self):
        payload = decode_token("invalid-token")
        assert payload is None
