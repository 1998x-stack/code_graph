# core/graph/knowledge_graph.py
# ── 知识图谱核心 ──────────────────────────────────────────────────────
# 存储结构：networkx.DiGraph（边 + 节点属性） + 两个快速查询 dict
from __future__ import annotations

from typing import Optional

import networkx as nx

from schema.enums import NodeType, RelationType
from schema.models import (
    AnyNode, AnyRelation,
    DirNode, FileNode, ClassNode, FunctionNode,
    HasRelation, ImportRelation, CallRelation,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class KnowledgeGraph:
    """
    代码知识图谱。

    内部双存储：
      _node_map     : node_id → AnyNode        （O(1) 查询）
      _relation_map : relation_id → AnyRelation （O(1) 查询）
      _graph        : nx.DiGraph               （图算法）
    """

    def __init__(self, project_root: str = "") -> None:
        self.project_root = project_root
        self._node_map:     dict[str, AnyNode]     = {}
        self._relation_map: dict[str, AnyRelation] = {}
        self._graph: nx.DiGraph = nx.DiGraph()

    # ═══════════════════════════════════════════════
    #  写入
    # ═══════════════════════════════════════════════
    def add_node(self, node: AnyNode) -> None:
        if node.node_id in self._node_map:
            logger.debug(f"节点已存在，覆盖: {node.node_id}")
        self._node_map[node.node_id] = node
        self._graph.add_node(node.node_id, **node.model_dump())

    def add_nodes(self, nodes: list[AnyNode]) -> None:
        for n in nodes:
            self.add_node(n)

    def add_relation(self, rel: AnyRelation) -> None:
        if rel.relation_id in self._relation_map:
            logger.debug(f"关系已存在，覆盖: {rel.relation_id}")
        self._relation_map[rel.relation_id] = rel
        self._graph.add_edge(
            rel.source_id,
            rel.target_id,
            **rel.model_dump(),
        )

    def add_relations(self, rels: list[AnyRelation]) -> None:
        for r in rels:
            self.add_relation(r)

    # ═══════════════════════════════════════════════
    #  基础查询
    # ═══════════════════════════════════════════════
    def get_node(self, node_id: str) -> Optional[AnyNode]:
        return self._node_map.get(node_id)

    def get_nodes_by_name(
        self,
        name: str,
        node_type: Optional[NodeType] = None,
        fuzzy: bool = True,
    ) -> list[AnyNode]:
        """按名称（模糊/精确）查节点，可按 node_type 过滤"""
        result = []
        for node in self._node_map.values():
            match = (name.lower() in node.name.lower()) if fuzzy else (name == node.name)
            if match:
                if node_type is None or node.node_type == node_type:
                    result.append(node)
        return result

    def get_relations_from(
        self,
        source_id: str,
        rel_type: Optional[RelationType] = None,
    ) -> list[AnyRelation]:
        """获取某节点的所有出边关系"""
        return [
            r for r in self._relation_map.values()
            if r.source_id == source_id
            and (rel_type is None or r.relation_type == rel_type)
        ]

    def get_relations_to(
        self,
        target_id: str,
        rel_type: Optional[RelationType] = None,
    ) -> list[AnyRelation]:
        """获取某节点的所有入边关系"""
        return [
            r for r in self._relation_map.values()
            if r.target_id == target_id
            and (rel_type is None or r.relation_type == rel_type)
        ]

    # ═══════════════════════════════════════════════
    #  调用链查询
    # ═══════════════════════════════════════════════
    def get_call_chain(
        self,
        func_node_id: str,
        max_depth: int = 3,
    ) -> dict:
        """
        返回函数的 上游调用者（谁调了我）& 下游被调者（我调了谁）。
        使用 networkx DFS 遍历，限制深度。
        """
        g = self._graph
        rg = g.reverse(copy=False)

        downstream = (
            dict(nx.dfs_successors(g,  func_node_id, depth_limit=max_depth))
            if func_node_id in g else {}
        )
        upstream = (
            dict(nx.dfs_successors(rg, func_node_id, depth_limit=max_depth))
            if func_node_id in rg else {}
        )
        return {
            "func_node_id": func_node_id,
            "callers":  upstream,     # 谁调了我
            "callees":  downstream,   # 我调了谁
        }

    # ═══════════════════════════════════════════════
    #  统计
    # ═══════════════════════════════════════════════
    @property
    def node_count(self) -> int:
        return len(self._node_map)

    @property
    def relation_count(self) -> int:
        return len(self._relation_map)

    def summary(self) -> str:
        counts = {}
        for n in self._node_map.values():
            counts[n.node_type] = counts.get(n.node_type, 0) + 1
        rel_counts = {}
        for r in self._relation_map.values():
            rel_counts[r.relation_type] = rel_counts.get(r.relation_type, 0) + 1
        lines = [f"项目: {self.project_root}"]
        lines += [f"  节点 {t.value}: {c}" for t, c in counts.items()]
        lines += [f"  关系 {t.value}: {c}" for t, c in rel_counts.items()]
        return "\n".join(lines)

    # ═══════════════════════════════════════════════
    #  序列化 / 反序列化
    # ═══════════════════════════════════════════════
    def to_dict(self) -> dict:
        """导出为纯字典，用于 pickle / JSON 持久化"""
        return {
            "project_root": self.project_root,
            "nodes":        [n.model_dump() for n in self._node_map.values()],
            "relations":    [r.model_dump() for r in self._relation_map.values()],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeGraph":
        """从 to_dict() 返回的字典重建图谱"""
        graph = cls(project_root=data.get("project_root", ""))

        _node_cls_map = {
            NodeType.DIR:      DirNode,
            NodeType.FILE:     FileNode,
            NodeType.CLASS:    ClassNode,
            NodeType.FUNCTION: FunctionNode,
        }
        for nd in data.get("nodes", []):
            nt = NodeType(nd["node_type"])
            node = _node_cls_map[nt](**nd)
            graph.add_node(node)

        _rel_cls_map = {
            RelationType.HAS:    HasRelation,
            RelationType.IMPORT: ImportRelation,
            RelationType.CALL:   CallRelation,
        }
        for rd in data.get("relations", []):
            rt = RelationType(rd["relation_type"])
            rel = _rel_cls_map[rt](**rd)
            graph.add_relation(rel)

        logger.info(
            f"图谱加载完成: {graph.node_count} 节点, {graph.relation_count} 关系"
        )
        return graph

    # ═══════════════════════════════════════════════
    #  增量更新接口（预留，TODO）
    # ═══════════════════════════════════════════════
    def remove_file(self, file_abs_path: str) -> None:
        """
        删除指定文件的所有节点及关联关系。
        增量更新时先调此方法，再重新解析。
        TODO: 实现细节
        """
        pass  # TODO

    def upsert_file(
        self,
        nodes: list[AnyNode],
        relations: list[AnyRelation],
    ) -> None:
        """
        增量更新单文件：先 remove_file，再 add_nodes + add_relations。
        TODO: 实现细节
        """
        pass  # TODO