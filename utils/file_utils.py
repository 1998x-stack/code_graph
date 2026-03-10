"""
Utilities for file operations.
"""

import os
import hashlib
from pathlib import Path
from typing import List, Generator, Tuple


def walk_project(root_path: str, exclude_patterns: List[str] = None) -> Generator[Path, None, None]:
    """
    Walk through a project directory and yield file paths.
    
    Args:
        root_path: The root directory to walk
        exclude_patterns: List of patterns to exclude (e.g., ['.git', '__pycache__', 'node_modules'])
    
    Yields:
        Path objects for each file in the project
    """
    if exclude_patterns is None:
        exclude_patterns = ['.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build']
    
    root = Path(root_path)
    
    for dirpath, dirnames, filenames in os.walk(root):
        # Remove excluded directories from the search
        dirnames[:] = [d for d in dirnames if d not in exclude_patterns]
        
        for filename in filenames:
            filepath = Path(dirpath) / filename
            
            # Check if the file should be excluded based on patterns
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern in str(filepath):
                    should_exclude = True
                    break
            
            if not should_exclude:
                yield filepath


def read_file(file_path: str) -> str:
    """
    Read the contents of a file.
    
    Args:
        file_path: Path to the file to read
    
    Returns:
        The contents of the file as a string
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def calculate_md5(file_path: str) -> str:
    """
    Calculate the MD5 hash of a file.
    
    Args:
        file_path: Path to the file
    
    Returns:
        The MD5 hash of the file as a hexadecimal string
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_file_info(file_path: str) -> dict:
    """
    Get information about a file including its content, size, and hash.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Dictionary with file information
    """
    path_obj = Path(file_path)
    
    return {
        'path': str(path_obj),
        'name': path_obj.name,
        'stem': path_obj.stem,
        'suffix': path_obj.suffix,
        'size': path_obj.stat().st_size,
        'md5': calculate_md5(file_path),
        'content': read_file(file_path)
    }