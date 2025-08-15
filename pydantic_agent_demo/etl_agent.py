"""
Pydantic AI Agent for ETL API Service

This agent exposes the hosted ETL service's endpoints as tools for natural language interaction.
"""

import os
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.tools import Tool

from api_client import APIClient, DataSource, User, QueryResult
from model import get_configured_model


class ETLAgentDeps(BaseModel):
    """Dependencies for the ETL agent."""
    api_client: APIClient
    
    class Config:
        arbitrary_types_allowed = True


# Tool parameter models
class CreateUserParams(BaseModel):
    """Parameters for creating a user."""
    username: str = Field(description="Unique username for the user")
    email: Optional[str] = Field(None, description="Email address for the user")


class UpdateUserParams(BaseModel):
    """Parameters for updating a user."""
    username: str = Field(description="Username of the user to update")
    email: Optional[str] = Field(None, description="New email address")
    is_active: Optional[bool] = Field(None, description="Whether the user is active")


class ShareDataSourceParams(BaseModel):
    """Parameters for sharing a data source."""
    owner_username: str = Field(description="Username of the data source owner")
    data_source_id: str = Field(description="ID of the data source to share")
    target_username: str = Field(description="Username of the user to share with")


class QueryDataParams(BaseModel):
    """Parameters for querying data."""
    data_source_id: str = Field(description="ID of the data source to query")
    query: str = Field(description="Natural language query to process")
    generate_chart: Optional[bool] = Field(True, description="Whether to generate chart configuration")
    theme: Optional[str] = Field("auto", description="Chart theme: 'light', 'dark', or 'auto'")


class ProcessFromUrlParams(BaseModel):
    """Parameters for processing files from URL."""
    presigned_url: str = Field(description="The presigned URL to download the file from")
    file_type: str = Field(description="The type of file being processed (csv, json, log, parquet)")
    tracking_id: str = Field(description="Unique ID for tracking the processing")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the file")


class ProcessFromS3Params(BaseModel):
    """Parameters for processing files from S3."""
    aws_access_key: str = Field(description="AWS access key for S3 authentication")
    aws_secret_key: str = Field(description="AWS secret key for S3 authentication")
    aws_region: Optional[str] = Field("us-east-1", description="AWS region")
    s3_bucket: str = Field(description="S3 bucket name")
    s3_path: str = Field(description="S3 path/prefix to the file(s)")
    file_type: str = Field(description="The type of file being processed (csv, json, log, parquet)")
    tracking_id: str = Field(description="Unique ID for tracking the processing")
    partition_format: Optional[str] = Field(None, description="Format for partitioned data")
    start_date: Optional[str] = Field(None, description="Start date for partitioned data (ISO format)")
    end_date: Optional[str] = Field(None, description="End date for partitioned data (ISO format)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the file")


class ProcessFromSQLParams(BaseModel):
    """Parameters for processing from SQL database."""
    db_type: str = Field(description="Database type (postgres, mysql, sqlserver)")
    host: str = Field(description="Database host address")
    port: int = Field(description="Database port")
    username: str = Field(description="Database username")
    password: str = Field(description="Database password")
    database: str = Field(description="Database name")
    table: str = Field(description="Table name to extract data from")
    schema: Optional[str] = Field(None, description="Schema name (if applicable)")
    query: Optional[str] = Field(None, description="Custom SQL query (if not extracting entire table)")
    tracking_id: str = Field(description="Unique ID for tracking the processing")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ProcessFromMongoParams(BaseModel):
    """Parameters for processing from MongoDB."""
    connection_string: str = Field(description="MongoDB connection string")
    db_name: str = Field(description="Database name")
    collection_name: str = Field(description="Collection name to extract schema from")
    tracking_id: str = Field(description="Unique ID for tracking the processing")
    username: Optional[str] = Field(None, description="Username for authentication")
    password: Optional[str] = Field(None, description="Password for authentication")
    use_ssl: Optional[bool] = Field(False, description="Whether to use SSL for connection")
    connection_options: Optional[Dict[str, Any]] = Field(None, description="Additional connection options")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class UpdateDataSourceParams(BaseModel):
    """Parameters for updating a data source."""
    data_source_id: str = Field(description="ID of the data source to update")
    name: Optional[str] = Field(None, description="New name for the data source")
    description: Optional[str] = Field(None, description="New description for the data source")
    status: Optional[str] = Field(None, description="New status (active, inactive, error, pending)")
    tags: Optional[List[str]] = Field(None, description="New tags for the data source")


