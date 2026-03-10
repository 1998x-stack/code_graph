# tests/fixtures/sample/utils.py
"""工具模块"""
import hashlib


def validate_token(raw: str) -> str | None:
    """验证 token，返回 None 表示无效"""
    if not raw:
        return None
    return raw[:16]


def hash_password(password: str) -> str:
    """SHA256 哈希密码"""
    return hashlib.sha256(password.encode()).hexdigest()