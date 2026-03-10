"""
Main entry point for the code graph application.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from cli.args import parse_args
from core.graph.knowledge_graph import KnowledgeGraph
from core.parser.factory import ParserFactory
from core.incremental.updater import IncrementalUpdater
from storage.graph_store import GraphStore
from utils.file_utils import walk_project
from utils.logger import get_logger
from llm.client import OpenAIClient
from config.settings import settings


def build_graph(args):
    """
    Build the knowledge graph from a project.
    
    Args:
        args: Parsed command line arguments
    """
    logger = get_logger(__name__)
    logger.info(f"Building knowledge graph for project: {args.project_path}")
    
    # Create the knowledge graph
    graph = KnowledgeGraph()
    
    # Create the incremental updater
    updater = IncrementalUpdater(graph)
    
    # Process all files in the project
    file_count = 0
    for file_path in walk_project(args.project_path, args.exclude):
        try:
            # Determine the file extension
            ext = '.' + str(file_path).split('.')[-1]
            
            # Get the appropriate parser
            parser = ParserFactory.create_parser(ext)
            
            # Parse the file and add results to the graph
            nodes, relations = parser.parse_file(str(file_path))
            
            for node in nodes:
                graph.add_node(node)
            
            for relation in relations:
                graph.add_relation(relation)
            
            file_count += 1
            if file_count % 100 == 0:
                logger.info(f"Processed {file_count} files...")
                
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {str(e)}")
    
    logger.info(f"Processed {file_count} files. Final graph has {len(graph.nodes)} nodes and {len(graph.relations)} relations.")
    
    # Create the storage directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the graph
    store = GraphStore(str(output_path.parent))
    store.save(graph, output_path.name, "pickle")
    
    logger.info(f"Graph saved to {args.output}")


def query_graph(args):
    """
    Query the knowledge graph.
    
    Args:
        args: Parsed command line arguments
    """
    logger = get_logger(__name__)
    logger.info(f"Querying graph with question: {args.question}")
    
    # Load the graph
    graph_path = Path(args.graph_path)
    store = GraphStore(str(graph_path.parent))
    graph = store.load(graph_path.name, args.format)
    
    logger.info(f"Loaded graph with {len(graph.nodes)} nodes and {len(graph.relations)} relations.")
    
    # Create OpenAI client and generate response
    client = OpenAIClient()
    
    try:
        # For now, just print the question and some graph stats
        # In a real implementation, we would use the client to generate a response
        print(f"Question: {args.question}")
        print(f"Graph has {len(graph.nodes)} nodes and {len(graph.relations)} relations.")
        print(f"The graph contains:")
        print(f"- {len([n for n in graph.nodes.values() if n.type.value == 'FILE'])} files")
        print(f"- {len([n for n in graph.nodes.values() if n.type.value == 'CLASS'])} classes")
        print(f"- {len([n for n in graph.nodes.values() if n.type.value == 'FUNCTION'])} functions")
        
        # Generate a grep command suggestion
        grep_cmd = client.generate_grep_command(graph, args.question)
        print(f"\nSuggested grep command: {grep_cmd}")
        
    except Exception as e:
        logger.error(f"Error querying graph: {str(e)}")


def export_graph(args):
    """
    Export the knowledge graph in a different format.
    
    Args:
        args: Parsed command line arguments
    """
    logger = get_logger(__name__)
    logger.info(f"Exporting graph from {args.input_path} to {args.output_path} in {args.format} format")
    
    # Load the graph in its current format
    input_path = Path(args.input_path)
    input_store = GraphStore(str(input_path.parent))
    
    # Determine input format from file extension if not specified
    input_format = "pickle"  # default
    if input_path.suffix == ".json":
        input_format = "json"
    
    graph = input_store.load(input_path.name, input_format)
    
    # Save in the requested format
    output_path = Path(args.output_path)
    output_store = GraphStore(str(output_path.parent))
    
    output_store.save(graph, output_path.name, args.format)
    
    logger.info("Export completed successfully")


def update_graph(args):
    """
    Incrementally update the knowledge graph.
    
    Args:
        args: Parsed command line arguments
    """
    logger = get_logger(__name__)
    logger.info(f"Updating graph for project: {args.project_path}")
    
    # Load the existing graph if it exists
    graph_path = Path(args.graph_path)
    store = GraphStore(str(graph_path.parent))
    
    if store.exists(graph_path.name):
        graph = store.load(graph_path.name, "pickle")  # assume pickle for updates
        logger.info(f"Loaded existing graph with {len(graph.nodes)} nodes and {len(graph.relations)} relations.")
    else:
        graph = KnowledgeGraph()
        logger.info("Created new graph.")
    
    # Create the incremental updater
    updater = IncrementalUpdater(graph)
    
    # Update the graph
    updater.update_graph(args.project_path, args.exclude)
    
    # Save the updated graph
    store.save(graph, graph_path.name, "pickle")
    
    logger.info(f"Updated graph saved to {args.graph_path}. Now has {len(graph.nodes)} nodes and {len(graph.relations)} relations.")


def main():
    """
    Main function to parse arguments and dispatch to appropriate handler.
    """
    # Set up logging
    from utils.logger import setup_logger
    setup_logger()
    
    # Parse arguments
    args = parse_args()
    
    # Dispatch based on the command
    if args.command == 'build':
        build_graph(args)
    elif args.command == 'query':
        query_graph(args)
    elif args.command == 'export':
        export_graph(args)
    elif args.command == 'update':
        update_graph(args)
    else:
        print("Please specify a command: build, query, export, or update")
        sys.exit(1)


if __name__ == "__main__":
    main()