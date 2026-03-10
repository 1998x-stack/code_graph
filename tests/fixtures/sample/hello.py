"""
Sample Python file for testing the code graph parser.
"""


def greet(name: str) -> str:
    """
    Greets a person with a friendly message.
    
    Args:
        name: The name of the person to greet
        
    Returns:
        A greeting message
    """
    return f"Hello, {name}!"


def farewell(name: str) -> str:
    """
    Says goodbye to a person.
    
    Args:
        name: The name of the person to say goodbye to
        
    Returns:
        A farewell message
    """
    return f"Goodbye, {name}."


class Greeter:
    """
    A class that handles greeting and farewell messages.
    """
    
    def __init__(self, default_name: str = "World"):
        """
        Initializes the Greeter with a default name.
        
        Args:
            default_name: The default name to use for greetings
        """
        self.default_name = default_name
    
    def greet(self, name: str = None) -> str:
        """
        Greets a person using the provided name or the default name.
        
        Args:
            name: The name to greet. If None, uses the default name.
            
        Returns:
            A greeting message
        """
        target_name = name or self.default_name
        return greet(target_name)  # Calling the standalone function
    
    def farewell(self, name: str = None) -> str:
        """
        Says goodbye to a person using the provided name or the default name.
        
        Args:
            name: The name to say goodbye to. If None, uses the default name.
            
        Returns:
            A farewell message
        """
        target_name = name or self.default_name
        return farewell(target_name)  # Calling the standalone function


def main():
    """
    Main function to demonstrate the usage of the Greeter class.
    """
    greeter = Greeter("Alice")
    
    greeting = greeter.greet()
    print(greeting)
    
    farewell_msg = greeter.farewell("Bob")
    print(farewell_msg)


if __name__ == "__main__":
    main()