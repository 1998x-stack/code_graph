# core/parser/python_parser.py
# ── Python AST 解析器 ────────────────────────────────────────────────
# 提取：FileNode / ClassNode / FunctionNode
#        HAS / IMPORT / CALL 关系
from __future__ import annotations

import ast
import os
from typing import Optional

from core.parser.base import BaseParser
from schema.enums import RelationType
from schema.models import (
    AnyNode, AnyRelation,
    FileNode, ClassNode, FunctionNode,
    HasRelation, ImportRelation, CallRelation,
)
from utils.file_utils import file_md5
from utils.id_gen import file_id, class_id, func_id, relation_id
from utils.logger import get_logger

logger = get_logger(__name__)


class PythonParser(BaseParser):
    """基于标准库 ast 的 Python 解析器，支持 Python 3.8+"""

    @property
    def supported_suffixes(self) -> list[str]:
        return [".py"]

    # ─────────────────────────────────────────────────
    def parse_file(
        self,
        file_abs_path: str,
        file_content: str,
    ) -> tuple[list[AnyNode], list[AnyRelation]]:

        path = os.path.abspath(file_abs_path)
        nodes:     list[AnyNode]     = []
        relations: list[AnyRelation] = []

        # ── 解析 AST ─────────────────────────────────
        try:
            tree = ast.parse(file_content, filename=path)
        except SyntaxError as e:
            logger.warning(f"AST 解析失败 {path}: {e}")
            return [], []

        # ── 1. 文件节点 ───────────────────────────────
        fid = file_id(path)
        f_node = FileNode(
            node_id=fid,
            name=os.path.basename(path),
            abs_path=path,
            file_suffix=".py",
            file_md5=file_md5(path),
            line_count=file_content.count("\n") + 1,
        )
        nodes.append(f_node)

        # ── 2. Import 语句 → ImportRelation ───────────
        # import_map: 本地名 → 目标字符串（用于 CALL 精准匹配）
        import_map: dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    local = alias.asname or alias.name
                    import_map[local] = alias.name
                    rel = ImportRelation(
                        relation_id=relation_id(fid, RelationType.IMPORT, alias.name),
                        source_id=fid,
                        target_id=alias.name,       # 模块路径字符串
                        import_alias=alias.asname,
                        imported_name=alias.name,
                    )
                    relations.append(rel)

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    local = alias.asname or alias.name
                    full  = f"{module}.{alias.name}" if module else alias.name
                    import_map[local] = full
                    rel = ImportRelation(
                        relation_id=relation_id(fid, RelationType.IMPORT, full),
                        source_id=fid,
                        target_id=full,
                        import_alias=alias.asname,
                        imported_name=alias.name,
                    )
                    relations.append(rel)

        # ── 3. 顶级类 & 函数 ──────────────────────────
        for stmt in tree.body:
            if isinstance(stmt, ast.ClassDef):
                cls_node, cls_rels = self._parse_class(
                    stmt, path, fid, import_map
                )
                nodes.append(cls_node)
                relations.append(HasRelation(
                    relation_id=relation_id(fid, RelationType.HAS, cls_node.node_id),
                    source_id=fid,
                    target_id=cls_node.node_id,
                ))
                nodes.extend(cls_rels[0])   # method nodes
                relations.extend(cls_rels[1])

            elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_node, fn_rels = self._parse_function(
                    stmt, path, fid, import_map, class_name=None
                )
                nodes.append(fn_node)
                relations.append(HasRelation(
                    relation_id=relation_id(fid, RelationType.HAS, fn_node.node_id),
                    source_id=fid,
                    target_id=fn_node.node_id,
                ))
                relations.extend(fn_rels)

        logger.debug(
            f"解析完成 {os.path.basename(path)}: "
            f"{len(nodes)} 节点, {len(relations)} 关系"
        )
        return nodes, relations

    # ─────────────────────────────────────────────────
    def _parse_class(
        self,
        node: ast.ClassDef,
        file_path: str,
        fid: str,
        import_map: dict[str, str],
    ) -> tuple[ClassNode, tuple[list[AnyNode], list[AnyRelation]]]:

        cid = class_id(file_path, node.name)
        super_classes = [
            (b.id if isinstance(b, ast.Name) else ast.unparse(b))
            for b in node.bases
        ]
        cls_node = ClassNode(
            node_id=cid,
            name=node.name,
            abs_path=file_path,
            docstring=ast.get_docstring(node) or "",
            super_classes=super_classes,
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            file_node_id=fid,
        )

        method_nodes:     list[AnyNode]     = []
        method_relations: list[AnyRelation] = []

        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_node, fn_rels = self._parse_function(
                    child, file_path, fid, import_map, class_name=node.name
                )
                method_nodes.append(fn_node)
                method_relations.append(HasRelation(
                    relation_id=relation_id(cid, RelationType.HAS, fn_node.node_id),
                    source_id=cid,
                    target_id=fn_node.node_id,
                ))
                method_relations.extend(fn_rels)

        return cls_node, (method_nodes, method_relations)

    # ─────────────────────────────────────────────────
    def _parse_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: str,
        fid: str,
        import_map: dict[str, str],
        class_name: Optional[str],
    ) -> tuple[FunctionNode, list[AnyRelation]]:

        fnid = func_id(file_path, node.name, class_name)

        # 参数签名
        try:
            params = ast.unparse(node.args)
        except Exception:
            params = "()"

        # 返回值类型
        return_type = "Any"
        if node.returns:
            try:
                return_type = ast.unparse(node.returns)
            except Exception:
                pass

        # 收集函数体内所有调用名（用于 CALL 关系）
        called_names: list[str] = []
        call_relations: list[AnyRelation] = []
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                call_name = _extract_call_name(sub.func)
                if call_name:
                    called_names.append(call_name)
                    # 目标尽量精准：先查 import_map，否则保留原始名
                    target = import_map.get(call_name, call_name)
                    call_relations.append(CallRelation(
                        relation_id=relation_id(fnid, RelationType.CALL, f"{target}:{sub.lineno}"),
                        source_id=fnid,
                        target_id=target,
                        call_line=sub.lineno,
                    ))

        fn_node = FunctionNode(
            node_id=fnid,
            name=node.name,
            abs_path=file_path,
            docstring=ast.get_docstring(node) or "",
            params=params,
            return_type=return_type,
            is_method=class_name is not None,
            class_node_id=class_id(file_path, class_name) if class_name else None,
            file_node_id=fid,
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            called_names=called_names,
        )
        return fn_node, call_relations


# ── 辅助：从 ast.Call.func 提取可读调用名 ────────────────
def _extract_call_name(func_node: ast.expr) -> str:
    """提取被调用名称：Name → 'func_name'，Attribute → 'method_name'"""
    if isinstance(func_node, ast.Name):
        return func_node.id
    if isinstance(func_node, ast.Attribute):
        return func_node.attr
    return ""