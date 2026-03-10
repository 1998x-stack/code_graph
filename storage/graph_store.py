"""
Graph storage implementation for saving and loading the knowledge graph.
"""

import json
import pickle
from pathlib import Path
from typing import Union
from ..core.graph.knowledge_graph import KnowledgeGraph


class GraphStore:
    """
    Storage interface for the knowledge graph.
    Supports both pickle (binary) and JSON (human-readable) formats.
    """
    
    def __init__(self, storage_path: str = "./graph_data"):
        """
        Initialize the graph store with a storage path.
        
        Args:
            storage_path: Directory path to store graph data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
    
    def save_pickle(self, graph: KnowledgeGraph, filename: str = "graph.pkl"):
        """
        Save the graph in pickle format.
        
        Args:
            graph: KnowledgeGraph instance to save
            filename: Name of the file to save to
        """
        filepath = self.storage_path / filename
        with open(filepath, 'wb') as f:
            pickle.dump({
                'nodes': graph.nodes,
                'relations': graph.relations,
                'nx_graph': graph.graph
            }, f)
    
    def load_pickle(self, filename: str = "graph.pkl") -> KnowledgeGraph:
        """
        Load the graph from pickle format.
        
        Args:
            filename: Name of the file to load from
            
        Returns:
            Loaded KnowledgeGraph instance
        """
        filepath = self.storage_path / filename
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        graph = KnowledgeGraph()
        graph.nodes = data['nodes']
        graph.relations = data['relations']
        graph.graph = data['nx_graph']
        
        return graph
    
    def save_json(self, graph: KnowledgeGraph, filename: str = "graph.json"):
        """
        Save the graph in JSON format.
        
        Args:
            graph: KnowledgeGraph instance to save
            filename: Name of the file to save to
        """
        filepath = self.storage_path / filename
        graph_data = graph.export_dict()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
    
    def load_json(self, filename: str = "graph.json") -> KnowledgeGraph:
        """
        Load the graph from JSON format.
        
        Args:
            filename: Name of the file to load from
            
        Returns:
            Loaded KnowledgeGraph instance
        """
        filepath = self.storage_path / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
        
        graph = KnowledgeGraph()
        graph.load_dict(graph_data)
        
        return graph
    
    def save(self, graph: KnowledgeGraph, filename: str = "graph.pkl", format: str = "pickle"):
        """
        Save the graph in the specified format.
        
        Args:
            graph: KnowledgeGraph instance to save
            filename: Name of the file to save to
            format: Format to save in - either 'pickle' or 'json'
        """
        if format.lower() == "pickle":
            self.save_pickle(graph, filename)
        elif format.lower() == "json":
            self.save_json(graph, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def load(self, filename: str = "graph.pkl", format: str = "pickle") -> KnowledgeGraph:
        """
        Load the graph from the specified format.
        
        Args:
            filename: Name of the file to load from
            format: Format to load from - either 'pickle' or 'json'
            
        Returns:
            Loaded KnowledgeGraph instance
        """
        if format.lower() == "pickle":
            return self.load_pickle(filename)
        elif format.lower() == "json":
            return self.load_json(filename)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def exists(self, filename: str) -> bool:
        """
        Check if a saved graph file exists.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            True if the file exists, False otherwise
        """
        return (self.storage_path / filename).exists()