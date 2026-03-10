# schema/models.py
# ── 节点 & 关系 Pydantic v2 模型 ──────────────────────────────────────
from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from schema.enums import NodeType, RelationType


# ═══════════════════════════════════════════════════════
#  节点基类
# ═══════════════════════════════════════════════════════
class BaseNode(BaseModel):
    """所有节点的公共字段"""
    node_id:   str      = Field(description="全局唯一 ID，由 id_gen 生成")
    node_type: NodeType = Field(description="节点类型")
    name:      str      = Field(description="节点名称（目录/文件/类/函数名）")
    abs_path:  str      = Field(description="绝对路径")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    extra:     dict     = Field(default_factory=dict, description="扩展字段，预留")


# ── 目录节点 ──────────────────────────────────────────
class DirNode(BaseNode):
    node_type:  NodeType = NodeType.DIR
    parent_dir: Optional[str] = Field(default=None, description="父目录绝对路径")


# ── 文件节点 ──────────────────────────────────────────
class FileNode(BaseNode):
    node_type:   NodeType = NodeType.FILE
    file_suffix: str      = Field(description="文件后缀，如 .py")
    file_md5:    str      = Field(description="文件 MD5，用于增量更新")
    line_count:  int      = Field(description="文件总行数")


# ── 类节点 ────────────────────────────────────────────
class ClassNode(BaseNode):
    node_type:    NodeType     = NodeType.CLASS
    docstring:    str          = Field(default="", description="类文档字符串")
    super_classes: list[str]   = Field(default_factory=list, description="父类列表")
    start_line:   int          = Field(description="类定义起始行（1-based）")
    end_line:     int          = Field(description="类定义结束行（1-based）")
    file_node_id: str          = Field(description="所属 FileNode 的 node_id")


# ── 函数/方法节点 ─────────────────────────────────────
class FunctionNode(BaseNode):
    node_type:      NodeType         = NodeType.FUNCTION
    docstring:      str              = Field(default="", description="函数文档字符串")
    params:         str              = Field(default="()", description="参数签名字符串")
    return_type:    str              = Field(default="Any", description="返回值类型注解")
    is_method:      bool             = Field(default=False, description="是否是类方法")
    class_node_id:  Optional[str]    = Field(default=None, description="所属 ClassNode.node_id，顶级函数为 None")
    file_node_id:   str              = Field(description="所属 FileNode 的 node_id")
    start_line:     int              = Field(description="函数定义起始行（1-based）")
    end_line:       int              = Field(description="函数定义结束行（1-based）")
    called_names:   list[str]        = Field(default_factory=list, description="函数体内所有被调用的名称（原始名）")


# 统一节点联合类型
AnyNode = DirNode | FileNode | ClassNode | FunctionNode


# ═══════════════════════════════════════════════════════
#  关系基类
# ═══════════════════════════════════════════════════════
class BaseRelation(BaseModel):
    """所有关系的公共字段"""
    relation_id:   str          = Field(description="全局唯一关系 ID")
    relation_type: RelationType = Field(description="关系类型")
    source_id:     str          = Field(description="源节点 node_id")
    target_id:     str          = Field(description="目标节点 node_id")
    created_at:    datetime     = Field(default_factory=datetime.now)
    extra:         dict         = Field(default_factory=dict)


# ── HAS 关系 ──────────────────────────────────────────
class HasRelation(BaseRelation):
    """包含关系：dir→file, file→class, class→function"""
    relation_type: RelationType = RelationType.HAS


# ── IMPORT 关系 ───────────────────────────────────────
class ImportRelation(BaseRelation):
    """导入关系：file → 被导入模块/类/函数"""
    relation_type: RelationType = RelationType.IMPORT
    import_alias:  Optional[str] = Field(default=None, description="import 别名，如 import numpy as np")
    imported_name: str           = Field(default="", description="被导入的具体名称（from x import Y 中的 Y）")


# ── CALL 关系 ─────────────────────────────────────────
class CallRelation(BaseRelation):
    """调用关系：function → function"""
    relation_type: RelationType = RelationType.CALL
    call_line:     Optional[int] = Field(default=None, description="调用发生的行号")


# 统一关系联合类型
AnyRelation = HasRelation | ImportRelation | CallRelation