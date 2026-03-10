"""
Knowledge graph implementation using NetworkX.
"""

import networkx as nx
from typing import List, Dict, Any, Optional, Union
from ...schema.models import Node, Relation, FileNode, ClassNode, FunctionNode
from ...schema.enums import NodeType, RelationType


class KnowledgeGraph:
    """
    A knowledge graph implementation using NetworkX as the underlying graph structure.
    """
    
    def __init__(self):
        """
        Initialize the knowledge graph with a directed NetworkX graph.
        """
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, Node] = {}
        self.relations: Dict[str, Relation] = {}
    
    def add_node(self, node: Node):
        """
        Add a node to the graph.
        
        Args:
            node: Node to add to the graph
        """
        self.nodes[node.id] = node
        self.graph.add_node(node.id, **node.dict())
    
    def add_relation(self, relation: Relation):
        """
        Add a relation (edge) to the graph.
        
        Args:
            relation: Relation to add to the graph
        """
        self.relations[relation.id] = relation
        self.graph.add_edge(
            relation.source_id, 
            relation.target_id, 
            id=relation.id,
            type=relation.type.value,
            **relation.properties
        )
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Get a node by its ID.
        
        Args:
            node_id: ID of the node to retrieve
            
        Returns:
            Node with the specified ID, or None if not found
        """
        return self.nodes.get(node_id)
    
    def get_by_name(self, name: str, node_type: Optional[NodeType] = None) -> List[Node]:
        """
        Get nodes by name, optionally filtered by type.
        
        Args:
            name: Name of the nodes to search for
            node_type: Optional filter for node type
            
        Returns:
            List of nodes with the specified name
        """
        result = []
        for node in self.nodes.values():
            if node.name == name:
                if node_type is None or node.type == node_type:
                    result.append(node)
        return result
    
    def get_call_chain(self, start_node_id: str) -> List[str]:
        """
        Get the call chain starting from a specific node.
        
        Args:
            start_node_id: ID of the starting node
            
        Returns:
            List of node IDs representing the call chain
        """
        if start_node_id not in self.graph:
            return []
        
        # Find all successors in the graph that represent call relations
        call_chain = []
        visited = set()
        
        def traverse(current_id):
            if current_id in visited:
                return
            visited.add(current_id)
            call_chain.append(current_id)
            
            # Get all outgoing edges that are call relations
            for successor in self.graph.successors(current_id):
                edge_data = self.graph.get_edge_data(current_id, successor)
                if edge_data and edge_data.get('type') == RelationType.CALL.value:
                    traverse(successor)
        
        traverse(start_node_id)
        return call_chain[1:]  # Exclude the starting node itself
    
    def export_dict(self) -> Dict[str, Any]:
        """
        Export the graph to a dictionary representation.
        
        Returns:
            Dictionary representation of the graph
        """
        return {
            'nodes': [node.dict() for node in self.nodes.values()],
            'relations': [relation.dict() for relation in self.relations.values()],
            'graph_structure': nx.node_link_data(self.graph)
        }
    
    def load_dict(self, data: Dict[str, Any]):
        """
        Load the graph from a dictionary representation.
        
        Args:
            data: Dictionary representation of the graph to load
        """
        # Clear existing data
        self.graph.clear()
        self.nodes = {}
        self.relations = {}
        
        # Load nodes
        for node_data in data['nodes']:
            node_type = node_data.get('type')
            if node_type == NodeType.FILE.value:
                node = FileNode(**node_data)
            elif node_type == NodeType.CLASS.value:
                node = ClassNode(**node_data)
            elif node_type == NodeType.FUNCTION.value:
                node = FunctionNode(**node_data)
            else:
                node = Node(**node_data)
            
            self.add_node(node)
        
        # Load relations
        for relation_data in data['relations']:
            relation_type = relation_data.get('type')
            if relation_type == RelationType.HAS.value:
                relation = HasRelation(**relation_data)
            elif relation_type == RelationType.IMPORT.value:
                relation = ImportRelation(**relation_data)
            elif relation_type == RelationType.CALL.value:
                relation = CallRelation(**relation_data)
            else:
                relation = Relation(**relation_data)
            
            self.add_relation(relation)
        
        # Load graph structure
        if 'graph_structure' in data:
            self.graph = nx.node_link_graph(data['graph_structure'])
    
    def get_neighbors(self, node_id: str, relation_type: Optional[RelationType] = None) -> List[Node]:
        """
        Get neighboring nodes connected to the specified node.
        
        Args:
            node_id: ID of the node to get neighbors for
            relation_type: Optional filter for relation type
            
        Returns:
            List of neighboring nodes
        """
        if node_id not in self.graph:
            return []
        
        neighbors = []
        for neighbor_id in self.graph.neighbors(node_id):
            if relation_type:
                # Check if the relation matches the specified type
                edge_data = self.graph.get_edge_data(node_id, neighbor_id)
                if edge_data and edge_data.get('type') == relation_type.value:
                    neighbor_node = self.get_node(neighbor_id)
                    if neighbor_node:
                        neighbors.append(neighbor_node)
            else:
                neighbor_node = self.get_node(neighbor_id)
                if neighbor_node:
                    neighbors.append(neighbor_node)
        
        return neighbors
    
    def get_subgraph(self, node_ids: List[str]) -> 'KnowledgeGraph':
        """
        Get a subgraph containing only the specified nodes and their connections.
        
        Args:
            node_ids: List of node IDs to include in the subgraph
            
        Returns:
            New KnowledgeGraph instance with the subgraph
        """
        subgraph_nx = self.graph.subgraph(node_ids)
        subgraph_kg = KnowledgeGraph()
        
        # Add nodes and relations that exist in the subgraph
        for node_id in node_ids:
            if node_id in self.nodes:
                subgraph_kg.add_node(self.nodes[node_id])
        
        for edge in subgraph_nx.edges(data=True):
            source_id, target_id, edge_data = edge
            relation_id = edge_data.get('id')
            
            if relation_id and relation_id in self.relations:
                subgraph_kg.add_relation(self.relations[relation_id])
        
        return subgraph_kg