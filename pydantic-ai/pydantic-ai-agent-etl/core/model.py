from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
import os
from dotenv import load_dotenv
 
# Load environment variables
load_dotenv()
 
def get_openai_client() -> AsyncOpenAI:
    """Configure and return OpenAI client."""
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL', 'https://api.dosashop1.com/openai/v1')
    
    return AsyncOpenAI(
        base_url=base_url,
        api_key=api_key,
        max_retries=3,
        default_headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "api-key": api_key
        }
    )
 
def get_openai_model(client: AsyncOpenAI) -> OpenAIModel:
    """Initialize and return OpenAI model with provider."""
    provider = OpenAIProvider(openai_client=client)
    model_name = os.getenv('OPENAI_MODEL', 'gpt-4o')
    return OpenAIModel(model_name, provider=provider)

def get_configured_model() -> OpenAIModel:
    """Get a fully configured OpenAI model ready for use."""
    client = get_openai_client()
    return get_openai_model(client)