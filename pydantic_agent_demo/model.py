from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
import os
from dotenv import load_dotenv
 
# Load environment variables
load_dotenv()
 
def get_openai_client() -> AsyncOpenAI:
    """Configure and return OpenAI client."""
    return AsyncOpenAI(
        base_url='https://api.dosashop1.com/openai/v1',
        api_key=os.getenv('API_KEY'),
        max_retries=3,
        default_headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('API_KEY')}",
            "api-key": os.getenv('API_KEY')
        }
    )
 
def get_openai_model(client: AsyncOpenAI) -> OpenAIModel:
    """Initialize and return OpenAI model with provider."""
    provider = OpenAIProvider(openai_client=client)
    return OpenAIModel('gpt-4o', provider=provider)

def get_configured_model() -> OpenAIModel:
    """Get a fully configured OpenAI model ready for use."""
    client = get_openai_client()
    return get_openai_model(client)
