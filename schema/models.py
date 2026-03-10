"""
Pydantic models for the knowledge graph schema.
"""

from typing import Optional, List
from pydantic import BaseModel
from .enums import NodeType, RelationType


class Node(BaseModel):
    id: str
    name: str
    type: NodeType
    path: Optional[str] = None
    properties: dict = {}


class Relation(BaseModel):
    id: str
    source_id: str
    target_id: str
    type: RelationType
    properties: dict = {}


class DirNode(Node):
    type: NodeType = NodeType.DIR


class FileNode(Node):
    type: NodeType = NodeType.FILE
    language: Optional[str] = None


class ClassNode(Node):
    type: NodeType = NodeType.CLASS
    methods: List[str] = []


class FunctionNode(Node):
    type: NodeType = NodeType.FUNCTION
    parameters: List[str] = []
    return_type: Optional[str] = None


class HasRelation(Relation):
    type: RelationType = RelationType.HAS


class ImportRelation(Relation):
    type: RelationType = RelationType.IMPORT


class CallRelation(Relation):
    type: RelationType = RelationType.CALL