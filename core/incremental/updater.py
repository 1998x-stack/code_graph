# core/incremental/updater.py
# ── 增量更新器（接口完整，实现体为 TODO） ─────────────────────────────
# 设计契约：外部调用方只依赖此接口，实现随时填充，不影响其他模块。
from __future__ import annotations

import os
from typing import Optional

from core.graph.knowledge_graph import KnowledgeGraph
from core.parser.factory import ParserFactory
from schema.enums import NodeType
from utils.file_utils import walk_project, read_file, file_md5
from utils.logger import get_logger

logger = get_logger(__name__)

# ──────────────────────────────────────────────────────────────────────
# 数据类：文件变更快照
# ──────────────────────────────────────────────────────────────────────
class FileChanges:
    """描述一次增量检查的结果"""
    def __init__(
        self,
        added:    list[str],
        modified: list[str],
        deleted:  list[str],
    ) -> None:
        self.added    = added
        self.modified = modified
        self.deleted  = deleted

    def __repr__(self) -> str:
        return (
            f"FileChanges("
            f"added={len(self.added)}, "
            f"modified={len(self.modified)}, "
            f"deleted={len(self.deleted)})"
        )

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.modified or self.deleted)


# ──────────────────────────────────────────────────────────────────────
class IncrementalUpdater:
    """
    增量更新器。

    工作流：
    1. check_changes(project_root) → FileChanges
    2. apply_changes(graph, changes)

    当前状态：接口已定义，实现体为 TODO。
    MD5 缓存来源：图谱中 FileNode.file_md5 字段。
    """

    def __init__(self, graph: KnowledgeGraph) -> None:
        self.graph = graph
        # file_path → md5（启动时从图谱初始化）
        self._md5_cache: dict[str, str] = self._init_cache(graph)

    # ── 初始化 MD5 缓存 ───────────────────────────
    @staticmethod
    def _init_cache(graph: KnowledgeGraph) -> dict[str, str]:
        cache: dict[str, str] = {}
        for node in graph._node_map.values():
            if node.node_type == NodeType.FILE:
                cache[node.abs_path] = node.file_md5  # type: ignore[attr-defined]
        logger.debug(f"MD5 缓存初始化完成，共 {len(cache)} 个文件")
        return cache

    # ─────────────────────────────────────────────
    def check_changes(self, project_root: str) -> FileChanges:
        """
        对比现有图谱 MD5 缓存与磁盘，返回新增 / 修改 / 删除文件列表。
        TODO: 当前返回空变更，待实现。
        """
        # TODO: 实现文件变更检测
        # 参考逻辑：
        #   current_files = set(walk_project(project_root, ParserFactory.supported_suffixes()))
        #   last_files    = set(self._md5_cache.keys())
        #   added    = list(current_files - last_files)
        #   deleted  = list(last_files - current_files)
        #   modified = [f for f in current_files & last_files
        #               if file_md5(f) != self._md5_cache[f]]
        logger.warning("check_changes: TODO 未实现，返回空变更")
        return FileChanges(added=[], modified=[], deleted=[])

    def apply_changes(self, changes: FileChanges) -> None:
        """
        将 FileChanges 应用到图谱：
        - deleted  → remove_file
        - added    → parse + upsert
        - modified → remove_file + parse + upsert
        TODO: 当前为空实现。
        """
        # TODO: 实现增量更新逻辑
        logger.warning("apply_changes: TODO 未实现，跳过")

    def update_graph(self, project_root: str) -> None:
        """
        一步完成：check_changes → apply_changes。
        TODO: 依赖上面两个方法。
        """
        changes = self.check_changes(project_root)
        if not changes.has_changes:
            logger.info("增量更新：无文件变更，跳过")
            return
        logger.info(f"增量更新: {changes}")
        self.apply_changes(changes)

    # ── 单文件重建（apply_changes 内部使用）──────────
    def _rebuild_file(self, file_abs_path: str) -> None:
        """
        删除旧节点并重新解析单个文件。
        TODO: 实现细节。
        """
        # TODO:
        #   suffix  = os.path.splitext(file_abs_path)[1]
        #   if not ParserFactory.is_supported(suffix): return
        #   content = read_file(file_abs_path)
        #   if not content: return
        #   parser = ParserFactory.get(suffix)
        #   nodes, rels = parser.parse_file(file_abs_path, content)
        #   self.graph.remove_file(file_abs_path)
        #   self.graph.add_nodes(nodes)
        #   self.graph.add_relations(rels)
        #   self._md5_cache[file_abs_path] = file_md5(file_abs_path)
        logger.warning(f"_rebuild_file: TODO 未实现，跳过 {file_abs_path}")