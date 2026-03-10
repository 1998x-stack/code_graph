# storage/graph_store.py
# ── 图谱持久化存储 ────────────────────────────────────────────────────
# 当前实现：本地文件（pickle 二进制 + JSON 可读）
# 扩展预留：Neo4j / MySQL 只需新增 StorageBackend 子类
from __future__ import annotations

import json
import os
import pickle
from typing import Optional

from core.graph.knowledge_graph import KnowledgeGraph
from utils.logger import get_logger

logger = get_logger(__name__)


class GraphStore:
    """
    图谱持久化存储类。

    用法：
        store = GraphStore("./output/graph.pkl")
        store.save(graph)
        graph = store.load()
    """

    def __init__(self, default_path: str) -> None:
        self.default_path = default_path
        os.makedirs(os.path.dirname(os.path.abspath(default_path)), exist_ok=True)

    # ── Pickle（默认，完整保留对象） ──────────────────
    def save(self, graph: KnowledgeGraph, path: Optional[str] = None) -> None:
        """保存图谱到 pickle 文件"""
        target = path or self.default_path
        try:
            with open(target, "wb") as f:
                pickle.dump(graph.to_dict(), f, protocol=pickle.HIGHEST_PROTOCOL)
            logger.info(f"图谱已保存: {target} ({graph.node_count} 节点, {graph.relation_count} 关系)")
        except OSError as e:
            logger.error(f"图谱保存失败: {e}")
            raise

    def load(self, path: Optional[str] = None) -> KnowledgeGraph:
        """从 pickle 文件加载图谱"""
        target = path or self.default_path
        if not os.path.isfile(target):
            raise FileNotFoundError(f"图谱文件不存在: {target}")
        try:
            with open(target, "rb") as f:
                data = pickle.load(f)
            return KnowledgeGraph.from_dict(data)
        except Exception as e:
            logger.error(f"图谱加载失败: {e}")
            raise

    # ── JSON（用于可视化 / 前端对接） ─────────────────
    def save_json(self, graph: KnowledgeGraph, path: str) -> None:
        """导出图谱为 JSON（human-readable，含完整元数据）"""
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(graph.to_dict(), f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"JSON 已导出: {path}")
        except OSError as e:
            logger.error(f"JSON 导出失败: {e}")
            raise

    def load_json(self, path: str) -> KnowledgeGraph:
        """从 JSON 文件加载图谱"""
        if not os.path.isfile(path):
            raise FileNotFoundError(f"JSON 文件不存在: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return KnowledgeGraph.from_dict(data)