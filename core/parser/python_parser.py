"""
Python parser implementation using the AST module.
"""

import ast
from typing import Tuple, List, Dict, Set
from .base import BaseParser
from ...schema.models import (
    Node, Relation, FileNode, ClassNode, FunctionNode, 
    HasRelation, ImportRelation, CallRelation
)
from ...schema.enums import NodeType, RelationType
from ...utils.id_gen import (
    generate_file_id, generate_class_id, generate_function_id
)


class PythonParser(BaseParser):
    """
    Parser for Python files using the AST module.
    Extracts imports, classes, methods, and call sites.
    """
    
    def parse_file(self, file_path: str) -> Tuple[List[Node], List[Relation]]:
        """
        Parse a Python file and return a list of nodes and relations.
        
        Args:
            file_path: Path to the Python file to parse
            
        Returns:
            A tuple containing:
            - List of nodes extracted from the file
            - List of relations between the nodes
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # If the file has syntax errors, return empty lists
            return [], []
        
        # Initialize lists to store nodes and relations
        nodes: List[Node] = []
        relations: List[Relation] = []
        
        # Create a file node
        file_id = generate_file_id(file_path)
        file_node = FileNode(
            id=file_id,
            name=file_path.split('/')[-1],
            type=NodeType.FILE,
            path=file_path,
            language='python'
        )
        nodes.append(file_node)
        
        # Track imports to connect to other elements
        imports: Dict[str, str] = {}  # Maps imported name to module
        import_nodes: List[Node] = []
        import_relations: List[Relation] = []
        
        # Process AST nodes
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    imported_as = alias.asname or alias.name
                    
                    # Store import mapping
                    imports[imported_as] = module_name
                    
                    # Create import node
                    import_node = Node(
                        id=f"import::{file_path}::{imported_as}",
                        name=imported_as,
                        type=NodeType.MODULE,
                        path=file_path,
                        properties={'module': module_name}
                    )
                    import_nodes.append(import_node)
                    
                    # Create relation from file to import
                    import_rel = ImportRelation(
                        id=f"import_rel::{file_node.id}::{import_node.id}",
                        source_id=file_node.id,
                        target_id=import_node.id,
                        properties={'module': module_name}
                    )
                    import_relations.append(import_rel)
                    
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ''
                for alias in node.names:
                    imported_name = alias.name
                    imported_as = alias.asname or imported_name
                    
                    # Store import mapping
                    full_import_name = f"{module_name}.{imported_name}"
                    imports[imported_as] = full_import_name
                    
                    # Create import node
                    import_node = Node(
                        id=f"import::{file_path}::{imported_as}",
                        name=imported_as,
                        type=NodeType.MODULE,
                        path=file_path,
                        properties={'module': full_import_name}
                    )
                    import_nodes.append(import_node)
                    
                    # Create relation from file to import
                    import_rel = ImportRelation(
                        id=f"import_rel::{file_node.id}::{import_node.id}",
                        source_id=file_node.id,
                        target_id=import_node.id,
                        properties={'module': full_import_name}
                    )
                    import_relations.append(import_rel)
                    
            elif isinstance(node, ast.ClassDef):
                class_id = generate_class_id(file_path, node.name)
                
                # Create class node
                class_node = ClassNode(
                    id=class_id,
                    name=node.name,
                    type=NodeType.CLASS,
                    path=file_path,
                    methods=[]
                )
                nodes.append(class_node)
                
                # Create relation from file to class
                has_rel = HasRelation(
                    id=f"has_rel::{file_node.id}::{class_node.id}",
                    source_id=file_file.id,
                    target_id=class_node.id,
                    properties={}
                )
                relations.append(has_rel)
                
                # Process methods in the class
                method_names = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_names.append(item.name)
                        
                        # Create function node
                        func_id = generate_function_id(file_path, node.name, item.name)
                        func_node = FunctionNode(
                            id=func_id,
                            name=item.name,
                            type=NodeType.FUNCTION,
                            path=file_path,
                            parameters=[],
                            return_type=None
                        )
                        nodes.append(func_node)
                        
                        # Create relation from class to method
                        method_rel = HasRelation(
                            id=f"has_rel::{class_node.id}::{func_node.id}",
                            source_id=class_node.id,
                            target_id=func_node.id,
                            properties={}
                        )
                        relations.append(method_rel)
                        
                        # Extract parameters
                        params = []
                        for arg in item.args.args:
                            if arg.arg != 'self':  # Exclude 'self' parameter
                                params.append(arg.arg)
                        func_node.parameters = params
                        
                        # Look for calls within the function
                        calls = self._extract_calls(item, file_path, func_id)
                        for call_target in calls:
                            # Create call relation
                            call_rel = CallRelation(
                                id=f"call_rel::{func_node.id}::{call_target}",
                                source_id=func_node.id,
                                target_id=call_target,
                                properties={}
                            )
                            relations.append(call_rel)
                
                # Update class node with method names
                class_node.methods = method_names
                
            elif isinstance(node, ast.FunctionDef):
                # Skip if this function is inside a class (already processed)
                if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) 
                          if hasattr(parent, 'body') and node in parent.body):
                    func_id = generate_function_id(file_path, None, node.name)
                    
                    # Create function node
                    func_node = FunctionNode(
                        id=func_id,
                        name=node.name,
                        type=NodeType.FUNCTION,
                        path=file_path,
                        parameters=[],
                        return_type=None
                    )
                    nodes.append(func_node)
                    
                    # Create relation from file to function
                    has_rel = HasRelation(
                        id=f"has_rel::{file_node.id}::{func_node.id}",
                        source_id=file_node.id,
                        target_id=func_node.id,
                        properties={}
                    )
                    relations.append(has_rel)
                    
                    # Extract parameters
                    params = []
                    for arg in node.args.args:
                        params.append(arg.arg)
                    func_node.parameters = params
                    
                    # Look for calls within the function
                    calls = self._extract_calls(node, file_path, func_id)
                    for call_target in calls:
                        # Create call relation
                        call_rel = CallRelation(
                            id=f"call_rel::{func_node.id}::{call_target}",
                            source_id=func_node.id,
                            target_id=call_target,
                            properties={}
                        )
                        relations.append(call_rel)
        
        # Add all import nodes and relations
        nodes.extend(import_nodes)
        relations.extend(import_relations)
        
        return nodes, relations
    
    def _extract_calls(self, node: ast.AST, file_path: str, source_func_id: str) -> List[str]:
        """
        Extract function/method calls from an AST node.
        
        Args:
            node: AST node to extract calls from
            file_path: Path to the file being parsed
            source_func_id: ID of the source function
            
        Returns:
            List of target IDs for calls made in the node
        """
        calls = set()
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                # Extract the function being called
                if isinstance(child.func, ast.Name):
                    # Direct function call
                    func_name = child.func.id
                    # Check if this is an imported name
                    if func_name in imports:
                        # This is a call to an imported function
                        target_id = f"import::{file_path}::{func_name}"
                        calls.add(target_id)
                    else:
                        # This is a local function call - we'd need more context to resolve
                        # For now, we'll add it as a potential local call
                        local_func_id = generate_function_id(file_path, None, func_name)
                        calls.add(local_func_id)
                elif isinstance(child.func, ast.Attribute):
                    # Method call or attribute access
                    attr_name = child.func.attr
                    value = child.func.value
                    
                    if isinstance(value, ast.Name):
                        # Could be obj.method() or a module.function() call
                        obj_name = value.id
                        if obj_name in imports:
                            # This is likely a call to an imported module function
                            target_id = f"import::{file_path}::{obj_name}.{attr_name}"
                            calls.add(target_id)
                        else:
                            # This could be a call to a local object method
                            # For now, we'll represent it generically
                            calls.add(f"method::{file_path}::{obj_name}::{attr_name}")
                    elif isinstance(value, ast.Call):
                        # Chained call like func()().method()
                        # Extract the inner call target
                        inner_calls = self._extract_calls(value, file_path, source_func_id)
                        calls.update(inner_calls)
        
        return list(calls)