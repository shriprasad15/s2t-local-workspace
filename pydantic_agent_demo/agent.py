import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

# Load environment variables
load_dotenv()

# Configure OpenAI model with custom API key and base URL
api_key = os.getenv('OPENAI_API_KEY') or os.getenv('DOSASHOP_API_KEY')
base_url = os.getenv('OPENAI_BASE_URL') or os.getenv('DOSASHOP_URL')

# Create OpenAI model with custom configuration
model = OpenAIModel(
    'gpt-4o',
    api_key=api_key,
    base_url=base_url
)

# Create the agent with CSV analysis capabilities
agent = Agent(
    model=model,
    system_prompt="""
    You are a CSV data analysis expert specializing in data visualization and insights.
    
    Your capabilities include:
    - Analyzing CSV data structures and content
    - Understanding natural language queries about data
    - Recommending appropriate chart types (bar, line, scatter, histogram, pie)
    - Providing data insights and statistical summaries
    - Helping users understand their data patterns and trends
    
    When users ask about CSV data analysis:
    1. Help them understand their data structure
    2. Suggest appropriate visualizations based on their questions
    3. Provide insights about data patterns, correlations, and trends
    4. Explain statistical concepts in simple terms
    5. Guide them through data exploration techniques
    
    Be helpful, clear, and educational in your responses. Focus on making data analysis accessible to users of all skill levels.
    """
)

# Export the agent for use in other modules
__all__ = ['agent']

# Run the server (this won't be used since we're importing the agent)
if __name__ == "__main__":
    print("🚀 CSV Analysis Agent is ready to be imported and used")
    print("📊 This agent can be used with Pydantic AI for CSV data analysis")