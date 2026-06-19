import base64
import hashlib
import hmac
import json
import time
from enum import Enum
from functools import lru_cache
from typing import Any

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SystemRole(str, Enum):
    admin = "admin"
    analyst = "analyst"
    operator = "operator"
    viewer = "viewer"


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    role: SystemRole


class UserClaims(BaseModel):
    sub: str
    role: SystemRole
    exp: int


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    jwt_secret_key: str = Field(default="change-me", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_seconds: int = Field(default=3600, alias="JWT_ACCESS_TOKEN_EXPIRE_SECONDS")

    admin_username: str = Field(default="admin", alias="ADMIN_USERNAME")
    admin_password: str = Field(default="admin", alias="ADMIN_PASSWORD")
    analyst_username: str = Field(default="analyst", alias="ANALYST_USERNAME")
    analyst_password: str = Field(default="analyst", alias="ANALYST_PASSWORD")
    operator_username: str = Field(default="operator", alias="OPERATOR_USERNAME")
    operator_password: str = Field(default="operator", alias="OPERATOR_PASSWORD")

    internal_api_key: str = Field(default="internal-change-me", alias="INTERNAL_API_KEY")
    queue_api_key: str = Field(default="queue-change-me", alias="QUEUE_API_KEY")


def _base64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _base64_decode(encoded: str) -> bytes:
    padding = "=" * (-len(encoded) % 4)
    return base64.urlsafe_b64decode(encoded + padding)


@lru_cache()
def get_auth_settings() -> AuthSettings:
    return AuthSettings()


def _sign_token(payload: bytes, secret: str) -> bytes:
    return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).digest()


def create_access_token(username: str, role: SystemRole) -> tuple[str, int]:
    settings = get_auth_settings()
    exp = int(time.time()) + settings.jwt_access_token_expire_seconds
    payload = {
        "sub": username,
        "role": role.value,
        "exp": exp,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = _sign_token(payload_bytes, settings.jwt_secret_key)
    token = f"{_base64_encode(payload_bytes)}.{_base64_encode(signature)}"
    return token, exp


def decode_access_token(token: str) -> UserClaims:
    settings = get_auth_settings()
    try:
        encoded_payload, encoded_signature = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization token") from exc

    try:
        payload_bytes = _base64_decode(encoded_payload)
        signature = _base64_decode(encoded_signature)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization token") from exc

    expected_signature = _sign_token(payload_bytes, settings.jwt_secret_key)
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization token")

    payload = json.loads(payload_bytes.decode("utf-8"))
    claims = UserClaims(**payload)
    if claims.exp < int(time.time()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

    return claims


def get_user_role(username: str) -> SystemRole | None:
    settings = get_auth_settings()
    if username == settings.admin_username:
        return SystemRole.admin
    if username == settings.analyst_username:
        return SystemRole.analyst
    if username == settings.operator_username:
        return SystemRole.operator
    return None


def validate_user_credentials(username: str, password: str) -> SystemRole | None:
    settings = get_auth_settings()
    if username == settings.admin_username and password == settings.admin_password:
        return SystemRole.admin
    if username == settings.analyst_username and password == settings.analyst_password:
        return SystemRole.analyst
    if username == settings.operator_username and password == settings.operator_password:
        return SystemRole.operator
    return None


bearer_scheme = HTTPBearer(auto_error=False)
internal_key_header = APIKeyHeader(name="X-Internal-API-Key", auto_error=False)
queue_key_header = APIKeyHeader(name="X-Queue-API-Key", auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme)) -> UserClaims:
    if credentials is None or not credentials.scheme.lower() == "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid",
        )
    return decode_access_token(credentials.credentials)


def require_minimum_role(minimum: SystemRole):
    def dependency(user: UserClaims = Depends(get_current_user)) -> UserClaims:
        role_priority = {
            SystemRole.viewer: 0,
            SystemRole.operator: 1,
            SystemRole.analyst: 2,
            SystemRole.admin: 3,
        }
        if role_priority[user.role] < role_priority[minimum]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return dependency


def require_operator(user: UserClaims = Depends(require_minimum_role(SystemRole.operator))) -> UserClaims:
    return user


def require_analyst(user: UserClaims = Depends(require_minimum_role(SystemRole.analyst))) -> UserClaims:
    return user


def require_admin(user: UserClaims = Depends(require_minimum_role(SystemRole.admin))) -> UserClaims:
    return user


def require_internal_service(api_key: str | None = Security(internal_key_header)) -> None:
    settings = get_auth_settings()
    if api_key != settings.internal_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Internal service authentication failed")


def require_queue_access(api_key: str | None = Security(queue_key_header)) -> None:
    settings = get_auth_settings()
    if api_key != settings.queue_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Queue API authentication failed")