class ListDataSourcesParams(BaseModel):
    """Parameters for listing data sources."""
    source_type: Optional[str] = Field(None, description="Filter by source type")
    status: Optional[str] = Field(None, description="Filter by status")
    tags: Optional[str] = Field(None, description="Filter by tags (comma-separated)")
    limit: Optional[int] = Field(100, description="Maximum number of results")
    skip: Optional[int] = Field(0, description="Number of results to skip")


# Create the agent
etl_agent = Agent(
    get_configured_model(),
    deps_type=ETLAgentDeps,
    system_prompt="""You are an ETL (Extract, Transform, Load) API assistant.
    You help users interact with an ETL service that can process various data sources including files, databases, and cloud storage.
    
    You have access to tools that can:
    - Check service health
    - Manage users and data source sharing
    - Query data sources using natural language
    - Process files from URLs, S3, SQL databases, and MongoDB
    - Manage data source metadata
    
    Always provide helpful explanations of what each operation does and what the results mean.
    When errors occur, explain them in user-friendly terms and suggest solutions.
    """,
)


@etl_agent.tool
def ping_service(ctx: RunContext[ETLAgentDeps]) -> str:
    """Check if the ETL service is healthy and responsive."""
    try:
        result = ctx.deps.api_client.get("/api/v1/ping")
        return f"Service is healthy! Version: {result.get('version', 'Unknown')}, Message: {result.get('message', 'No message')}"
    except Exception as e:
        return f"Service health check failed: {str(e)}"


@etl_agent.tool
def test_error_handling(ctx: RunContext[ETLAgentDeps]) -> str:
    """Test the service's error handling capabilities."""
    try:
        ctx.deps.api_client.get("/api/v1/error")
        return "Unexpected: Error endpoint didn't raise an error"
    except Exception as e:
        return f"Error handling test completed. Expected error occurred: {str(e)}"


@etl_agent.tool
def create_user(ctx: RunContext[ETLAgentDeps], params: CreateUserParams) -> str:
    """Create a new user in the system."""
    try:
        result = ctx.deps.api_client.post("/api/v1/users/", {
            "username": params.username,
            "email": params.email
        })
        return f"User created successfully! ID: {result.get('id')}, Username: {result.get('username')}, Email: {result.get('email')}"
    except Exception as e:
        if "already exists" in str(e):
            return f"User '{params.username}' already exists. Please choose a different username."
        return f"Failed to create user: {str(e)}"


@etl_agent.tool
def get_user(ctx: RunContext[ETLAgentDeps], username: str) -> str:
    """Get a user by username."""
    try:
        result = ctx.deps.api_client.get(f"/api/v1/users/{username}")
        data_sources_count = len(result.get('data_sources', []))
        return f"User found - Username: {result.get('username')}, Email: {result.get('email', 'None')}, Active: {result.get('is_active')}, Data Sources: {data_sources_count}"
    except Exception as e:
        if "404" in str(e):
            return f"User '{username}' not found."
        return f"Failed to get user: {str(e)}"


@etl_agent.tool
def list_users(ctx: RunContext[ETLAgentDeps]) -> str:
    """List all users in the system."""
    try:
        result = ctx.deps.api_client.get("/api/v1/users/")
        if not result:
            return "No users found in the system."
        
        user_list = []
        for user in result:
            data_sources_count = len(user.get('data_sources', []))
            user_list.append(f"- {user.get('username')} ({user.get('email', 'no email')}) - {data_sources_count} data sources")
        
        return f"Found {len(result)} users:\n" + "\n".join(user_list)
    except Exception as e:
        return f"Failed to list users: {str(e)}"


@etl_agent.tool
def update_user(ctx: RunContext[ETLAgentDeps], params: UpdateUserParams) -> str:
    """Update a user's information."""
    try:
        update_data = {}
        if params.email is not None:
            update_data['email'] = params.email
        if params.is_active is not None:
            update_data['is_active'] = params.is_active
            
        result = ctx.deps.api_client.put(f"/api/v1/users/{params.username}", update_data)
        return f"User updated successfully! Username: {result.get('username')}, Email: {result.get('email')}, Active: {result.get('is_active')}"
    except Exception as e:
        if "404" in str(e):
            return f"User '{params.username}' not found."
        return f"Failed to update user: {str(e)}"


@etl_agent.tool
def delete_user(ctx: RunContext[ETLAgentDeps], username: str) -> str:
    """Delete a user from the system."""
    try:
        result = ctx.deps.api_client.delete(f"/api/v1/users/{username}")
        return f"User deleted successfully: {result.get('message', 'User deleted')}"
    except Exception as e:
        if "404" in str(e):
            return f"User '{username}' not found."
        return f"Failed to delete user: {str(e)}"


@etl_agent.tool
def share_data_source(ctx: RunContext[ETLAgentDeps], params: ShareDataSourceParams) -> str:
    """Share a data source with another user."""
    try:
        result = ctx.deps.api_client.post(f"/api/v1/users/{params.owner_username}/share/{params.data_source_id}/{params.target_username}")
        return f"Data source shared successfully: {result.get('message')}"
    except Exception as e:
        if "403" in str(e):
            return f"Permission denied. User '{params.owner_username}' is not the owner of this data source."
        elif "404" in str(e):
            return f"Data source or user not found."
        return f"Failed to share data source: {str(e)}"


@etl_agent.tool
def get_user_data_sources(ctx: RunContext[ETLAgentDeps], username: str) -> str:
    """Get all data sources accessible by a user."""
    try:
        result = ctx.deps.api_client.get(f"/api/v1/users/{username}/data_sources")
        data_sources = result.get('data_sources', [])
        
        if not data_sources:
            return f"User '{username}' has no accessible data sources."
        
        source_list = []
        for ds in data_sources:
            shared_info = f"shared with {len(ds.get('shared_with', []))} users" if ds.get('shared_with') else "not shared"
            source_list.append(f"- {ds.get('name')} ({ds.get('source_type')}) - Status: {ds.get('status')}, {shared_info}")
        
        return f"User '{username}' has access to {len(data_sources)} data sources:\n" + "\n".join(source_list)
    except Exception as e:
        return f"Failed to get user data sources: {str(e)}"


@etl_agent.tool
def list_data_sources(ctx: RunContext[ETLAgentDeps], params: ListDataSourcesParams) -> str:
    """List all data sources with optional filtering."""
    try:
        query_params = {}
        if params.source_type:
            query_params['source_type'] = params.source_type
        if params.status:
            query_params['status'] = params.status
        if params.tags:
            query_params['tags'] = params.tags
        if params.limit != 100:
            query_params['limit'] = params.limit
        if params.skip != 0:
            query_params['skip'] = params.skip
            
        result = ctx.deps.api_client.get("/api/v1/query/data-sources", query_params)
        data_sources = result.get('data_sources', [])
        
        if not data_sources:
            return "No data sources found matching the criteria."
        
        source_list = []
        for ds in data_sources:
            tags_info = f"tags: {', '.join(ds.get('tags', []))}" if ds.get('tags') else "no tags"
            source_list.append(f"- {ds.get('name')} ({ds.get('source_type')}) - Status: {ds.get('status')}, {tags_info}")
        
        total = result.get('total', len(data_sources))
        return f"Found {len(data_sources)} data sources (total: {total}):\n" + "\n".join(source_list)
    except Exception as e:
        return f"Failed to list data sources: {str(e)}"


