"""
FastAPI Web Service for ETL Pydantic AI Agent

This service exposes the ETL agent functionality through REST API endpoints,
allowing natural language queries to interact with the ETL service using OpenAI.
"""

import os
import uuid
import json
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import asyncio
import logging
from openai import AsyncOpenAI

from core.api_client import APIClient

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Global variables for dependencies
api_client = None
openai_client = None


class QueryRequest(BaseModel):
    """Request model for natural language queries."""
    query: str = Field(..., description="Natural language query for the ETL agent")
    user_id: Optional[str] = Field(None, description="Optional user ID for the request")


class QueryResponse(BaseModel):
    """Response model for query results."""
    success: bool = Field(..., description="Whether the query was successful")
    output: str = Field(..., description="The agent's response to the query")
    error: Optional[str] = Field(None, description="Error message if query failed")
    request_id: str = Field(..., description="Unique identifier for this request")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Health check message")
    version: str = Field(..., description="Service version")
    etl_service_healthy: bool = Field(..., description="Whether the ETL service is accessible")


async def initialize_etl_agent():
    """Initialize the ETL agent and dependencies."""
    global api_client, openai_client
    
    if not api_client or not openai_client:
        try:
            # Configuration
            api_url = os.getenv('ETL_API_URL', 'http://localhost:8000')
            user_id = os.getenv('ETL_USER_ID', 'system')
            openai_api_key = os.getenv('OPENAI_API_KEY')
            openai_base_url = os.getenv('OPENAI_BASE_URL', 'https://api.dosashop1.com/openai/v1')
            
            logger.info(f"Initializing API client with URL: {api_url}")
            logger.info(f"Using user ID: {user_id}")
            
            # Initialize API client and OpenAI client
            api_client = APIClient(base_url=api_url, user_id=user_id)
            openai_client = AsyncOpenAI(
                api_key=openai_api_key,
                base_url=openai_base_url,
                max_retries=3,
                default_headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openai_api_key}",
                    "api-key": openai_api_key
                }
            )
            
            # Test connection to ETL service
            try:
                result = api_client.get("/api/v1/ping")
                logger.info(f"ETL service connection successful: {result}")
            except Exception as e:
                logger.warning(f"ETL service connection test failed: {str(e)}")
                
            logger.info("ETL agent initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ETL agent: {str(e)}")
            raise e


async def process_with_ai(query: str, user_id: Optional[str] = None) -> str:
    """Process queries using OpenAI to understand intent and execute ETL operations."""
    
    # Define available tools/functions for the AI
    tools = [
        {
            "type": "function",
            "function": {
                "name": "ping_service",
                "description": "Check if the ETL service is healthy and responsive",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "create_user",
                "description": "Create a new user in the system",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "Unique username"},
                        "email": {"type": "string", "description": "Email address"}
                    },
                    "required": ["username"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_users", 
                "description": "List all users in the system",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_user",
                "description": "Get details of a specific user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "Username to get details for"}
                    },
                    "required": ["username"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_data_sources",
                "description": "List all data sources with optional filtering",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "source_type": {"type": "string", "description": "Filter by source type"},
                        "status": {"type": "string", "description": "Filter by status"}
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_data_source",
                "description": "Get details about a specific data source",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data_source_id": {"type": "string", "description": "ID of the data source"}
                    },
                    "required": ["data_source_id"]
                }
            }
        }
    ]
    
    try:
        # Call OpenAI with function calling
        response = await openai_client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o'),
            messages=[
                {
                    "role": "system", 
                    "content": """You are an ETL (Extract, Transform, Load) API assistant. 
                    You help users interact with an ETL service that can process various data sources including files, databases, and cloud storage.
                    
                    You have access to tools that can:
                    - Check service health
                    - Manage users and data source sharing  
                    - Query data sources using natural language
                    - Process files from URLs, S3, SQL databases, and MongoDB
                    - Manage data source metadata
                    
                    Always provide helpful explanations of what each operation does and what the results mean.
                    When errors occur, explain them in user-friendly terms and suggest solutions.
                    """
                },
                {"role": "user", "content": query}
            ],
            tools=tools,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        # Check if the AI wants to call a tool
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Execute the requested function
            result = await execute_tool(function_name, function_args, user_id)
            
            # Get final response from AI with tool result
            final_response = await openai_client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4o'),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an ETL API assistant. Provide a helpful response based on the tool result."
                    },
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": message.content, "tool_calls": message.tool_calls},
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    }
                ]
            )
            
            return final_response.choices[0].message.content
        else:
            # Direct response from AI
            return message.content
            
    except Exception as e:
        logger.error(f"AI processing failed: {str(e)}")
        return f"I encountered an error processing your request: {str(e)}"


async def execute_tool(function_name: str, function_args: Dict[str, Any], user_id: Optional[str] = None) -> str:
    """Execute the requested tool/function."""
    try:
        if function_name == "ping_service":
            result = api_client.get("/api/v1/ping")
            return f"Service is healthy! Version: {result.get('version', 'Unknown')}, Message: {result.get('message', 'No message')}"
        
        elif function_name == "create_user":
            result = api_client.post("/api/v1/users/", {
                "username": function_args.get("username"),
                "email": function_args.get("email")
            })
            return f"User created successfully! ID: {result.get('id')}, Username: {result.get('username')}, Email: {result.get('email')}"
        
        elif function_name == "list_users":
            result = api_client.get("/api/v1/users/")
            if not result:
                return "No users found in the system."
            
            user_list = []
            for user in result:
                data_sources_count = len(user.get('data_sources', []))
                user_list.append(f"- {user.get('username')} ({user.get('email', 'no email')}) - {data_sources_count} data sources")
            
            return f"Found {len(result)} users:\n" + "\n".join(user_list)
        
        elif function_name == "get_user":
            result = api_client.get(f"/api/v1/users/{function_args.get('username')}")
            data_sources_count = len(result.get('data_sources', []))
            return f"User found - Username: {result.get('username')}, Email: {result.get('email', 'None')}, Active: {result.get('is_active')}, Data Sources: {data_sources_count}"
        
        elif function_name == "list_data_sources":
            query_params = {}
            if function_args.get('source_type'):
                query_params['source_type'] = function_args['source_type']
            if function_args.get('status'):
                query_params['status'] = function_args['status']
                
            result = api_client.get("/api/v1/query/data-sources", query_params)
            data_sources = result.get('data_sources', [])
            
            if not data_sources:
                return "No data sources found matching the criteria."
            
            source_list = []
            for ds in data_sources:
                tags_info = f"tags: {', '.join(ds.get('tags', []))}" if ds.get('tags') else "no tags"
                source_list.append(f"- {ds.get('name')} ({ds.get('source_type')}) - Status: {ds.get('status')}, {tags_info}")
            
            total = result.get('total', len(data_sources))
            return f"Found {len(data_sources)} data sources (total: {total}):\n" + "\n".join(source_list)
        
        elif function_name == "get_data_source":
            result = api_client.get(f"/api/v1/query/data-sources/{function_args.get('data_source_id')}")
            ds = result.get('data_source', {})
            
            tags_info = f"Tags: {', '.join(ds.get('tags', []))}" if ds.get('tags') else "No tags"
            return f"""Data Source Details:
- Name: {ds.get('name')}
- Type: {ds.get('source_type')}
- Status: {ds.get('status')}
- Created by: {ds.get('created_by')}
- Created: {ds.get('created_at')}
- Description: {ds.get('description', 'No description')}
- {tags_info}"""
        
        else:
            return f"Unknown function: {function_name}"
            
    except Exception as e:
        if "404" in str(e):
            return f"Resource not found."
        elif "403" in str(e):
            return f"Access denied."
        return f"Operation failed: {str(e)}"


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Initialize if needed
        await initialize_etl_agent()
        
        # Check if our service is ready
        if not api_client or not openai_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not fully initialized"
            )
        
        # Test ETL service connectivity
        etl_healthy = False
        try:
            result = api_client.get("/api/v1/ping")
            etl_healthy = True
        except Exception as e:
            logger.warning(f"ETL service health check failed: {str(e)}")
        
        return HealthResponse(
            status="healthy",
            message="ETL AI Agent API is running",
            version="1.0.0",
            etl_service_healthy=etl_healthy
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@router.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Process a natural language query using the ETL agent with OpenAI.
    
    This endpoint accepts natural language queries and processes them using
    OpenAI with function calling to execute appropriate ETL operations.
    """
    request_id = str(uuid.uuid4())
    
    try:
        # Initialize if needed
        await initialize_etl_agent()
        
        # Validate that the service is ready
        if not api_client or not openai_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not fully initialized"
            )
        
        # Log the incoming request
        logger.info(f"Processing query request {request_id}: {request.query}")
        
        # Use the provided user_id or default from environment
        if request.user_id:
            # Create a temporary API client with the specific user_id
            temp_api_client = APIClient(
                base_url=api_client.base_url, 
                user_id=request.user_id
            )
            # Temporarily replace global client
            original_client = api_client
            globals()['api_client'] = temp_api_client
            result = await process_with_ai(request.query, request.user_id)
            globals()['api_client'] = original_client
            temp_api_client.close()
        else:
            result = await process_with_ai(request.query)
        
        logger.info(f"Query {request_id} processed successfully")
        
        return QueryResponse(
            success=True,
            output=result,
            request_id=request_id
        )
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Query {request_id} failed: {error_msg}")
        
        # Return error response instead of raising HTTPException
        return QueryResponse(
            success=False,
            output="I encountered an error processing your request. Please check if the ETL service is accessible and try again.",
            error=error_msg,
            request_id=request_id
        )


@router.get("/capabilities")
async def get_capabilities():
    """
    Get information about the agent's capabilities.
    
    Returns a list of available operations and example queries.
    """
    capabilities = {
        "description": "ETL AI Agent capabilities",
        "categories": {
            "health_checks": {
                "description": "Check service health and connectivity",
                "examples": [
                    "Check if the service is healthy",
                    "Test the ETL service connection"
                ]
            },
            "user_management": {
                "description": "Create, update, list, and delete users",
                "examples": [
                    "Create a user named john with email john@example.com",
                    "List all users",
                    "Update user john's email to newemail@example.com",
                    "Delete user john"
                ]
            },
            "data_source_management": {
                "description": "List, view, update, and delete data sources",
                "examples": [
                    "Show me all data sources",
                    "Get details for data source abc-123",
                    "List data sources with status active",
                    "Update data source abc-123 name to 'Sales Data'"
                ]
            },
            "data_sharing": {
                "description": "Share data sources between users",
                "examples": [
                    "Share data source abc-123 from user john to user jane",
                    "Show all data sources accessible by user john"
                ]
            },
            "data_processing": {
                "description": "Process files from URLs, S3, SQL databases, and MongoDB",
                "examples": [
                    "Process a CSV file from this URL: https://example.com/data.csv",
                    "Process data from S3 bucket my-bucket path data/file.json",
                    "Extract schema from PostgreSQL database on host db.example.com"
                ]
            },
            "data_querying": {
                "description": "Query data sources using natural language",
                "examples": [
                    "Query the sales data for revenue by region",
                    "Show me the top 10 customers by purchase amount",
                    "Get monthly trends from the user activity data"
                ]
            }
        },
        "usage": {
            "endpoint": "/api/v1/ai/query",
            "method": "POST",
            "format": "Send natural language queries as JSON in the request body"
        }
    }
    
    return capabilities


@router.get("/")
async def root():
    """Root endpoint with basic service information."""
    return {
        "service": "ETL AI Agent API",
        "version": "1.0.0",
        "description": "Natural language interface for ETL operations",
        "endpoints": {
            "health": "/api/v1/ai/health",
            "query": "/api/v1/ai/query", 
            "capabilities": "/api/v1/ai/capabilities"
        },
        "usage": "Send POST requests to /api/v1/ai/query with natural language queries"
    }
