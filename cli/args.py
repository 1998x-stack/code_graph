"""
Command line argument parsing for the code graph application.
"""

import argparse


def parse_args():
    """
    Parse command line arguments for the code graph application.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Code Graph - A tool for analyzing and navigating codebases using knowledge graphs"
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Build command - analyze a project and build the knowledge graph
    build_parser = subparsers.add_parser(
        'build', 
        help='Analyze a project and build the knowledge graph'
    )
    build_parser.add_argument(
        'project_path',
        type=str,
        help='Path to the project to analyze'
    )
    build_parser.add_argument(
        '--output',
        type=str,
        default='./graph_data/graph.pkl',
        help='Output file for the knowledge graph (default: ./graph_data/graph.pkl)'
    )
    build_parser.add_argument(
        '--exclude',
        type=str,
        nargs='*',
        default=['.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build'],
        help='Patterns to exclude from analysis (default: .git __pycache__ node_modules .venv venv dist build)'
    )
    
    # Query command - query the knowledge graph
    query_parser = subparsers.add_parser(
        'query',
        help='Query the knowledge graph'
    )
    query_parser.add_argument(
        'question',
        type=str,
        help='Natural language question about the codebase'
    )
    query_parser.add_argument(
        '--graph-path',
        type=str,
        default='./graph_data/graph.pkl',
        help='Path to the saved knowledge graph (default: ./graph_data/graph.pkl)'
    )
    query_parser.add_argument(
        '--format',
        type=str,
        choices=['pickle', 'json'],
        default='pickle',
        help='Format of the saved graph (default: pickle)'
    )
    
    # Export command - export the graph in different formats
    export_parser = subparsers.add_parser(
        'export',
        help='Export the knowledge graph in different formats'
    )
    export_parser.add_argument(
        'input_path',
        type=str,
        help='Path to the input knowledge graph'
    )
    export_parser.add_argument(
        'output_path',
        type=str,
        help='Path for the exported graph'
    )
    export_parser.add_argument(
        '--format',
        type=str,
        choices=['pickle', 'json'],
        default='json',
        help='Export format (default: json)'
    )
    
    # Incremental update command - update the graph incrementally
    update_parser = subparsers.add_parser(
        'update',
        help='Incrementally update the knowledge graph'
    )
    update_parser.add_argument(
        'project_path',
        type=str,
        help='Path to the project to update'
    )
    update_parser.add_argument(
        '--graph-path',
        type=str,
        default='./graph_data/graph.pkl',
        help='Path to the existing knowledge graph (default: ./graph_data/graph.pkl)'
    )
    update_parser.add_argument(
        '--exclude',
        type=str,
        nargs='*',
        default=['.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build'],
        help='Patterns to exclude from analysis (default: .git __pycache__ node_modules .venv venv dist build)'
    )
    
    return parser.parse_args()