# tests/test_parser.py
"""
解析器单元测试（Ralph Wiggum Loop 第一道关口）
运行：pytest tests/test_parser.py -v
"""
import os
import sys

# 确保项目根在 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from core.parser.python_parser import PythonParser
from core.parser.factory import ParserFactory
from schema.enums import NodeType, RelationType


FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "sample")
SERVICE_PY  = os.path.join(FIXTURE_DIR, "service.py")
UTILS_PY    = os.path.join(FIXTURE_DIR, "utils.py")


# ─── fixtures ────────────────────────────────────────────────
@pytest.fixture
def parser() -> PythonParser:
    return PythonParser()


@pytest.fixture
def service_content() -> str:
    with open(SERVICE_PY, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def utils_content() -> str:
    with open(UTILS_PY, "r", encoding="utf-8") as f:
        return f.read()


# ─── 基础测试 ──────────────────────────────────────────────────
class TestPythonParserBasic:
    def test_supported_suffixes(self, parser):
        assert ".py" in parser.supported_suffixes

    def test_parse_returns_tuple(self, parser, service_content):
        nodes, rels = parser.parse_file(SERVICE_PY, service_content)
        assert isinstance(nodes, list)
        assert isinstance(rels, list)

    def test_file_node_created(self, parser, service_content):
        nodes, _ = parser.parse_file(SERVICE_PY, service_content)
        file_nodes = [n for n in nodes if n.node_type == NodeType.FILE]
        assert len(file_nodes) == 1
        assert file_nodes[0].name == "service.py"

    def test_class_node_created(self, parser, service_content):
        nodes, _ = parser.parse_file(SERVICE_PY, service_content)
        class_nodes = [n for n in nodes if n.node_type == NodeType.CLASS]
        names = [n.name for n in class_nodes]
        assert "UserService" in names

    def test_function_nodes_created(self, parser, service_content):
        nodes, _ = parser.parse_file(SERVICE_PY, service_content)
        func_nodes = [n for n in nodes if n.node_type == NodeType.FUNCTION]
        names = [n.name for n in func_nodes]
        assert "login"       in names
        assert "logout"      in names
        assert "get_service" in names

    def test_method_is_method_flag(self, parser, service_content):
        nodes, _ = parser.parse_file(SERVICE_PY, service_content)
        login = next((n for n in nodes if n.name == "login"), None)
        assert login is not None
        assert login.is_method is True

    def test_top_level_func_not_method(self, parser, service_content):
        nodes, _ = parser.parse_file(SERVICE_PY, service_content)
        get_svc = next((n for n in nodes if n.name == "get_service"), None)
        assert get_svc is not None
        assert get_svc.is_method is False


# ─── 行号测试 ──────────────────────────────────────────────────
class TestLineNumbers:
    def test_class_has_line_numbers(self, parser, service_content):
        nodes, _ = parser.parse_file(SERVICE_PY, service_content)
        cls = next((n for n in nodes if n.node_type == NodeType.CLASS), None)
        assert cls is not None
        assert cls.start_line >= 1
        assert cls.end_line >= cls.start_line

    def test_function_has_line_numbers(self, parser, service_content):
        nodes, _ = parser.parse_file(SERVICE_PY, service_content)
        for fn in nodes:
            if fn.node_type == NodeType.FUNCTION:
                assert fn.start_line >= 1
                assert fn.end_line >= fn.start_line


# ─── 关系测试 ──────────────────────────────────────────────────
class TestRelations:
    def test_has_relations_exist(self, parser, service_content):
        _, rels = parser.parse_file(SERVICE_PY, service_content)
        has_rels = [r for r in rels if r.relation_type == RelationType.HAS]
        assert len(has_rels) > 0

    def test_import_relations_exist(self, parser, service_content):
        _, rels = parser.parse_file(SERVICE_PY, service_content)
        imp_rels = [r for r in rels if r.relation_type == RelationType.IMPORT]
        assert len(imp_rels) > 0

    def test_call_relations_exist(self, parser, service_content):
        _, rels = parser.parse_file(SERVICE_PY, service_content)
        call_rels = [r for r in rels if r.relation_type == RelationType.CALL]
        assert len(call_rels) > 0

    def test_call_relation_has_line(self, parser, service_content):
        _, rels = parser.parse_file(SERVICE_PY, service_content)
        for rel in rels:
            if rel.relation_type == RelationType.CALL:
                assert rel.call_line is not None
                assert rel.call_line >= 1


# ─── 工厂测试 ──────────────────────────────────────────────────
class TestParserFactory:
    def test_get_python_parser(self):
        p = ParserFactory.get(".py")
        assert isinstance(p, PythonParser)

    def test_unsupported_suffix_raises(self):
        with pytest.raises(ValueError):
            ParserFactory.get(".java")

    def test_supported_suffixes_contains_py(self):
        assert ".py" in ParserFactory.supported_suffixes()


# ─── 边界测试 ──────────────────────────────────────────────────
class TestEdgeCases:
    def test_empty_file(self, parser):
        nodes, rels = parser.parse_file("/tmp/empty.py", "")
        # 空文件仍应生成 FileNode
        file_nodes = [n for n in nodes if n.node_type == NodeType.FILE]
        assert len(file_nodes) == 1

    def test_syntax_error_file(self, parser):
        nodes, rels = parser.parse_file("/tmp/bad.py", "def broken(")
        assert nodes == []
        assert rels == []

    def test_docstring_extracted(self, parser, service_content):
        nodes, _ = parser.parse_file(SERVICE_PY, service_content)
        cls = next((n for n in nodes if n.name == "UserService"), None)
        assert cls is not None
        assert "用户服务" in cls.docstring