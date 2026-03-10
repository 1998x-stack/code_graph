"""
Tests for the knowledge graph module.
"""

import unittest
from ..core.graph.knowledge_graph import KnowledgeGraph
from ..schema.models import Node, FileNode, ClassNode, FunctionNode, HasRelation
from ..schema.enums import NodeType, RelationType


class TestKnowledgeGraph(unittest.TestCase):
    """
    Tests for the KnowledgeGraph class.
    """
    
    def setUp(self):
        """
        Set up test fixtures before each test method.
        """
        self.graph = KnowledgeGraph()
    
    def test_add_node(self):
        """
        Test adding a node to the graph.
        """
        node = Node(id="test_node", name="Test Node", type=NodeType.FUNCTION)
        self.graph.add_node(node)
        
        # Check that the node was added
        self.assertEqual(len(self.graph.nodes), 1)
        self.assertIn("test_node", self.graph.nodes)
        self.assertEqual(self.graph.nodes["test_node"].name, "Test Node")
        
        # Check that the node was added to the NetworkX graph
        self.assertIn("test_node", self.graph.graph.nodes)
    
    def test_add_relation(self):
        """
        Test adding a relation to the graph.
        """
        # Add two nodes first
        node1 = Node(id="node1", name="Node 1", type=NodeType.FUNCTION)
        node2 = Node(id="node2", name="Node 2", type=NodeType.FUNCTION)
        self.graph.add_node(node1)
        self.graph.add_node(node2)
        
        # Add a relation between them
        relation = HasRelation(
            id="rel1",
            source_id="node1",
            target_id="node2",
            type=RelationType.HAS
        )
        self.graph.add_relation(relation)
        
        # Check that the relation was added
        self.assertEqual(len(self.graph.relations), 1)
        self.assertIn("rel1", self.graph.relations)
        self.assertEqual(self.graph.relations["rel1"].source_id, "node1")
        
        # Check that the edge was added to the NetworkX graph
        self.assertTrue(self.graph.graph.has_edge("node1", "node2"))
    
    def test_get_node(self):
        """
        Test getting a node by ID.
        """
        node = Node(id="test_node", name="Test Node", type=NodeType.FUNCTION)
        self.graph.add_node(node)
        
        # Get the node by ID
        retrieved_node = self.graph.get_node("test_node")
        
        # Check that the right node was returned
        self.assertIsNotNone(retrieved_node)
        self.assertEqual(retrieved_node.id, "test_node")
        self.assertEqual(retrieved_node.name, "Test Node")
    
    def test_get_by_name(self):
        """
        Test getting nodes by name.
        """
        node1 = Node(id="node1", name="common_name", type=NodeType.FUNCTION)
        node2 = Node(id="node2", name="common_name", type=NodeType.CLASS)
        node3 = Node(id="node3", name="different_name", type=NodeType.FUNCTION)
        self.graph.add_node(node1)
        self.graph.add_node(node2)
        self.graph.add_node(node3)
        
        # Get all nodes with the common name
        nodes = self.graph.get_by_name("common_name")
        
        # Check that we got both nodes with the common name
        self.assertEqual(len(nodes), 2)
        node_ids = [node.id for node in nodes]
        self.assertIn("node1", node_ids)
        self.assertIn("node2", node_ids)
        
        # Get nodes with the common name and FUNCTION type
        nodes = self.graph.get_by_name("common_name", NodeType.FUNCTION)
        
        # Check that we got only the FUNCTION node
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].id, "node1")
    
    def test_export_and_load_dict(self):
        """
        Test exporting and loading the graph as a dictionary.
        """
        # Add some nodes and relations
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
        
        # Export the graph
        exported_data = self.graph.export_dict()
        
        # Create a new graph and load the data
        new_graph = KnowledgeGraph()
        new_graph.load_dict(exported_data)
        
        # Check that the new graph has the same nodes and relations
        self.assertEqual(len(new_graph.nodes), 2)
        self.assertEqual(len(new_graph.relations), 1)
        self.assertIn("node1", new_graph.nodes)
        self.assertIn("node2", new_graph.nodes)
        self.assertIn("rel1", new_graph.relations)
        
        # Check that the nodes and relations have the correct properties
        self.assertEqual(new_graph.nodes["node1"].name, "Node 1")
        self.assertEqual(new_graph.nodes["node2"].type, NodeType.CLASS)
        self.assertEqual(new_graph.relations["rel1"].source_id, "node1")
    
    def test_get_neighbors(self):
        """
        Test getting neighboring nodes.
        """
        # Add nodes
        node1 = Node(id="node1", name="Node 1", type=NodeType.FUNCTION)
        node2 = Node(id="node2", name="Node 2", type=NodeType.CLASS)
        node3 = Node(id="node3", name="Node 3", type=NodeType.VARIABLE)
        self.graph.add_node(node1)
        self.graph.add_node(node2)
        self.graph.add_node(node3)
        
        # Add relations of different types
        rel1 = HasRelation(
            id="has_rel",
            source_id="node1",
            target_id="node2",
            type=RelationType.HAS
        )
        self.graph.add_relation(rel1)
        
        import_rel = HasRelation(  # Using HasRelation for simplicity in test
            id="import_rel",
            source_id="node1",
            target_id="node3",
            type=RelationType.IMPORT  # This won't match HAS filter
        )
        self.graph.add_relation(import_rel)
        
        # Get all neighbors of node1
        all_neighbors = self.graph.get_neighbors("node1")
        self.assertEqual(len(all_neighbors), 2)
        
        # Get only neighbors connected by HAS relations
        has_neighbors = self.graph.get_neighbors("node1", RelationType.HAS)
        self.assertEqual(len(has_neighbors), 1)
        self.assertEqual(has_neighbors[0].id, "node2")


if __name__ == '__main__':
    unittest.main()