import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

# Load environment variables
load_dotenv()

# Configure OpenAI model with custom API key and base URL (dosashop)
api_key = os.getenv('OPENAI_API_KEY') or os.getenv('DOSASHOP_API_KEY')
base_url = os.getenv('OPENAI_BASE_URL') or os.getenv('DOSASHOP_URL')

# Create OpenAI model with custom configuration
model = OpenAIModel(
    'gpt-4o',
    api_key=api_key,
    base_url=base_url
)

# Create a simple agent
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
    
    Be helpful, clear, and educational in your responses. Focus on making data analysis accessible to users of all skill levels.
    """
)

# Use the automatic ag_ui generation
app = agent.to_ag_ui()

# If you want the server to run on invocation, you can do the following:
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple AG UI Demo with dosashop API...")
    print("📊 Agent UI available at: http://localhost:8001")
    uvicorn.run(app, host="localhost", port=8001)