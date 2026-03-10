"""
Utilities for generating deterministic node IDs.
"""

import hashlib
from pathlib import Path
from typing import Optional


def generate_node_id(node_type: str, abs_path: str, *args) -> str:
    """
    Generate a deterministic node ID based on the node type, absolute path, 
    and additional identifiers.
    
    Args:
        node_type: The type of the node (e.g., 'func', 'class', 'file', 'dir')
        abs_path: The absolute path of the file/directory
        *args: Additional identifiers (e.g., class name, function name)
    
    Returns:
        A deterministic ID string in the format "type::path::arg1::arg2::..."
    """
    parts = [node_type, abs_path] + [str(arg) for arg in args]
    path_part = "::".join(parts)
    
    # Create a hash to ensure uniqueness while keeping the ID readable
    path_hash = hashlib.md5(path_part.encode()).hexdigest()[:8]
    
    return f"{path_part}::{path_hash}"


def generate_function_id(abs_path: str, class_name: Optional[str], fn_name: str) -> str:
    """
    Generate a deterministic ID for a function.
    
    Args:
        abs_path: The absolute path of the file containing the function
        class_name: The name of the class containing the function (None if standalone function)
        fn_name: The name of the function
    
    Returns:
        A deterministic ID string for the function
    """
    if class_name:
        return generate_node_id("func", abs_path, class_name, fn_name)
    else:
        return generate_node_id("func", abs_path, fn_name)


def generate_class_id(abs_path: str, class_name: str) -> str:
    """
    Generate a deterministic ID for a class.
    
    Args:
        abs_path: The absolute path of the file containing the class
        class_name: The name of the class
    
    Returns:
        A deterministic ID string for the class
    """
    return generate_node_id("class", abs_path, class_name)


def generate_file_id(abs_path: str) -> str:
    """
    Generate a deterministic ID for a file.
    
    Args:
        abs_path: The absolute path of the file
    
    Returns:
        A deterministic ID string for the file
    """
    return generate_node_id("file", abs_path)


def generate_dir_id(abs_path: str) -> str:
    """
    Generate a deterministic ID for a directory.
    
    Args:
        abs_path: The absolute path of the directory
    
    Returns:
        A deterministic ID string for the directory
    """
    return generate_node_id("dir", abs_path)