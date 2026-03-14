"""Tests for security utilities."""


from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "my-secure-password"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed)

    def test_wrong_password(self):
        hashed = get_password_hash("correct-password")
        assert not verify_password("wrong-password", hashed)

    def test_different_hashes_for_same_password(self):
        password = "test-password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        # bcrypt should produce different hashes (different salts)
        assert hash1 != hash2
        # But both should verify
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestJWT:
    def test_create_and_decode_token(self):
        data = {"sub": "user-123", "email": "test@example.com"}
        token = create_access_token(data)
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user-123"
        assert decoded["email"] == "test@example.com"

    def test_invalid_token(self):
        result = decode_access_token("invalid-token")
        assert result is None

    def test_token_contains_expiry(self):
        token = create_access_token({"sub": "test"})
        decoded = decode_access_token(token)
        assert decoded is not None
        assert "exp" in decoded
