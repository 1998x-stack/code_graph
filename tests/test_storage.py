"""
Tests for the graph storage module.
"""

import unittest
import tempfile
import os
from pathlib import Path
from ..storage.graph_store import GraphStore
from ..core.graph.knowledge_graph import KnowledgeGraph
from ..schema.models import Node, HasRelation
from ..schema.enums import NodeType, RelationType


class TestGraphStore(unittest.TestCase):
    """
    Tests for the GraphStore class.
    """
    
    def setUp(self):
        """
        Set up test fixtures before each test method.
        """
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.store = GraphStore(self.temp_dir)
        self.graph = KnowledgeGraph()
        
        # Add some test data to the graph
        node1 = Node(id="node1", name="Node 1", type=NodeType.FUNCTION)
        node2 = Node(id="node2", name="Node 2", type=NodeType.CLASS)
        self.graph.add_node(node1)
        self.graph.add_node(node2)
        
        relation = HasRelation(
            id="rel1",
            source_id="node1",
            target_id="node2",
            type=RelationType.HAS
        )
        self.graph.add_relation(relation)
    
    def tearDown(self):
        """
        Clean up after each test method.
        """
        # Remove the temporary directory and all its contents
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_save_and_load_pickle(self):
        """
        Test saving and loading a graph in pickle format.
        """
        filename = "test_graph.pkl"
        
        # Save the graph
        self.store.save_pickle(self.graph, filename)
        
        # Check that the file exists
        filepath = Path(self.temp_dir) / filename
        self.assertTrue(filepath.exists())
        
        # Load the graph
        loaded_graph = self.store.load_pickle(filename)
        
        # Check that the loaded graph has the same data
        self.assertEqual(len(loaded_graph.nodes), 2)
        self.assertEqual(len(loaded_graph.relations), 1)
        self.assertIn("node1", loaded_graph.nodes)
        self.assertIn("node2", loaded_graph.nodes)
        self.assertIn("rel1", loaded_graph.relations)
        
        # Check that the nodes and relations have the correct properties
        self.assertEqual(loaded_graph.nodes["node1"].name, "Node 1")
        self.assertEqual(loaded_graph.nodes["node2"].type, NodeType.CLASS)
        self.assertEqual(loaded_graph.relations["rel1"].source_id, "node1")
    
    def test_save_and_load_json(self):
        """
        Test saving and loading a graph in JSON format.
        """
        filename = "test_graph.json"
        
        # Save the graph
        self.store.save_json(self.graph, filename)
        
        # Check that the file exists
        filepath = Path(self.temp_dir) / filename
        self.assertTrue(filepath.exists())
        
        # Load the graph
        loaded_graph = self.store.load_json(filename)
        
        # Check that the loaded graph has the same data
        self.assertEqual(len(loaded_graph.nodes), 2)
        self.assertEqual(len(loaded_graph.relations), 1)
        self.assertIn("node1", loaded_graph.nodes)
        self.assertIn("node2", loaded_graph.nodes)
        self.assertIn("rel1", loaded_graph.relations)
        
        # Check that the nodes and relations have the correct properties
        self.assertEqual(loaded_graph.nodes["node1"].name, "Node 1")
        self.assertEqual(loaded_graph.nodes["node2"].type, NodeType.CLASS)
        self.assertEqual(loaded_graph.relations["rel1"].source_id, "node1")
    
    def test_save_and_load_generic(self):
        """
        Test saving and loading using the generic save/load methods.
        """
        # Test pickle format
        pickle_filename = "test_generic.pkl"
        self.store.save(self.graph, pickle_filename, "pickle")
        loaded_pickle_graph = self.store.load(pickle_filename, "pickle")
        
        self.assertEqual(len(loaded_pickle_graph.nodes), 2)
        
        # Test JSON format
        json_filename = "test_generic.json"
        self.store.save(self.graph, json_filename, "json")
        loaded_json_graph = self.store.load(json_filename, "json")
        
        self.assertEqual(len(loaded_json_graph.nodes), 2)
        
        # Test invalid format
        with self.assertRaises(ValueError):
            self.store.save(self.graph, "invalid.ext", "invalid_format")
        
        with self.assertRaises(ValueError):
            self.store.load("invalid.ext", "invalid_format")
    
    def test_exists_method(self):
        """
        Test the exists method.
        """
        filename = "test_exists.pkl"
        
        # File shouldn't exist yet
        self.assertFalse(self.store.exists(filename))
        
        # Save a file
        self.store.save_pickle(self.graph, filename)
        
        # Now the file should exist
        self.assertTrue(self.store.exists(filename))
        
        # Test with a non-existent file
        self.assertFalse(self.store.exists("nonexistent.pkl"))


if __name__ == '__main__':
    unittest.main()