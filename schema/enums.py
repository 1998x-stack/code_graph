# schema/enums.py
# ── 节点类型 & 关系类型枚举 ────────────────────────────────────────────
from enum import Enum


class NodeType(str, Enum):
    """所有节点类型"""
    DIR      = "dir"       # 目录
    FILE     = "file"      # 文件
    CLASS    = "class"     # 类
    FUNCTION = "function"  # 函数 / 方法


class RelationType(str, Enum):
    """所有关系类型"""
    HAS    = "HAS"    # 包含: file→class, class→function, dir→file
    IMPORT = "IMPORT" # 导入: file→file 或 file→module
    CALL   = "CALL"   # 调用: function→function