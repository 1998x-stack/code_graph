# cli/args.py
# ── 命令行参数解析 ────────────────────────────────────────────────────
import argparse
import sys

from config.settings import settings


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="code-graph",
        description="Python 项目代码知识图谱构建 & 查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 构建图谱
  python main.py build -p ./my_project -o ./output/graph.pkl --export-json ./output/graph.json

  # 查询图谱（纯节点匹配）
  python main.py query -q "登录函数" -g ./output/graph.pkl

  # 查询 + 生成 bash/grep 指令
  python main.py query -q "哪些函数调用了 check_token" -g ./output/graph.pkl --gen-cmd
        """,
    )

    # 兼容低版本Python：手动处理subparsers的required（3.6-不支持required=True）
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True  # 显式设置（3.7+支持，3.6-需这样写）

    # ── build 子命令 ──────────────────────────────────
    build_p = subparsers.add_parser("build", help="解析项目，构建知识图谱")
    build_p.add_argument(
        "-p", "--project-path",
        required=True,
        metavar="PATH",
        help="目标 Python 项目根路径",
    )
    build_p.add_argument(
        "-o", "--output",
        default=settings.GRAPH_SAVE_PATH,
        metavar="PKL",
        help=f"图谱 pickle 保存路径（默认: {settings.GRAPH_SAVE_PATH}）",
    )
    build_p.add_argument(
        "--export-json",
        default=None,
        metavar="JSON",
        help="同时导出 JSON 格式（可选）",
    )
    build_p.add_argument(
        "--no-progress",
        action="store_true",
        help="关闭进度条（适合日志重定向场景）",
    )

    # ── query 子命令 ──────────────────────────────────
    query_p = subparsers.add_parser("query", help="查询图谱，可生成 bash/grep 指令")
    query_p.add_argument(
        "-q", "--question",
        required=True,
        metavar="TEXT",
        help="查询问题（自然语言）",
    )
    query_p.add_argument(
        "-g", "--graph-path",
        default=settings.GRAPH_SAVE_PATH,
        metavar="PKL",
        help=f"图谱 pickle 路径（默认: {settings.GRAPH_SAVE_PATH}）",
    )
    query_p.add_argument(
        "--gen-cmd",
        action="store_true",
        help="调用 LLM，根据图谱生成 bash/grep 定位指令",
    )
    query_p.add_argument(
        "--top-n",
        type=int,
        default=10,
        metavar="N",
        help="最多返回 N 个匹配节点（默认: 10）",
    )

    return parser


def parse_args() -> argparse.Namespace:
    import sys  # Add this if not already imported
    print("\n🔍 DEBUG: Raw sys.argv:", sys.argv)  # Show raw input
    parser = build_arg_parser()
    try:
        args = parser.parse_args()
        print("✅ DEBUG: Parsed args:", args)  # Show successful parse
    except argparse.ArgumentError as e:
        print(f"\n❌ DEBUG: Parse error: {e}", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    return args