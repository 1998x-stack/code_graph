# llm/client.py
# ── OpenAI 客户端封装 ─────────────────────────────────────────────────
from __future__ import annotations

from openai import OpenAI

from config.settings import settings
from core.graph.knowledge_graph import KnowledgeGraph
from llm.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from schema.enums import NodeType
from utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """
    封装 OpenAI Chat API，提供：
    - generate_grep_command(graph, question) → bash 指令字符串
    """

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY 未配置，请在 .env 文件中设置 OPENAI_API_KEY"
            )
        self._client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self.model       = settings.OPENAI_MODEL
        self.temperature = settings.OPENAI_TEMPERATURE

    # ── 图谱摘要：精简 token，保留核心定位信息 ──────
    @staticmethod
    def _build_graph_summary(graph: KnowledgeGraph, max_items: int = 400) -> str:
        """
        将图谱压缩为 LLM 可用的纯文本摘要。
        只保留 class / function 节点，包含路径、行号、docstring 摘要。
        """
        lines: list[str] = []
        for node in list(graph._node_map.values())[:max_items]:
            if node.node_type == NodeType.CLASS:
                doc = (node.docstring[:60] + "…") if node.docstring else ""  # type: ignore
                lines.append(
                    f"[CLASS] {node.name} | {node.abs_path}:{node.start_line}-{node.end_line}"  # type: ignore
                    + (f" | {doc}" if doc else "")
                )
            elif node.node_type == NodeType.FUNCTION:
                doc = (node.docstring[:60] + "…") if node.docstring else ""  # type: ignore
                lines.append(
                    f"[FUNC]  {node.name}{node.params} | {node.abs_path}:{node.start_line}-{node.end_line}"  # type: ignore
                    + (f" | {doc}" if doc else "")
                )
        return "\n".join(lines) if lines else "（图谱为空）"

    # ── 主接口 ────────────────────────────────────────
    def generate_grep_command(
        self,
        graph: KnowledgeGraph,
        question: str,
    ) -> str:
        """
        基于图谱摘要 + 用户问题，让 LLM 生成 bash/grep 定位指令。

        :param graph:    已构建的 KnowledgeGraph
        :param question: 用户自然语言问题
        :return:         LLM 返回的指令文本
        """
        summary = self._build_graph_summary(graph)
        user_prompt = USER_PROMPT_TEMPLATE.format(
            project_root=graph.project_root,
            graph_summary=summary,
            question=question,
        )

        logger.info(f"调用 LLM 生成指令 | 模型: {self.model} | 问题: {question[:80]}")
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_prompt},
                ],
            )
            result = response.choices[0].message.content or ""
            logger.info("LLM 指令生成完成")
            return result.strip()
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise