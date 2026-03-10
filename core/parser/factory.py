"""
Parser factory for registering and retrieving parsers by file extension.
"""

from typing import Dict, Type
from .base import BaseParser


class ParserFactory:
    """
    Factory class for managing parsers by file extension.
    """
    
    _parsers: Dict[str, Type[BaseParser]] = {}
    
    @classmethod
    def register(cls, extension: str, parser_cls: Type[BaseParser]):
        """
        Register a parser for a specific file extension.
        
        Args:
            extension: File extension (e.g., '.py', '.js', '.ts')
            parser_cls: Parser class to register
        """
        cls._parsers[extension.lower()] = parser_cls
    
    @classmethod
    def get_parser(cls, extension: str) -> Type[BaseParser]:
        """
        Get a parser for the specified file extension.
        
        Args:
            extension: File extension (e.g., '.py', '.js', '.ts')
            
        Returns:
            Parser class for the extension, or None if not registered
        """
        return cls._parsers.get(extension.lower())
    
    @classmethod
    def create_parser(cls, extension: str) -> BaseParser:
        """
        Create an instance of the parser for the specified file extension.
        
        Args:
            extension: File extension (e.g., '.py', '.js', '.ts')
            
        Returns:
            Instance of the parser for the extension
        """
        parser_cls = cls.get_parser(extension)
        if parser_cls:
            return parser_cls()
        else:
            raise ValueError(f"No parser registered for extension: {extension}")


# Register default parsers
from .python_parser import PythonParser
ParserFactory.register('.py', PythonParser)