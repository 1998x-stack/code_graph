#!/usr/bin/env python3
# main.py
# ── 项目入口 ──────────────────────────────────────────────────────────
from __future__ import annotations

import os
import sys

from tqdm import tqdm

from cli.args import parse_args
from config.settings import settings
from core.graph.knowledge_graph import KnowledgeGraph
from core.parser.factory import ParserFactory
from schema.enums import NodeType
from storage.graph_store import GraphStore
from utils.file_utils import walk_project, read_file
from utils.logger import get_logger

logger = get_logger(__name__)


# ═══════════════════════════════════════════════════════════════
#  build 命令
# ═══════════════════════════════════════════════════════════════
def cmd_build(args) -> None:
    project_path = os.path.abspath(args.project_path)
    output_path  = args.output
    json_path    = args.export_json
    show_progress = not args.no_progress

    logger.info(f"[BUILD] 项目路径: {project_path}")

    # 1. 收集目标文件
    suffixes    = ParserFactory.supported_suffixes()
    code_files  = walk_project(project_path, suffixes)
    if not code_files:
        logger.error("未找到任何支持的代码文件，请检查项目路径或扩展解析器注册")
        sys.exit(1)

    # 2. 初始化图谱
    graph = KnowledgeGraph(project_root=project_path)

    # 3. 逐文件解析
    iterator = tqdm(code_files, desc="解析文件", unit="file") if show_progress else code_files
    for file_path in iterator:
        content = read_file(file_path)
        if not content:
            logger.warning(f"跳过空文件: {file_path}")
            continue

        suffix = os.path.splitext(file_path)[1]
        try:
            parser = ParserFactory.get(suffix)
        except ValueError:
            logger.debug(f"无对应解析器，跳过: {file_path}")
            continue

        nodes, relations = parser.parse_file(file_path, content)
        if not nodes:
            continue

        graph.add_nodes(nodes)
        graph.add_relations(relations)

    # 4. 保存
    store = GraphStore(output_path)
    store.save(graph)

    if json_path:
        store.save_json(graph, json_path)

    print(f"\n✅  图谱构建完成")
    print(graph.summary())
    print(f"\n📦  已保存至: {output_path}")


# ═══════════════════════════════════════════════════════════════
#  query 命令
# ═══════════════════════════════════════════════════════════════
def cmd_query(args) -> None:
    question   = args.question
    graph_path = args.graph_path
    gen_cmd    = args.gen_cmd
    top_n      = args.top_n

    logger.info(f"[QUERY] 问题: {question}")

    # 1. 加载图谱
    store = GraphStore(graph_path)
    try:
        graph = store.load(graph_path)
    except FileNotFoundError:
        logger.error(f"图谱文件不存在: {graph_path}，请先运行 build 命令")
        sys.exit(1)

    # 2. 节点模糊匹配
    matched = graph.get_nodes_by_name(question, fuzzy=True)[:top_n]
    if matched:
        print(f"\n🔍  匹配到 {len(matched)} 个节点（最多显示 {top_n}）\n")
        for node in matched:
            _print_node(node)
    else:
        print("\n⚠️   未找到直接匹配的节点")

    # 3. 生成 bash/grep 指令
    if gen_cmd:
        if not settings.OPENAI_API_KEY:
            logger.error("未配置 OPENAI_API_KEY，无法生成 bash 指令")
            sys.exit(1)

        from llm.client import LLMClient
        try:
            client = LLMClient()
            result = client.generate_grep_command(graph, question)
            print("\n" + "═" * 60)
            print("🛠️   生成的定位指令")
            print("═" * 60)
            print(result)
            print("═" * 60)
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            sys.exit(1)


# ─────────────────────────────────────────────────────────────
def _print_node(node) -> None:
    """格式化打印单个节点"""
    type_label = node.node_type.value.upper()
    print(f"  [{type_label}] {node.name}")
    print(f"    路径  : {node.abs_path}")
    if hasattr(node, "start_line"):
        print(f"    行号  : {node.start_line} – {node.end_line}")
    if hasattr(node, "params"):
        print(f"    参数  : {node.params}")
    if hasattr(node, "docstring") and node.docstring:
        snippet = node.docstring[:120].replace("\n", " ")
        print(f"    文档  : {snippet}")
    print()


# ═══════════════════════════════════════════════════════════════
#  Dispatch
# ═══════════════════════════════════════════════════════════════
def main() -> None:
    args = parse_args()
    if args.command == "build":
        cmd_build(args)
    elif args.command == "query":
        cmd_query(args)


if __name__ == "__main__":
    main()