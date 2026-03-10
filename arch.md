# Code Knowledge Graph Builder — Architecture Map

## Project Purpose
Build a Python-first, pluggable code knowledge graph from any project path.
Input: project root path → Output: graph (nodes + relations) or bash/grep commands.

---

## Dependency Layer Model (STRICT — enforced top-down, no skip)

```
Layer 0: config/ schema/ utils/
    ↓         (foundation, zero internal deps)
Layer 1: core/parser/
    ↓         (AST → raw nodes/relations)
Layer 2: core/graph/
    ↓         (graph management, queries)
Layer 3: storage/  core/incremental/
    ↓         (persist + incremental stubs)
Layer 4: llm/
    ↓         (OpenAI, prompt templates)
Layer 5: cli/  main.py
              (entrypoint, wires everything)
```

**Rule**: Higher layers may import lower layers. Lower layers NEVER import higher layers.

---

## Module Breakdown

```
code_graph/
├── config/
│   └── settings.py          # pydantic-settings, env vars (OPENAI_*, LOG_*)
│
├── schema/
│   ├── enums.py             # NodeType(DIR/FILE/CLASS/FUNCTION), RelationType(HAS/IMPORT/CALL)
│   └── models.py            # Pydantic v2: DirNode, FileNode, ClassNode, FunctionNode
│                            #              HasRelation, ImportRelation, CallRelation
│
├── utils/
│   ├── logger.py            # loguru global setup + get_logger()
│   ├── id_gen.py            # Deterministic node IDs: "func::abs_path::ClassName::fn_name"
│   └── file_utils.py        # walk project, read files, md5 hash
│
├── core/
│   ├── parser/
│   │   ├── base.py          # ABC BaseParser: parse_file() → (nodes, relations)
│   │   ├── python_parser.py # Python ast: imports, classes, methods, call sites
│   │   └── factory.py       # ParserFactory: register/get by file suffix
│   │
│   ├── graph/
│   │   └── knowledge_graph.py  # KnowledgeGraph(networkx.DiGraph):
│   │                           #   add_node/add_relation, get_node, get_by_name
│   │                           #   get_call_chain, export_dict, load_dict
│   │
│   └── incremental/
│       └── updater.py       # IncrementalUpdater: check_changes(), update_graph()
│                            # [STUB — interfaces defined, bodies TODO]
│
├── storage/
│   └── graph_store.py       # GraphStore: save/load pickle + JSON
│
├── llm/
│   ├── prompts.py           # SYSTEM_PROMPT + USER_PROMPT_TEMPLATE
│   └── client.py            # OpenAIClient: generate_grep_command(graph, question)
│
├── cli/
│   └── args.py              # argparse: build / query subcommands
│
├── tests/
│   ├── fixtures/sample/     # Minimal Python project for tests
│   ├── test_parser.py
│   ├── test_graph.py
│   └── test_storage.py
│
├── main.py                  # Entry: parse_args → dispatch build/query
├── .env.example
└── requirements.txt
```

---

## Node ID Convention (deterministic, globally unique)

| Node Type | ID Pattern |
|-----------|-----------|
| Dir       | `dir::<abs_path>` |
| File      | `file::<abs_path>` |
| Class     | `class::<abs_path>::<ClassName>` |
| Function  | `func::<abs_path>::<ClassName>::<fn>` (method) |
| Function  | `func::<abs_path>::<fn>` (top-level) |

---

## Relation Types

| Type   | Source → Target         | Example |
|--------|------------------------|---------|
| HAS    | File → Class           | fileA.py contains class User |
| HAS    | Class → Function       | User contains login() |
| IMPORT | File → File/module     | fileA imports helper |
| CALL   | Function → Function    | login() calls check_token() |

---

## Build Order (Depth-First Closed Loops)

1. `requirements.txt` + `.env.example`
2. `config/` + `schema/` + `utils/`  ← **Layer 0 closed loop**
3. `core/parser/`                     ← **Layer 1 closed loop** (+ tests/fixtures)
4. `core/graph/`                      ← **Layer 2 closed loop**
5. `storage/` + `core/incremental/`   ← **Layer 3 closed loop**
6. `llm/`                             ← **Layer 4 closed loop**
7. `cli/` + `main.py`                 ← **Layer 5 — wire up**

---

## Incremental Update Contract (TODO stubs)

```python
class IncrementalUpdater:
    def check_changes(project_root) → (added, modified, deleted)  # TODO
    def update_graph(project_root)                                  # TODO
    def _rebuild_file(file_path)                                    # TODO
```
MD5 cache lives in FileNode.file_md5. On re-run, compare current md5 → skip unchanged.

---

## Environment Variables

```
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
LOG_FILE=./logs/code_graph.log
GRAPH_SAVE_PATH=./output/graph.pkl
```