# core/parser/factory.py
# ── 可插拔解析器工厂 ──────────────────────────────────────────────────
# 开闭原则：新增语言只需实现 BaseParser + 调用 register()，工厂代码不动。
from __future__ import annotations

from typing import Type

from core.parser.base import BaseParser
from utils.logger import get_logger

logger = get_logger(__name__)


class ParserFactory:
    """
    解析器工厂。
    注册示例：
        ParserFactory.register(PythonParser)
    获取示例：
        parser = ParserFactory.get(".py")
    """

    _registry: dict[str, Type[BaseParser]] = {}

    # ── 注册 ─────────────────────────────────────────
    @classmethod
    def register(cls, parser_cls: Type[BaseParser]) -> None:
        """注册解析器类；同一后缀重复注册会覆盖并警告"""
        instance = parser_cls()
        for suffix in instance.supported_suffixes:
            if suffix in cls._registry:
                logger.warning(
                    f"后缀 {suffix!r} 解析器已存在，将覆盖: "
                    f"{cls._registry[suffix].__name__} → {parser_cls.__name__}"
                )
            cls._registry[suffix] = parser_cls
            logger.debug(f"注册解析器: {parser_cls.__name__} ← {suffix}")

    # ── 获取 ─────────────────────────────────────────
    @classmethod
    def get(cls, suffix: str) -> BaseParser:
        """
        按文件后缀返回解析器实例。
        :raises ValueError: 未注册该后缀时抛出
        """
        parser_cls = cls._registry.get(suffix)
        if parser_cls is None:
            raise ValueError(
                f"没有注册支持后缀 {suffix!r} 的解析器。"
                f"已注册: {list(cls._registry.keys())}"
            )
        return parser_cls()

    # ── 查询 ─────────────────────────────────────────
    @classmethod
    def supported_suffixes(cls) -> list[str]:
        """返回所有已注册的文件后缀"""
        return list(cls._registry.keys())

    @classmethod
    def is_supported(cls, suffix: str) -> bool:
        return suffix in cls._registry


# ── 默认注册 Python 解析器 ───────────────────────────
# 其他语言解析器在此追加 register() 调用即可
from core.parser.python_parser import PythonParser  # noqa: E402
ParserFactory.register(PythonParser)