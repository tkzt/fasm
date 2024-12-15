import bcrypt
import jwt
from datetime import datetime, timedelta
from uuid import UUID

from settings import settings


JWT_ALGORITHM = "HS256"


def _create_jwt(subject: str, expires_minutes: int) -> str:
    expire = datetime.now() + timedelta(minutes=expires_minutes)
    payload = {"exp": expire, "sub": str(subject), "type": "access"}
    return jwt.encode(
        payload=payload,
        key=settings.SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def create_access_token(user_id: UUID) -> str:
    return _create_jwt(str(user_id), settings.ACCESS_TOKEN_EXPIRE_MINUTES)


def create_refresh_token(user_id: UUID) -> str:
    return _create_jwt(str(user_id), settings.REFRESH_TOKEN_EXPIRE_MINUTES)


def verify_jwt(token: str) -> dict:
    return jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
    )


def verify_pwd(plain_pwd: str, hashed_pwd: str) -> bool:
    return bcrypt.checkpw(plain_pwd.encode(), hashed_pwd.encode())


def gen_pwd_hash(plain_pwd: str) -> str:
    plain_pwd_bytes = plain_pwd.encode()
    return bcrypt.hashpw(plain_pwd_bytes, bcrypt.gensalt()).decode()
