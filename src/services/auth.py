from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from src.services.base import BaseServices
from src.config import settings
from src.schemas.auth import JWTData
from src.utils.exceptions.exceptions import (
    ExpiredJWTTokenException,
    InvalidTokenDecodedException,
)

password_hasher = PasswordHash.recommended()


class AuthServices(BaseServices):
    @staticmethod
    def _create_data_for_token(user_id: str) -> dict[str, str]:
        return {"sub": str(user_id)}

    @staticmethod
    def get_password_hash(password: str) -> str:
        return password_hasher.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return password_hasher.verify(plain_password, hashed_password)

    @classmethod
    def create_access_token(cls, sub: str, expire_time: timedelta) -> str:
        to_encode = cls._create_data_for_token(sub)
        expire = datetime.now(timezone.utc) + expire_time
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> JWTData:
        try:
            jwt_token = jwt.decode(
                token, settings.JWT_SECRET_KEY, [settings.JWT_ALGORITHM]
            )
        except jwt.exceptions.DecodeError:
            raise InvalidTokenDecodedException
        except jwt.exceptions.ExpiredSignatureError:
            raise ExpiredJWTTokenException
        return JWTData(**jwt_token)
