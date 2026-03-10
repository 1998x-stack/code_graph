# tests/fixtures/sample/service.py
"""样本服务模块，供测试用"""
from tests.fixtures.sample.utils import validate_token, hash_password


class UserService:
    """用户服务类"""

    def login(self, username: str, password: str) -> bool:
        """登录逻辑"""
        hashed = hash_password(password)
        token = validate_token(username + hashed)
        return token is not None

    def logout(self, user_id: int) -> None:
        """登出逻辑"""
        pass


def get_service() -> UserService:
    """工厂函数，返回 UserService 实例"""
    return UserService()