@etl_agent.tool
def get_data_source(ctx: RunContext[ETLAgentDeps], data_source_id: str) -> str:
    """Get details about a specific data source."""
    try:
        result = ctx.deps.api_client.get(f"/api/v1/query/data-sources/{data_source_id}")
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
    except Exception as e:
        if "404" in str(e):
            return f"Data source '{data_source_id}' not found."
        elif "403" in str(e):
            return f"Access denied to data source '{data_source_id}'."
        return f"Failed to get data source: {str(e)}"


@etl_agent.tool
def query_data(ctx: RunContext[ETLAgentDeps], params: QueryDataParams) -> str:
    """Query data using natural language for a specific data source."""
    try:
        query_params = {
            'query': params.query,
            'generate_chart': params.generate_chart,
            'theme': params.theme
        }
        
        result = ctx.deps.api_client.get(f"/api/v1/query/{params.data_source_id}", query_params)
        
        response_parts = [
            f"Query executed successfully!",
            f"Natural Language Query: {result.get('natural_language_query')}",
            f"Query Type: {result.get('query_type', 'Unknown')}",
        ]
        
        if result.get('documents'):
            doc_count = len(result['documents'])
            response_parts.append(f"Retrieved {doc_count} documents")
            
        if result.get('chart_config'):
            response_parts.append("Chart configuration generated for visualization")
            
        return "\n".join(response_parts)
    except Exception as e:
        if "404" in str(e):
            return f"Data source '{params.data_source_id}' not found."
        elif "403" in str(e):
            return f"Access denied to data source '{params.data_source_id}'."
        return f"Failed to query data: {str(e)}"


@etl_agent.tool
def process_file_from_url(ctx: RunContext[ETLAgentDeps], params: ProcessFromUrlParams) -> str:
    """Process a file from a presigned S3 URL."""
    try:
        result = ctx.deps.api_client.post("/api/v1/extraction/process-from-url", {
            "presigned_url": params.presigned_url,
            "file_type": params.file_type,
            "tracking_id": params.tracking_id,
            "metadata": params.metadata or {}
        })
        
        processing_result = result.get('processing_result', {})
        return f"""File processed successfully!
- File: {result.get('file_name')}
- Type: {result.get('file_type')}
- Data Source ID: {result.get('data_source_id')}
- Total Records: {processing_result.get('total_records', 'Unknown')}
- Processing Time: {processing_result.get('elapsed_time', 'Unknown')}s
- S3 Location: {result.get('s3_location')}"""
    except Exception as e:
        if "400" in str(e):
            return f"File processing failed: Invalid file type or file validation error."
        return f"Failed to process file from URL: {str(e)}"


@etl_agent.tool
def process_file_from_s3(ctx: RunContext[ETLAgentDeps], params: ProcessFromS3Params) -> str:
    """Process a file directly from S3 using AWS credentials."""
    try:
        data = {
            "aws_access_key": params.aws_access_key,
            "aws_secret_key": params.aws_secret_key,
            "aws_region": params.aws_region,
            "s3_bucket": params.s3_bucket,
            "s3_path": params.s3_path,
            "file_type": params.file_type,
            "tracking_id": params.tracking_id,
            "metadata": params.metadata or {}
        }
        
        if params.partition_format:
            data["partition_format"] = params.partition_format
        if params.start_date:
            data["start_date"] = params.start_date
        if params.end_date:
            data["end_date"] = params.end_date
            
        result = ctx.deps.api_client.post("/api/v1/extraction/process-from-s3", data)
        
        processing_result = result.get('processing_result', {})
        return f"""S3 file processed successfully!
- File: {result.get('file_name', 'Unknown')}
- Type: {result.get('file_type')}
- Data Source ID: {result.get('data_source_id')}
- Total Records: {processing_result.get('total_records', 'Unknown')}
- Processing Time: {processing_result.get('elapsed_time', 'Unknown')}s"""
    except Exception as e:
        if "400" in str(e):
            return f"S3 processing failed: Invalid credentials or file validation error."
        elif "404" in str(e):
            return f"No objects found at the specified S3 path."
        return f"Failed to process file from S3: {str(e)}"


