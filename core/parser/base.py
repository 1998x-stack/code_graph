"""
Base parser class definition.
"""

from abc import ABC, abstractmethod
from typing import Tuple, List
from ...schema.models import Node, Relation


class BaseParser(ABC):
    """
    Abstract base class for all parsers.
    """
    
    @abstractmethod
    def parse_file(self, file_path: str) -> Tuple[List[Node], List[Relation]]:
        """
        Parse a file and return a list of nodes and relations.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            A tuple containing:
            - List of nodes extracted from the file
            - List of relations between the nodes
        """
        pass