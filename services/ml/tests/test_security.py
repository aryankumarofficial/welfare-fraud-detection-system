import os
import sys
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ML_ROOT))
os.chdir(ML_ROOT)

from src import security as security_module
from src.security import SystemRole


def test_create_and_decode_access_token() -> None:
    token, expires_at = security_module.create_access_token("operator", SystemRole.operator)
    assert token
    assert expires_at > 0

    claims = security_module.decode_access_token(token)
    assert claims.sub == "operator"
    assert claims.role == SystemRole.operator


def test_access_token_expires() -> None:
    original_expire = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_SECONDS")
    os.environ["JWT_ACCESS_TOKEN_EXPIRE_SECONDS"] = "1"

    try:
        token, expires_at = security_module.create_access_token("operator", SystemRole.operator)
        assert expires_at - int(__import__("time").time()) in (0, 1)
    finally:
        if original_expire is None:
            del os.environ["JWT_ACCESS_TOKEN_EXPIRE_SECONDS"]
        else:
            os.environ["JWT_ACCESS_TOKEN_EXPIRE_SECONDS"] = original_expire


def test_validate_user_credentials_returns_role() -> None:
    os.environ["ADMIN_USERNAME"] = "admin"
    os.environ["ADMIN_PASSWORD"] = "admin"
    role = security_module.validate_user_credentials("admin", "admin")
    assert role == SystemRole.admin


def test_require_internal_service_rejects_bad_key() -> None:
    old_key = os.getenv("INTERNAL_API_KEY")
    os.environ["INTERNAL_API_KEY"] = "internal-change-me"

    try:
        try:
            security_module.require_internal_service("wrong-key")
            assert False, "Expected HTTPException for invalid internal API key"
        except security_module.HTTPException as exc:
            assert exc.status_code == 401
    finally:
        if old_key is None:
            del os.environ["INTERNAL_API_KEY"]
        else:
            os.environ["INTERNAL_API_KEY"] = old_key


def test_require_queue_access_accepts_correct_key() -> None:
    old_key = os.getenv("QUEUE_API_KEY")
    os.environ["QUEUE_API_KEY"] = "queue-change-me"

    try:
        assert security_module.require_queue_access("queue-change-me") is None
    finally:
        if old_key is None:
            del os.environ["QUEUE_API_KEY"]
        else:
            os.environ["QUEUE_API_KEY"] = old_key
