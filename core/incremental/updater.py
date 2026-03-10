"""
Incremental updater for the knowledge graph.
"""

from typing import Dict, List, Set
from ...utils.file_utils import calculate_md5, walk_project
from ...core.graph.knowledge_graph import KnowledgeGraph
from ...core.parser.factory import ParserFactory
from ...schema.models import Node, Relation


class IncrementalUpdater:
    """
    Handles incremental updates to the knowledge graph based on file changes.
    """
    
    def __init__(self, graph: KnowledgeGraph):
        """
        Initialize the incremental updater with a knowledge graph.
        
        Args:
            graph: The knowledge graph to update
        """
        self.graph = graph
        self.file_hashes: Dict[str, str] = {}
    
    def check_changes(self, project_root: str, exclude_patterns: List[str] = None) -> Dict[str, str]:
        """
        Check for changes in the project files by comparing MD5 hashes.
        
        Args:
            project_root: Root directory of the project
            exclude_patterns: List of patterns to exclude from the scan
            
        Returns:
            Dictionary mapping file paths to change types ('added', 'modified', 'deleted')
        """
        current_files = set()
        changes = {}
        
        # Get all current files in the project
        for file_path in walk_project(project_root, exclude_patterns):
            current_files.add(str(file_path))
            file_str = str(file_path)
            
            # Calculate current hash
            current_hash = calculate_md5(file_str)
            
            # Compare with stored hash
            if file_str not in self.file_hashes:
                # File is new
                changes[file_str] = 'added'
            elif self.file_hashes[file_str] != current_hash:
                # File has been modified
                changes[file_str] = 'modified'
            
            # Update stored hash
            self.file_hashes[file_str] = current_hash
        
        # Check for deleted files
        for stored_file in self.file_hashes:
            if stored_file not in current_files:
                changes[stored_file] = 'deleted'
                # Remove from hashes since file no longer exists
                del self.file_hashes[stored_file]
        
        return changes
    
    def update_graph(self, project_root: str, exclude_patterns: List[str] = None):
        """
        Update the knowledge graph based on file changes.
        
        Args:
            project_root: Root directory of the project
            exclude_patterns: List of patterns to exclude from the update
        """
        changes = self.check_changes(project_root, exclude_patterns)
        
        # Process added or modified files
        for file_path, change_type in changes.items():
            if change_type in ['added', 'modified']:
                self._process_file(file_path)
            elif change_type == 'deleted':
                self._remove_file_from_graph(file_path)
    
    def _process_file(self, file_path: str):
        """
        Process a single file and update the graph accordingly.
        
        Args:
            file_path: Path to the file to process
        """
        # Determine the file extension
        ext = '.' + file_path.split('.')[-1]
        
        # Get the appropriate parser
        parser = ParserFactory.create_parser(ext)
        
        # Parse the file to get nodes and relations
        nodes, relations = parser.parse_file(file_path)
        
        # Remove any existing nodes/relations for this file
        self._remove_file_nodes(file_path)
        
        # Add new nodes and relations to the graph
        for node in nodes:
            self.graph.add_node(node)
        
        for relation in relations:
            self.graph.add_relation(relation)
    
    def _remove_file_nodes(self, file_path: str):
        """
        Remove all nodes and relations associated with a file.
        
        Args:
            file_path: Path to the file whose nodes should be removed
        """
        # Find nodes associated with this file
        nodes_to_remove = []
        for node_id, node in self.graph.nodes.items():
            if node.path == file_path:
                nodes_to_remove.append(node_id)
        
        # Remove nodes and their relations
        for node_id in nodes_to_remove:
            self._remove_node_and_relations(node_id)
    
    def _remove_node_and_relations(self, node_id: str):
        """
        Remove a node and all relations associated with it.
        
        Args:
            node_id: ID of the node to remove
        """
        # Find relations to remove
        relations_to_remove = []
        for rel_id, relation in self.graph.relations.items():
            if relation.source_id == node_id or relation.target_id == node_id:
                relations_to_remove.append(rel_id)
        
        # Remove relations first
        for rel_id in relations_to_remove:
            del self.graph.relations[rel_id]
            # Also remove from NetworkX graph
            try:
                self.graph.graph.remove_edge(relation.source_id, relation.target_id)
            except nx.NetworkXError:
                pass  # Edge might not exist
        
        # Then remove the node
        if node_id in self.graph.nodes:
            del self.graph.nodes[node_id]
            try:
                self.graph.graph.remove_node(node_id)
            except nx.NetworkXError:
                pass  # Node might not exist
    
    def _remove_file_from_graph(self, file_path: str):
        """
        Remove all traces of a file from the graph when the file is deleted.
        
        Args:
            file_path: Path to the deleted file
        """
        self._remove_file_nodes(file_path)