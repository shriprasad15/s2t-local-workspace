# CSV Chart Agent

A Pydantic AI agent that loads CSV data and generates charts based on natural language queries, integrated with CopilotKit.

## Features

- 📊 **Smart Chart Generation**: Automatically determines the best chart type based on your query
- 🤖 **Natural Language Interface**: Ask questions about your data in plain English
- 📈 **Multiple Chart Types**: Bar charts, line charts, scatter plots, histograms, and pie charts
- 🎨 **Interactive Visualizations**: Both static (matplotlib) and interactive (plotly) charts
- 💡 **Data Insights**: Get key insights and statistics about your data
- 🔗 **CopilotKit Integration**: Modern chat interface with AI-powered assistance

## Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Backend

```bash
python backend.py
```

The backend will be available at `http://localhost:8000`

### 3. Install Frontend Dependencies

```bash
npm install
```

### 4. Start the Frontend

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

1. **Upload CSV Data**: Click the upload button to select your CSV file
2. **Ask Questions**: Use natural language to query your data
   - "Show me the sales trend over time"
   - "Compare revenue by region"
   - "What's the distribution of customer ages?"
   - "Create a scatter plot of price vs quantity"
3. **Get Insights**: The AI will generate appropriate charts and provide data insights

## Sample Questions

- **Trend Analysis**: "Show me the trend of sales over time"
- **Comparisons**: "Compare revenue by region"
- **Distributions**: "Show the distribution of customer ages"
- **Correlations**: "What's the relationship between price and quantity?"
- **Top/Bottom Analysis**: "Show me the top 10 products by sales"

## API Endpoints

- `/copilotkit` - CopilotKit integration endpoint
- `/analyze` - Direct API for chart generation
- `/upload` - File upload endpoint
- `/demo` - Built-in demo page
- `/health` - Health check

## Environment Variables

The application uses environment variables from `.env` file:
- `OPENAI_API_KEY` - OpenAI API key (uses DOSASHOP_API_KEY)
- `OPENAI_BASE_URL` - OpenAI API base URL (uses DOSASHOP_URL)

## Architecture

### Backend (Python + FastAPI)
- **Pydantic AI Agent**: Core logic for CSV analysis and chart generation
- **FastAPI**: Web framework for API endpoints
- **CopilotKit Integration**: Exposes the agent through CopilotKit
- **Chart Generation**: matplotlib for static charts, plotly for interactive charts
- **Data Processing**: pandas for CSV manipulation and analysis

### Frontend (Next.js + React)
- **Next.js 14**: Modern React framework with App Router
- **CopilotKit React Components**: AI chat interface
- **Tailwind CSS**: Utility-first CSS framework
- **File Upload**: Drag-and-drop CSV file handling
- **Responsive Design**: Works on desktop and mobile

## Supported Chart Types

The agent automatically selects the best chart type based on your query:

- **Bar Charts**: Comparisons, categorical data
- **Line Charts**: Trends over time, time series data
- **Scatter Plots**: Relationships between variables, correlations
- **Histograms**: Data distributions, frequency analysis
- **Pie Charts**: Proportions, percentage breakdowns

## Development

### Backend Development

```bash
# Run with auto-reload
python backend.py

# Or use uvicorn directly
uvicorn backend:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
# Development mode
npm run dev

# Build for production
npm run build
npm start
```

## Troubleshooting

1. **Module Import Errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   npm install
   ```

2. **CORS Issues**: The backend is configured to allow requests from localhost:3000

3. **Chart Generation Issues**: Ensure matplotlib backend is properly configured for your environment

4. **File Upload Issues**: Check file size limits and CSV format

## License

This project is for demonstration purposes of Pydantic AI integration with CopilotKit.