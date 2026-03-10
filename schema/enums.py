"""
Enum definitions for the knowledge graph schema.
"""

from enum import Enum


class NodeType(Enum):
    DIR = "DIR"
    FILE = "FILE"
    CLASS = "CLASS"
    FUNCTION = "FUNCTION"
    VARIABLE = "VARIABLE"
    MODULE = "MODULE"


class RelationType(Enum):
    HAS = "HAS"
    IMPORT = "IMPORT"
    CALL = "CALL"
    EXTENDS = "EXTENDS"
    USES = "USES"