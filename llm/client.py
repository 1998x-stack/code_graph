"""
OpenAI client for generating grep commands based on the knowledge graph.
"""

import openai
from typing import Dict, Any
from ..config.settings import settings
from ..core.graph.knowledge_graph import KnowledgeGraph


class OpenAIClient:
    """
    Client for interacting with OpenAI API to generate grep commands based on the knowledge graph.
    """
    
    def __init__(self):
        """
        Initialize the OpenAI client with API key from settings.
        """
        openai.api_key = settings.OPENAI_API_KEY
    
    def generate_grep_command(self, graph: KnowledgeGraph, question: str) -> str:
        """
        Generate a grep command based on the knowledge graph and user question.
        
        Args:
            graph: KnowledgeGraph instance containing codebase information
            question: Natural language question about the codebase
            
        Returns:
            A grep command string that would help answer the question
        """
        # For now, we'll return a placeholder implementation
        # In a real implementation, we would use the graph and question
        # to generate a relevant grep command
        
        # Example of how we might use the graph:
        # 1. Analyze the question to determine what kind of search is needed
        # 2. Use the graph to identify relevant files/directories
        # 3. Construct an appropriate grep command
        
        # Placeholder implementation:
        prompt = f"""
        Given the following question about a codebase: "{question}"
        
        And the following information about the codebase structure:
        - Number of files: {len([n for n in graph.nodes.values() if n.type.value == 'FILE'])}
        - Number of classes: {len([n for n in graph.nodes.values() if n.type.value == 'CLASS'])}
        - Number of functions: {len([n for n in graph.nodes.values() if n.type.value == 'FUNCTION'])}
        
        Generate an appropriate grep command to find relevant code for this question.
        Return only the grep command without any explanation.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates grep commands to search codebases."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.1
            )
            
            command = response.choices[0].message.content.strip()
            # Basic validation to ensure we got a grep command
            if command.startswith("grep ") or "grep" in command:
                return command
            else:
                # If we didn't get a grep command, return a generic one
                return f"grep -r '{question}' . --include='*.py'"
                
        except Exception as e:
            # If there's an error, return a generic grep command
            return f"grep -r '{question}' . --include='*.py'"
    
    def generate_code_explanation(self, graph: KnowledgeGraph, code_elements: list) -> str:
        """
        Generate explanations for specific code elements based on the knowledge graph.
        
        Args:
            graph: KnowledgeGraph instance containing codebase information
            code_elements: List of code element IDs to explain
            
        Returns:
            Explanation of the code elements and their relationships
        """
        # Extract information about the requested elements from the graph
        element_details = []
        for elem_id in code_elements:
            node = graph.get_node(elem_id)
            if node:
                neighbors = graph.get_neighbors(elem_id)
                element_details.append({
                    'id': node.id,
                    'name': node.name,
                    'type': node.type.value,
                    'neighbors': [(n.name, n.type.value) for n in neighbors]
                })
        
        # Create a prompt for the LLM
        prompt = f"""
        Explain the following code elements and their relationships:

        {element_details}

        Describe their purpose, functionality, and how they interact with other components.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that explains code structure and relationships."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Could not generate explanation: {str(e)}"