# code_graph

**Build a pluggable code knowledge graph from any Python project — then query it as nodes/relations or as bash/grep commands.**

> 中文一句话：Python-first、可插拔的代码知识图谱构建器——输入项目根路径，输出知识图谱（节点+关系），或直接给出可执行的 bash/grep 定位指令，帮助你快速理解陌生代码库。

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](.) [![Status](https://img.shields.io/badge/status-experimental-orange)](.)

## What It Does（它解决什么）

> 中文要点：把一个代码仓库「解析成图」——目录/文件/类/函数为节点，包含/导入/调用为关系；之后无论 LLM 还是人工，都能按图或按命令定位代码。

- **AST 解析**：从代码生成结构化节点与关系（`PythonParser`，经 `ParserFactory` 注册扩展）
- **图管理**：`KnowledgeGraph` 增删改查，多粒度查询（`--top-n`）
- **双输出**：`.pkl` 图谱 或 `--export-json`，以及查询时 `--gen-cmd` 生成 bash/grep 定位指令
- **可插拔分层**：Parser / Graph / Storage / LLM / CLI 严格分层，低层永不 import 高层

## Quick Start（快速开始）

> 中文要点：`build` 先建图谱，`query` 再检索；`--gen-cmd` 让 LLM 基于图谱给出 grep/bash 定位命令。

```bash
pip install -r requirements.txt
```

```bash
# 1. 构建图谱
python main.py build -p ./my_project -o ./output/graph.pkl --export-json ./output/graph.json

# 2. 查询（纯节点匹配）
python main.py query -q "登录函数" -g ./output/graph.pkl

# 3. 查询 + 生成 bash/grep 定位指令
python main.py query -q "哪些函数调用了 check_token" -g ./output/graph.pkl --gen-cmd
```

## CLI Reference

```bash
# build — 解析项目，构建知识图谱
python main.py build -p <项目路径> \
  -o <graph.pkl> --export-json <graph.json> [--no-progress]

# query — 查询图谱，可生成 bash/grep 指令
python main.py query -q "<自然语言问题>" -g <graph.pkl> \
  [--gen-cmd] [--top-n N]
```

| 参数 | 默认 | 说明 |
|------|------|------|
| `build -p/--project-path` | 必填 | 目标项目根路径 |
| `build -o/--output` | `settings` | 图谱 pickle 保存路径 |
| `build --export-json` / `--no-progress` | — | 导出 JSON / 关闭进度条 |
| `query -q/--question` | 必填 | 查询问题（自然语言） |
| `query -g/--graph-path` | `settings` | 图谱 pickle 路径 |
| `query --gen-cmd` | — | 调用 LLM 生成 bash/grep 指令 |
| `query --top-n` | `10` | 最多返回 N 个匹配节点 |

## Architecture（分层架构）

```text
Layer 0: config/ schema/ utils/          # 基础层，零内部依赖
Layer 1: core/parser/                    # AST → 原始节点/关系
Layer 2: core/graph/                     # 图管理与查询
Layer 3: storage/ core/incremental/      # 持久化 + 增量更新
Layer 4: llm/                            # OpenAI + prompt 模板
Layer 5: cli/ main.py                    # 入口，接线
```

**节点与关系类型**（`schema/enums.py`）：

| 类型 | 枚举值 |
|------|--------|
| 节点 `NodeType` | `dir` / `file` / `class` / `function(method)` |
| 关系 `RelationType` | `HAS`（包含）、`IMPORT`（导入）、`CALL`（调用） |

> 设计规则：高层可 import 低层，低层**绝不** import 高层。详见 [`arch.md`](arch.md)。

## The Harness / 工程定位

`code_graph` 不是执行循环，而是 harness 家族的**代码理解前端**：它把「读代码」这一步产品化（AST→图→命令），让 agent 在陌生仓库里能按图索骥、按命令定位：

| 成员 | 侧重 | 与 code_graph 的关系 |
|------|------|-----------------------|
| `tiny/mid-harness` / `agent-loop` 等 | 代码**执行与编排** | code_graph 提供「执行前先看懂代码」的解析层 |
| `code_graph` | 代码知识图谱 | --- 本仓库（AST 解析 → 图 / 命令） |
| 代码搜索类能力 | 语义/文本检索 | code_graph 用 AST 结构 + LLM 生成指令，互补而非替代 |

## Package Layout

```text
code_graph/
├── main.py                 # 入口（build / query）
├── cli/args.py             # 命令行参数
├── config/settings.py      # 配置
├── schema/enums.py, models.py   # 节点/关系枚举与数据模型
├── core/
│   ├── parser/ (base, factory, python_parser)
│   ├── graph/  (knowledge_graph)
│   └── incremental/ (updater)
├── storage/graph_store.py  # 持久化
├── llm/                    # OpenAI 客户端 + prompts
├── utils/                  # id / logger / file utils
└── tests/                  # parser / graph / storage
```

## Development

```bash
python -m pytest tests/ -v
```

## License

MIT