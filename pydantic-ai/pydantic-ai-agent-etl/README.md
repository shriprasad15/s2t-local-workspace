# ETL AI Agent API

A comprehensive FastAPI-based service that provides a natural language interface for ETL (Extract, Transform, Load) operations. This service uses Pydantic AI to process natural language queries and interact with ETL microservices.

## Features

### 🤖 Natural Language Processing
- Process complex ETL operations using simple natural language commands
- Intelligent query understanding and execution
- Context-aware responses with helpful explanations

### 👥 User Management
- Create, update, list, and delete users
- User-specific data source access control
- Comprehensive user profile management

### 📊 Data Source Management
- List, view, update, and delete data sources
- Advanced filtering by type, status, and tags
- Metadata management and organization

### 🔄 Data Sharing
- Share data sources between users
- Access control and permission management
- Collaborative data workflows

### 🔧 Data Processing
- **File Processing**: CSV, JSON, Log files, Parquet
- **URL Processing**: Process files from presigned URLs
- **S3 Integration**: Direct S3 bucket processing with AWS credentials
- **SQL Databases**: PostgreSQL, MySQL, SQL Server support
- **MongoDB**: NoSQL database schema extraction
- **Partitioned Data**: Handle time-based partitioned datasets

### 🔍 Data Querying
- Natural language queries against processed data
- Automatic chart configuration generation
- Multiple chart themes (light, dark, auto)
- Document retrieval and analysis

### ⚡ Service Health
- Comprehensive health monitoring
- ETL service connectivity checks
- Error handling and diagnostics

## Quick Start

### Prerequisites
- Python 3.8+
- Access to an ETL microservice
- OpenAI API key or custom AI model endpoint

### Installation

1. **Clone and navigate to the project**
   ```bash
   cd pydantic-ai-agent-etl
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run quick tests**
   ```bash
   python quick_test.py
   ```

5. **Start the API server**
   ```bash
   python main.py
   # or
   uvicorn main:app --reload --host 0.0.0.0 --port 8080
   ```

## Configuration

### Environment Variables

```bash
# ETL API Configuration
ETL_API_URL=http://cyber-ai-etl-microservice.cyber.svc.cluster.local
ETL_USER_ID=system

# AI Model Configuration
API_KEY=your_custom_api_key_here
# or
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
APP_PORT=8080
ENVIRONMENT=development
```

## API Endpoints

### Core Endpoints

- **`GET /`** - Service information and available endpoints
- **`GET /api/v1/ai/health`** - Health check with ETL service status
- **`POST /api/v1/ai/query`** - Natural language query processing
- **`GET /api/v1/ai/capabilities`** - Available operations and examples

### Example API Usage

```bash
# Health check
curl http://localhost:8080/api/v1/ai/health

# Natural language query
curl -X POST http://localhost:8080/api/v1/ai/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Create a user named john with email john@example.com",
    "user_id": "optional_user_id"
  }'
```

## Usage Examples

### User Management
```
"Create a user named alice with email alice@example.com"
"List all users in the system"
"Update user john's email to newemail@example.com"
"Delete user bob"
```

### Data Source Operations
```
"Show me all data sources"
"List data sources with status active"
"Get details for data source abc-123"
"Update data source xyz-456 name to 'Sales Data'"
```

### Data Processing
```
"Process a CSV file from this URL: https://example.com/data.csv"
"Process data from S3 bucket my-bucket path data/file.json"
"Extract schema from PostgreSQL database on host db.example.com"
"Process MongoDB collection users from database analytics"
```

### Data Querying
```
"Query the sales data for revenue by region"
"Show me the top 10 customers by purchase amount"
"Get monthly trends from the user activity data"
```

### Data Sharing
```
"Share data source abc-123 from user john to user jane"
"Show all data sources accessible by user alice"
```

## Interactive Demo

### Command Line Demo
```bash
python demo.py
```

### Test Scenarios
```bash
python test_scenarios.py
```

## Development

### Project Structure
```
pydantic-ai-agent-etl/
├── app/
│   └── api/
│       └── v1/
│           ├── ai.py          # Main ETL AI endpoints
│           ├── ping.py        # Health check
│           ├── sse.py         # Server-sent events
│           └── websocket.py   # WebSocket support
├── core/
│   ├── api_client.py          # ETL service HTTP client
│   ├── etl_agent.py           # Pydantic AI agent with tools
│   ├── model.py               # AI model configuration
│   ├── config.py              # Application settings
│   └── server.py              # FastAPI app setup
├── demo.py                    # Interactive demo script
├── test_scenarios.py          # Comprehensive test suite
├── quick_test.py              # Quick validation tests
└── main.py                    # Application entry point
```

### Available Tools

The ETL agent includes comprehensive tools for:

- **Health Monitoring**: `ping_service`, `test_error_handling`
- **User Management**: `create_user`, `get_user`, `list_users`, `update_user`, `delete_user`
- **Data Sources**: `list_data_sources`, `get_data_source`, `update_data_source`, `delete_data_source`
- **Data Sharing**: `share_data_source`, `get_user_data_sources`
- **Data Processing**: `process_file_from_url`, `process_file_from_s3`, `process_sql_database`, `process_mongodb`
- **Data Querying**: `query_data`

### Adding Custom Tools

To add new tools to the ETL agent:

1. Define parameter models in `core/etl_agent.py`
2. Create tool functions with `@etl_agent.tool` decorator
3. Implement ETL service API calls using the `APIClient`
4. Add comprehensive error handling and user-friendly responses

## Deployment

### Docker Support
The project includes Docker configuration from the boilerplate:
```bash
docker build -t etl-ai-agent .
docker run -d -p 8080:8080 --env-file .env etl-ai-agent
```

### Kubernetes
Deploy using the included Kubernetes configurations with appropriate environment variables.

## Monitoring and Logging

- Comprehensive logging with correlation IDs
- Prometheus metrics via `prometheus-fastapi-instrumentator`
- Health check endpoints for monitoring systems
- Request/response tracking and error reporting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass with `python quick_test.py`
5. Submit a pull request

## License

This project follows the same license as the FastAPI boilerplate it's based on.

## Support

For issues and questions:
1. Run `python quick_test.py` to validate setup
2. Check logs for detailed error information
3. Verify ETL service connectivity
4. Review configuration and environment variables

---

**Built with FastAPI, Pydantic AI, and comprehensive ETL integration for seamless natural language data operations.**
