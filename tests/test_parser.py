"""
Tests for the parser module.
"""

import unittest
from pathlib import Path
from ..core.parser.python_parser import PythonParser
from ..core.parser.factory import ParserFactory
from ..schema.enums import NodeType, RelationType


class TestPythonParser(unittest.TestCase):
    """
    Tests for the PythonParser class.
    """
    
    def setUp(self):
        """
        Set up test fixtures before each test method.
        """
        self.parser = PythonParser()
        self.sample_file = Path(__file__).parent / "fixtures" / "sample" / "hello.py"
    
    def test_parse_file_returns_nodes_and_relations(self):
        """
        Test that parsing a file returns nodes and relations.
        """
        nodes, relations = self.parser.parse_file(str(self.sample_file))
        
        # Check that we have nodes and relations
        self.assertGreater(len(nodes), 0)
        self.assertGreater(len(relations), 0)
        
        # Check that nodes have the expected properties
        for node in nodes:
            self.assertIsNotNone(node.id)
            self.assertIsNotNone(node.name)
            self.assertIsNotNone(node.type)
    
    def test_parse_file_creates_function_nodes(self):
        """
        Test that parsing a file creates function nodes.
        """
        nodes, relations = self.parser.parse_file(str(self.sample_file))
        
        # Find function nodes
        function_nodes = [node for node in nodes if node.type == NodeType.FUNCTION]
        
        # Check that we have the expected functions
        function_names = [node.name for node in function_nodes]
        expected_functions = ["greet", "farewell", "greet", "farewell", "main"]
        
        for expected_func in expected_functions:
            self.assertIn(expected_func, function_names)
    
    def test_parse_file_creates_class_nodes(self):
        """
        Test that parsing a file creates class nodes.
        """
        nodes, relations = self.parser.parse_file(str(self.sample_file))
        
        # Find class nodes
        class_nodes = [node for node in nodes if node.type == NodeType.CLASS]
        
        # Check that we have the expected class
        class_names = [node.name for node in class_nodes]
        self.assertIn("Greeter", class_names)
    
    def test_parse_file_creates_has_relations(self):
        """
        Test that parsing a file creates HAS relations.
        """
        nodes, relations = self.parser.parse_file(str(self.sample_file))
        
        # Find HAS relations
        has_relations = [rel for rel in relations if rel.type == RelationType.HAS]
        
        # Check that we have HAS relations
        self.assertGreater(len(has_relations), 0)
    
    def test_parse_file_creates_call_relations(self):
        """
        Test that parsing a file creates CALL relations.
        """
        nodes, relations = self.parser.parse_file(str(self.sample_file))
        
        # Find CALL relations
        call_relations = [rel for rel in relations if rel.type == RelationType.CALL]
        
        # Check that we have CALL relations (at least the calls from Greeter methods to standalone functions)
        self.assertGreater(len(call_relations), 0)


class TestParserFactory(unittest.TestCase):
    """
    Tests for the ParserFactory class.
    """
    
    def test_get_python_parser(self):
        """
        Test that the factory returns a Python parser for .py files.
        """
        parser = ParserFactory.create_parser('.py')
        
        from ..core.parser.python_parser import PythonParser
        self.assertIsInstance(parser, PythonParser)
    
    def test_register_new_parser(self):
        """
        Test that we can register and retrieve a new parser type.
        """
        from ..core.parser.base import BaseParser
        
        class MockParser(BaseParser):
            def parse_file(self, file_path: str):
                return [], []
        
        # Register a new parser type
        ParserFactory.register('.mock', MockParser)
        
        # Retrieve the parser
        parser = ParserFactory.get_parser('.mock')
        
        # Check that we got the right parser
        self.assertEqual(parser, MockParser)
        
        # Clean up by removing the test parser
        if '.mock' in ParserFactory._parsers:
            del ParserFactory._parsers['.mock']


if __name__ == '__main__':
    unittest.main()