@etl_agent.tool
def process_sql_database(ctx: RunContext[ETLAgentDeps], params: ProcessFromSQLParams) -> str:
    """Process schema from a SQL database."""
    try:
        data = {
            "db_type": params.db_type,
            "host": params.host,
            "port": params.port,
            "username": params.username,
            "password": params.password,
            "database": params.database,
            "table": params.table,
            "tracking_id": params.tracking_id,
            "metadata": params.metadata or {}
        }
        
        if params.schema:
            data["schema"] = params.schema
        if params.query:
            data["query"] = params.query
            
        result = ctx.deps.api_client.post("/api/v1/extraction/process-from-sql", data)
        
        processing_result = result.get('processing_result', {})
        return f"""SQL database processed successfully!
- Database: {params.database} ({params.db_type})
- Table: {params.table}
- Data Source ID: {result.get('data_source_id')}
- Field Count: {processing_result.get('field_count', 'Unknown')}
- Fields: {', '.join(processing_result.get('fields', [])[:5])}{"..." if len(processing_result.get('fields', [])) > 5 else ""}"""
    except Exception as e:
        if "400" in str(e):
            return f"SQL processing failed: Database type unsupported or connection failed."
        return f"Failed to process SQL database: {str(e)}"


@etl_agent.tool
def process_mongodb(ctx: RunContext[ETLAgentDeps], params: ProcessFromMongoParams) -> str:
    """Process schema from a MongoDB database."""
    try:
        data = {
            "connection_string": params.connection_string,
            "db_name": params.db_name,
            "collection_name": params.collection_name,
            "tracking_id": params.tracking_id,
            "use_ssl": params.use_ssl,
            "metadata": params.metadata or {}
        }
        
        if params.username:
            data["username"] = params.username
        if params.password:
            data["password"] = params.password
        if params.connection_options:
            data["connection_options"] = params.connection_options
            
        result = ctx.deps.api_client.post("/api/v1/extraction/process-from-mongo", data)
        
        processing_result = result.get('processing_result', {})
        return f"""MongoDB processed successfully!
- Database: {params.db_name}
- Collection: {params.collection_name}
- Data Source ID: {result.get('data_source_id')}
- Field Count: {processing_result.get('field_count', 'Unknown')}
- Fields: {', '.join(processing_result.get('fields', [])[:5])}{"..." if len(processing_result.get('fields', [])) > 5 else ""}"""
    except Exception as e:
        if "400" in str(e):
            return f"MongoDB processing failed: Connection failed or invalid credentials."
        elif "404" in str(e):
            return f"Database or collection not found, or collection is empty."
        return f"Failed to process MongoDB: {str(e)}"


@etl_agent.tool
def update_data_source(ctx: RunContext[ETLAgentDeps], params: UpdateDataSourceParams) -> str:
    """Update a data source's metadata."""
    try:
        update_data = {}
        if params.name:
            update_data['name'] = params.name
        if params.description:
            update_data['description'] = params.description
        if params.status:
            update_data['status'] = params.status
        if params.tags:
            update_data['tags'] = params.tags
            
        result = ctx.deps.api_client.patch(f"/api/v1/data/{params.data_source_id}", update_data)
        updated_fields = result.get('updated_fields', [])
        return f"Data source updated successfully! Updated fields: {', '.join(updated_fields)}"
    except Exception as e:
        if "404" in str(e):
            return f"Data source '{params.data_source_id}' not found."
        return f"Failed to update data source: {str(e)}"


@etl_agent.tool
def delete_data_source(ctx: RunContext[ETLAgentDeps], data_source_id: str) -> str:
    """Delete a data source and its associated extracted data."""
    try:
        result = ctx.deps.api_client.delete(f"/api/v1/data/{data_source_id}")
        deleted_count = result.get('deleted_data_count', 'Unknown')
        return f"Data source deleted successfully! Deleted {deleted_count} associated data records."
    except Exception as e:
        if "404" in str(e):
            return f"Data source '{data_source_id}' not found."
        return f"Failed to delete data source: {str(e)}"
    

app = etl_agent.to_ag_ui()