"""
Demo test scenarios for the ETL Agent

This script demonstrates various agent capabilities with predefined test scenarios.
"""

import asyncio
import uuid
from rich.console import Console
from rich.panel import Panel

from core.etl_agent import etl_agent, ETLAgentDeps
from core.api_client import APIClient

console = Console()


async def test_user_management():
    """Test user management functionality."""
    console.print(Panel("Testing User Management", style="blue"))
    
    api_client = APIClient(base_url='http://localhost:8000', user_id='test-user')
    agent_deps = ETLAgentDeps(api_client=api_client)
    
    scenarios = [
        "Create a user named alice with email alice@example.com",
        "Create a user named bob with email bob@example.com", 
        "List all users in the system",
        "Get details for user alice",
        "Update alice's email to alice.smith@example.com",
        "Show alice's data sources"
    ]
    
    for prompt in scenarios:
        console.print(f"\n[bold blue]> {prompt}[/bold blue]")
        try:
            result = await etl_agent.run(prompt, deps=agent_deps)
            console.print(f"[green]Response:[/green] {result.data}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
    
    api_client.close()


async def test_data_operations():
    """Test data processing and querying."""
    console.print(Panel("Testing Data Operations", style="green"))
    
    api_client = APIClient(base_url='http://localhost:8000', user_id='test-user')
    agent_deps = ETLAgentDeps(api_client=api_client)
    
    scenarios = [
        "Check if the ETL service is healthy",
        "List all available data sources",
        "Show me data sources that are active",
        "Get details for the first data source if any exist"
    ]
    
    for prompt in scenarios:
        console.print(f"\n[bold blue]> {prompt}[/bold blue]")
        try:
            result = await etl_agent.run(prompt, deps=agent_deps)
            console.print(f"[green]Response:[/green] {result.data}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
    
    api_client.close()


async def test_file_processing():
    """Test file processing capabilities."""
    console.print(Panel("Testing File Processing", style="yellow"))
    
    api_client = APIClient(base_url='http://localhost:8000', user_id='test-user')
    agent_deps = ETLAgentDeps(api_client=api_client)
    
    # Generate a unique tracking ID for testing
    tracking_id = str(uuid.uuid4())
    
    scenarios = [
        f"Process a CSV file from URL https://example.com/data.csv with tracking ID {tracking_id}",
        "Show me how to process a file from S3 with AWS credentials",
        "Explain how to connect to a PostgreSQL database for data extraction"
    ]
    
    for prompt in scenarios:
        console.print(f"\n[bold blue]> {prompt}[/bold blue]")
        try:
            result = await etl_agent.run(prompt, deps=agent_deps)
            console.print(f"[green]Response:[/green] {result.data}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
    
    api_client.close()


async def test_comprehensive_workflow():
    """Test a comprehensive workflow combining multiple operations."""
    console.print(Panel("Testing Comprehensive Workflow", style="magenta"))
    
    api_client = APIClient(base_url='http://localhost:8000', user_id='workflow-test-user')
    agent_deps = ETLAgentDeps(api_client=api_client)
    
    workflow_steps = [
        "Check if the service is healthy",
        "Create a user named workflow_user with email workflow@example.com",
        "List all users to confirm the user was created",
        "Show all data sources available to the user",
        "Explain the process of uploading and processing a CSV file",
        "Show how to query data using natural language"
    ]
    
    for step, prompt in enumerate(workflow_steps, 1):
        console.print(f"\n[bold cyan]Step {step}:[/bold cyan] [bold blue]{prompt}[/bold blue]")
        try:
            result = await etl_agent.run(prompt, deps=agent_deps)
            console.print(f"[green]Response:[/green] {result.data}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
        
        # Small delay between steps for readability
        await asyncio.sleep(0.5)
    
    api_client.close()


async def main():
    """Run all test scenarios."""
    console.print("[bold cyan]🧪 ETL Agent Test Scenarios[/bold cyan]\n")
    
    try:
        await test_user_management()
        console.print("\n" + "="*60 + "\n")
        
        await test_data_operations()
        console.print("\n" + "="*60 + "\n")
        
        await test_file_processing()
        console.print("\n" + "="*60 + "\n")
        
        await test_comprehensive_workflow()
        
        console.print(Panel("✅ All test scenarios completed!", style="green"))
        
    except Exception as e:
        console.print(f"[red]Test execution failed:[/red] {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())