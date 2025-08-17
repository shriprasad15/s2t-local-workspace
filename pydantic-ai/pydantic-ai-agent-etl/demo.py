"""
Demo script for the ETL Pydantic AI Agent

This script demonstrates how to use natural language to interact with the ETL API service.
"""

import os
import asyncio
import uuid
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

from core.etl_agent import etl_agent, ETLAgentDeps
from core.api_client import APIClient

# Load environment variables
load_dotenv()

console = Console()


def print_welcome():
    """Print welcome message and instructions."""
    welcome_text = """
# ETL API Assistant Demo

Welcome! I'm your ETL API assistant. I can help you interact with the ETL service using natural language.

## What I can do:
- **Health checks**: Check if the service is running
- **User management**: Create, update, list, and delete users
- **Data source management**: List, view, update, and delete data sources
- **Data sharing**: Share data sources between users
- **Data processing**: Process files from URLs, S3, SQL databases, and MongoDB
- **Data querying**: Query data sources using natural language

## Example commands you can try:
- "Check if the service is healthy"
- "Create a user named john with email john@example.com"
- "List all users"
- "Show me all data sources"
- "Query the sales data for revenue by region"
- "Process a CSV file from this URL: https://example.com/data.csv"

Just type your request in natural language!
    """
    
    console.print(Panel(Markdown(welcome_text), title="🚀 ETL API Assistant", border_style="blue"))


def run_example_scenarios(agent_deps):
    """Run some example scenarios to demonstrate capabilities."""
    console.print("\n[bold blue]🎯 Running Example Scenarios[/bold blue]\n")
    
    scenarios = [
        {
            "description": "Check service health",
            "prompt": "Check if the ETL service is healthy and running"
        },
        {
            "description": "List users",
            "prompt": "Show me all users in the system"
        },
        {
            "description": "List data sources",
            "prompt": "List all available data sources"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        console.print(f"[bold yellow]Scenario {i}:[/bold yellow] {scenario['description']}")
        console.print(f"[dim]User input:[/dim] {scenario['prompt']}")
        
        try:
            # Run the agent synchronously for demo
            result = etl_agent.run_sync(scenario['prompt'], deps=agent_deps)
            console.print(f"[green]Response:[/green] {result.data}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
        
        console.print("")


async def interactive_chat(agent_deps):
    """Run interactive chat session with the agent."""
    console.print("\n[bold green]🎪 Interactive Mode[/bold green]")
    console.print("[dim]Type 'quit', 'exit', or 'bye' to end the session[/dim]\n")
    
    while True:
        try:
            user_input = Prompt.ask("[bold blue]You[/bold blue]")
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                console.print("[yellow]Goodbye! 👋[/yellow]")
                break
            
            if not user_input.strip():
                continue
            
            console.print("[dim]Processing...[/dim]")
            
            # Run the agent
            result = await etl_agent.run(user_input, deps=agent_deps)
            
            console.print(f"[bold green]Assistant:[/bold green] {result.data}")
            console.print("")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Session interrupted. Goodbye! 👋[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
            console.print("")


def main():
    """Main demo function."""
    console.print("[bold cyan]🔧 ETL API Assistant Demo[/bold cyan]\n")
    
    # Configuration
    api_url = os.getenv('ETL_API_URL', 'http://localhost:8000')
    user_id = os.getenv('ETL_USER_ID', 'demo-user')
    
    console.print(f"[dim]API URL: {api_url}[/dim]")
    console.print(f"[dim]User ID: {user_id}[/dim]\n")
    
    # Initialize API client and agent dependencies
    try:
        api_client = APIClient(base_url=api_url, user_id=user_id)
        agent_deps = ETLAgentDeps(api_client=api_client)
        
        print_welcome()
        
        # Ask user what they want to do
        choice = Prompt.ask(
            "What would you like to do?",
            choices=["examples", "interactive", "both"],
            default="both"
        )
        
        if choice in ["examples", "both"]:
            run_example_scenarios(agent_deps)
        
        if choice in ["interactive", "both"]:
            asyncio.run(interactive_chat(agent_deps))
            
    except Exception as e:
        console.print(f"[red]Failed to initialize:[/red] {str(e)}")
        console.print("\n[yellow]Make sure the ETL API service is running and accessible.[/yellow]")
    
    finally:
        # Cleanup
        if 'api_client' in locals():
            api_client.close()


if __name__ == "__main__":
    main()