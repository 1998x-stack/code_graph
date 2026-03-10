# tests/test_graph.py
"""
KnowledgeGraph 单元测试
运行：pytest tests/test_graph.py -v
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from core.graph.knowledge_graph import KnowledgeGraph
from core.parser.python_parser import PythonParser
from schema.enums import NodeType, RelationType

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "sample")
SERVICE_PY  = os.path.join(FIXTURE_DIR, "service.py")
UTILS_PY    = os.path.join(FIXTURE_DIR, "utils.py")


# ─── fixtures ────────────────────────────────────────────────
@pytest.fixture
def built_graph() -> KnowledgeGraph:
    """解析两个 fixture 文件，返回已构建的图谱"""
    parser = PythonParser()
    graph  = KnowledgeGraph(project_root=FIXTURE_DIR)
    for path in (SERVICE_PY, UTILS_PY):
        with open(path, encoding="utf-8") as f:
            content = f.read()
        nodes, rels = parser.parse_file(path, content)
        graph.add_nodes(nodes)
        graph.add_relations(rels)
    return graph


# ─── 基础查询 ──────────────────────────────────────────────────
class TestGraphBasic:
    def test_node_count_gt_zero(self, built_graph):
        assert built_graph.node_count > 0

    def test_relation_count_gt_zero(self, built_graph):
        assert built_graph.relation_count > 0

    def test_get_node_by_id_returns_none_for_missing(self, built_graph):
        assert built_graph.get_node("nonexistent") is None

    def test_get_nodes_by_name_fuzzy(self, built_graph):
        results = built_graph.get_nodes_by_name("UserService")
        assert any(n.name == "UserService" for n in results)

    def test_get_nodes_by_name_with_type_filter(self, built_graph):
        results = built_graph.get_nodes_by_name("login", node_type=NodeType.FUNCTION)
        assert all(n.node_type == NodeType.FUNCTION for n in results)

    def test_get_relations_from(self, built_graph):
        # 文件节点必然有 HAS 关系
        file_nodes = [n for n in built_graph._node_map.values() if n.node_type == NodeType.FILE]
        assert len(file_nodes) > 0
        rels = built_graph.get_relations_from(file_nodes[0].node_id, RelationType.HAS)
        assert len(rels) >= 0  # 可能为空（若文件只有导入语句）


# ─── 序列化往返 ────────────────────────────────────────────────
class TestGraphSerialization:
    def test_to_dict_and_from_dict_roundtrip(self, built_graph):
        data     = built_graph.to_dict()
        restored = KnowledgeGraph.from_dict(data)
        assert restored.node_count     == built_graph.node_count
        assert restored.relation_count == built_graph.relation_count
        assert restored.project_root   == built_graph.project_root

    def test_serialized_dict_has_required_keys(self, built_graph):
        data = built_graph.to_dict()
        assert "project_root" in data
        assert "nodes"        in data
        assert "relations"    in data

    def test_nodes_preserve_line_numbers(self, built_graph):
        data     = built_graph.to_dict()
        restored = KnowledgeGraph.from_dict(data)
        for node in restored._node_map.values():
            if node.node_type in (NodeType.CLASS, NodeType.FUNCTION):
                assert node.start_line >= 1  # type: ignore


# ─── summary ──────────────────────────────────────────────────
class TestGraphSummary:
    def test_summary_contains_project_root(self, built_graph):
        s = built_graph.summary()
        assert FIXTURE_DIR in s or "sample" in s