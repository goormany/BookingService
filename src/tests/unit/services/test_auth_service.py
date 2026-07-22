from datetime import timedelta
from unittest.mock import patch

from jwt import DecodeError, ExpiredSignatureError
import pytest

from src.services.auth import AuthServices
from src.config import settings
from src.utils.exceptions.exceptions import (
    ExpiredJWTTokenException,
    InvalidTokenDecodedException,
)


class TestCreateDataForToken:
    @pytest.mark.parametrize("user_id", [1, "1", "user_123"])
    def test_success(self, user_id):
        result = AuthServices._create_data_for_token(user_id=user_id)

        assert isinstance(result, dict)
        assert result.get("sub", None) is not None
        assert isinstance(result["sub"], str)
        assert result["sub"] == str(user_id)


class TestGetPasswordHash:
    @patch("src.services.auth.password_hasher")
    @pytest.mark.parametrize("password", ["pass", "Snj^d#", ""])
    def test_success(self, mock_hasher, password):
        mock_hasher.hash.return_value = "mocked_hashed_password"

        hashed_password = AuthServices.get_password_hash(password)

        mock_hasher.hash.assert_called_once_with(password)
        assert isinstance(hashed_password, str)
        assert hashed_password == "mocked_hashed_password"
        assert len(hashed_password) > 0

    @patch("src.services.auth.password_hasher")
    def test_diff_hash(self, mock_hasher):
        mock_hasher.hash.side_effect = ["hash1", "hash2"]
        password = "pass"

        hash1 = AuthServices.get_password_hash(password)
        hash2 = AuthServices.get_password_hash(password)

        assert mock_hasher.hash.call_count == 2
        assert hash1 == "hash1"
        assert hash2 == "hash2"
        assert hash1 != hash2

    @patch("src.services.auth.password_hasher")
    def test_calls_hasher_with_correct_password(self, mock_hasher):
        mock_hasher.hash.return_value = "hashed"
        password = "my_secret_password"

        AuthServices.get_password_hash(password)

        mock_hasher.hash.assert_called_once_with(password)


class TestVerifyPassword:
    @patch("src.services.auth.password_hasher")
    def test_success(self, mock_hasher):
        mock_hasher.verify.return_value = True
        password = "pass"
        hashed_password = "hashed_pass"

        result = AuthServices.verify_password(password, hashed_password)

        mock_hasher.verify.assert_called_once_with(password, hashed_password)
        assert isinstance(result, bool)
        assert result is True

    @patch("src.services.auth.password_hasher")
    def test_incorrect_password(self, mock_hasher):
        mock_hasher.verify.return_value = False
        password = "pass"
        hashed_password = "hashed_else"

        result = AuthServices.verify_password(password, hashed_password)

        mock_hasher.verify.assert_called_once_with(password, hashed_password)
        assert isinstance(result, bool)
        assert result is False

    @patch("src.services.auth.password_hasher")
    def test_verify_with_empty_password(self, mock_hasher):
        mock_hasher.verify.return_value = False
        password = ""
        hashed_password = "hashed"

        result = AuthServices.verify_password(password, hashed_password)

        mock_hasher.verify.assert_called_once_with(password, hashed_password)
        assert result is False


class TestCreateAccessToken:
    @patch("src.services.auth.jwt.encode")
    @patch.object(AuthServices, "_create_data_for_token")
    def test_success(self, mock_create_data, mock_jwt_encode):
        mock_create_data.return_value = {"sub": "test_user"}
        mock_jwt_encode.return_value = "jwt_token"
        sub = "1"
        expire_time = timedelta(minutes=30)

        result = AuthServices.create_access_token(sub, expire_time)

        mock_create_data.assert_called_once_with(sub)
        mock_jwt_encode.assert_called_once()
        assert result == "jwt_token"

    @patch("src.services.auth.jwt.encode")
    @patch.object(AuthServices, "_create_data_for_token")
    def test_uses_correct_payload(self, mock_create_data, mock_jwt_encode):
        mock_create_data.return_value = {"sub": "1", "custom": "value"}
        sub = "1"
        expire_time = timedelta(minutes=30)

        AuthServices.create_access_token(sub, expire_time)

        payload = mock_jwt_encode.call_args[0][0]
        assert payload["sub"] == "1"
        assert payload["custom"] == "value"
        assert "exp" in payload

    @patch("src.services.auth.jwt.encode")
    @patch.object(AuthServices, "_create_data_for_token")
    def test_sets_expiration_time(self, mock_create_data, mock_jwt_encode):
        mock_create_data.return_value = {"sub": "1"}
        sub = "1"
        expire_time = timedelta(minutes=30)

        AuthServices.create_access_token(sub, expire_time)

        payload = mock_jwt_encode.call_args[0][0]
        assert "exp" in payload
        assert isinstance(payload["exp"], int) or hasattr(payload["exp"], "timestamp")

    @patch("src.services.auth.jwt.encode")
    @patch.object(AuthServices, "_create_data_for_token")
    def test_merges_data_with_exp(self, mock_create_data, mock_jwt_encode):
        mock_create_data.return_value = {
            "sub": "1",
        }
        sub = "1"
        expire_time = timedelta(minutes=30)

        AuthServices.create_access_token(sub, expire_time)

        payload = mock_jwt_encode.call_args[0][0]
        assert payload["sub"] == "1"
        assert "exp" in payload

    @patch("src.services.auth.jwt.encode")
    @patch.object(AuthServices, "_create_data_for_token")
    @pytest.mark.parametrize("sub", ["1", "user_123", ""])
    def test_different_sub_values(self, mock_create_data, mock_jwt_encode, sub):
        mock_create_data.return_value = {"sub": sub}
        expire_time = timedelta(minutes=30)

        AuthServices.create_access_token(sub, expire_time)

        payload = mock_jwt_encode.call_args[0][0]
        assert payload["sub"] == sub


class TestDecodeAccessToken:
    @patch("src.services.auth.jwt.decode")
    def test_successful_decode(self, mock_jwt_decode):
        mock_jwt_decode.return_value = {
            "sub": "1",
            "jti": "jwt.token.id",
            "exp": 1234567890,
        }
        token = "valid.token.here"

        result = AuthServices.decode_access_token(token)

        mock_jwt_decode.assert_called_once_with(
            token, settings.JWT_SECRET_KEY, [settings.JWT_ALGORITHM]
        )
        assert result.sub == "1"
        assert result.jti == "jwt.token.id"
        assert result.exp == 1234567890

    @patch("src.services.auth.jwt.decode")
    def test_raises_invalid_token_on_decode_error(self, mock_jwt_decode):
        mock_jwt_decode.side_effect = DecodeError("Invalid token")
        token = "invalid.token.here"

        with pytest.raises(InvalidTokenDecodedException):
            AuthServices.decode_access_token(token)

        mock_jwt_decode.assert_called_once()

    @patch("src.services.auth.jwt.decode")
    def test_raises_expired_on_expired_error(self, mock_jwt_decode):
        mock_jwt_decode.side_effect = ExpiredSignatureError("Token expired")
        token = "expired.token.here"

        # Act & Assert
        with pytest.raises(ExpiredJWTTokenException):
            AuthServices.decode_access_token(token)

        mock_jwt_decode.assert_called_once()
