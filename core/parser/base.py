# core/parser/base.py
# ── 解析器抽象基类（可插拔扩展接口） ─────────────────────────────────
from __future__ import annotations

from abc import ABC, abstractmethod

from schema.models import AnyNode, AnyRelation


class BaseParser(ABC):
    """
    所有语言解析器必须实现此接口。
    工厂通过 supported_suffixes 自动注册。

    扩展新语言步骤：
    1. 继承 BaseParser，实现 supported_suffixes + parse_file
    2. 在 factory.py 底部调用 ParserFactory.register(MyParser)
    """

    @property
    @abstractmethod
    def supported_suffixes(self) -> list[str]:
        """返回该解析器支持的文件后缀，如 ['.py']"""

    @abstractmethod
    def parse_file(
        self,
        file_abs_path: str,
        file_content: str,
    ) -> tuple[list[AnyNode], list[AnyRelation]]:
        """
        解析单个源文件，返回 (节点列表, 关系列表)。

        :param file_abs_path: 文件绝对路径
        :param file_content:  文件文本内容
        :return:              (nodes, relations) —— 均不含目录节点，目录由 builder 统一处理
        """