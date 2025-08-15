import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from csv_chart_agent import csv_chart_agent, ChartRequest, ChartResponse
from agent import agent

# Load environment variables
load_dotenv()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    csv_data: str = ""

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting CSV Chart Agent Backend...")
    yield
    # Shutdown
    print("👋 Shutting down CSV Chart Agent Backend...")

# Create FastAPI app
app = FastAPI(
    title="CSV Chart Agent",
    description="Pydantic AI agent for CSV data analysis and chart generation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CopilotKit-compatible endpoint that uses the actual Pydantic AI agent
@app.post("/copilotkit")
async def copilotkit_endpoint(request: dict):
    """CopilotKit compatible endpoint for chat completion using Pydantic AI agent with CSV data"""
    try:
        messages = request.get("messages", [])
        csv_data = request.get("csvData", "")
        
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        if not user_message:
            return JSONResponse({
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "Hello! I'm your CSV data analysis expert. I can help you understand your data, suggest appropriate visualizations, and provide insights about data patterns and trends. Upload CSV data first, then ask me questions about it!"
                    }
                }]
            })
        
        # Enhance the user message with CSV context if available
        if csv_data:
            enhanced_message = f"""I have CSV data loaded. Here's the data:

{csv_data}

User question: {user_message}

Please analyze this CSV data and answer the user's question with specific insights about their data. Provide concrete recommendations based on the actual data structure and values."""
        else:
            enhanced_message = f"""No CSV data is currently loaded. The user asked: {user_message}

Please provide general guidance about CSV data analysis and suggest that they upload their CSV data first so you can provide specific insights."""
        
        # Use the Pydantic AI agent to generate response
        try:
            # If this is a chart generation request, use csv_chart_agent
            if any(word in user_message.lower() for word in ['chart', 'graph', 'plot', 'visuali', 'bar', 'line', 'scatter', 'histogram', 'pie']):
                # Use the CSV chart agent for visualization requests
                from csv_chart_agent import ChartRequest
                
                chart_request = ChartRequest(
                    query=user_message,
                    csv_data=csv_data if csv_data else "",
                    chart_type="auto"
                )
                
                try:
                    chart_result = await csv_chart_agent.analyze_and_chart(chart_request)
                    
                    # Return structured response that can trigger chart display
                    response_content = f"I've generated your chart! {chart_result.summary}\n\nKey insights:\n"
                    for insight in chart_result.data_insights[:3]:  # Top 3 insights
                        response_content += f"• {insight}\n"
                    
                    return JSONResponse({
                        "choices": [{
                            "message": {
                                "role": "assistant",
                                "content": response_content,
                                "chart_data": {
                                    "chart_base64": chart_result.chart_base64,
                                    "chart_html": chart_result.chart_html,
                                    "summary": chart_result.summary,
                                    "data_insights": chart_result.data_insights
                                }
                            }
                        }]
                    })
                except Exception as chart_error:
                    # Fallback to regular agent
                    result = await agent.run(enhanced_message)
                    return JSONResponse({
                        "choices": [{
                            "message": {
                                "role": "assistant",
                                "content": str(result.data)
                            }
                        }]
                    })
            else:
                # Use the regular agent for non-chart requests
                result = await agent.run(enhanced_message)
                
                return JSONResponse({
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": str(result.data)
                        }
                    }]
                })
            
        except Exception as agent_error:
            # Fallback response that's still helpful
            if csv_data:
                # Extract some basic info about the CSV for fallback
                lines = csv_data.strip().split('\n')
                headers = lines[0].split(',') if lines else []
                row_count = len(lines) - 1 if len(lines) > 1 else 0
                
                fallback_content = f"I can see you have CSV data loaded with {row_count} rows and these columns: {', '.join(headers)}. I'm having trouble with my AI processing right now, but based on your question '{user_message}', I can suggest that you explore these data relationships. Please try your question again."
            else:
                fallback_content = "I'm here to help you with CSV data analysis! Please upload your CSV data first, then I can provide specific insights about your data patterns, suggest appropriate visualizations, and help you understand your data better."
            
            return JSONResponse({
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": fallback_content
                    }
                }]
            })
        
    except Exception as e:
        return JSONResponse({
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": f"I encountered an error while processing your request. Please try again. Error: {str(e)}"
                }
            }]
        }, status_code=500)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "CSV Chart Agent API",
        "version": "1.0.0",
        "endpoints": {
            "copilotkit": "/copilotkit",
            "health": "/health",
            "analyze": "/analyze",
            "upload": "/upload"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agent": "ready"}

@app.post("/analyze", response_model=ChartResponse)
async def analyze_csv(request: ChartRequest):
    """Direct endpoint to analyze CSV data and generate charts"""
    try:
        response = await csv_chart_agent.analyze_and_chart(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    query: str = Form(...)
):
    """Upload CSV file and analyze with natural language query"""
    try:
        # Read the uploaded file
        content = await file.read()
        csv_string = content.decode('utf-8')
        
        # Create request
        request = ChartRequest(
            query=query,
            csv_data=csv_string
        )
        
        # Analyze and generate chart
        response = await csv_chart_agent.analyze_and_chart(request)
        
        return {
            "filename": file.filename,
            "query": query,
            "chart_base64": response.chart_base64,
            "chart_html": response.chart_html,
            "summary": response.summary,
            "insights": response.data_insights
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """Demo page to test the CSV chart agent"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CSV Chart Agent Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { margin: 20px 0; }
            textarea { width: 100%; min-height: 100px; }
            input[type="file"], input[type="text"] { width: 100%; padding: 10px; margin: 5px 0; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 5px; }
            .chart { text-align: center; margin: 20px 0; }
            .insights { margin-top: 15px; }
            .insights ul { padding-left: 20px; }
        </style>
    </head>
    <body>
        <h1>📊 CSV Chart Agent Demo</h1>
        <p>Upload a CSV file and ask questions about your data in natural language!</p>
        
        <div class="container">
            <h3>Upload CSV File</h3>
            <input type="file" id="csvFile" accept=".csv" />
            
            <h3>Natural Language Query</h3>
            <input type="text" id="query" placeholder="e.g., Show me the trend of sales over time" />
            
            <button onclick="analyzeData()">Analyze Data</button>
        </div>
        
        <div id="result" class="result" style="display: none;">
            <h3>Analysis Result</h3>
            <div id="summary"></div>
            <div id="chart" class="chart"></div>
            <div id="insights" class="insights"></div>
        </div>
        
        <div class="container">
            <h3>Sample CSV Data (for testing)</h3>
            <textarea id="sampleData" readonly>
Date,Sales,Region
2024-01-01,1000,North
2024-01-02,1200,South
2024-01-03,800,East
2024-01-04,1500,West
2024-01-05,1100,North
2024-01-06,1300,South
2024-01-07,900,East
2024-01-08,1600,West
            </textarea>
            <button onclick="useSampleData()">Use Sample Data</button>
        </div>

        <script>
            function useSampleData() {
                const sampleData = document.getElementById('sampleData').value;
                const blob = new Blob([sampleData], { type: 'text/csv' });
                const file = new File([blob], 'sample_data.csv', { type: 'text/csv' });
                
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                document.getElementById('csvFile').files = dataTransfer.files;
                
                document.getElementById('query').value = 'Show me the sales trend over time';
            }
            
            async function analyzeData() {
                const fileInput = document.getElementById('csvFile');
                const queryInput = document.getElementById('query');
                
                if (!fileInput.files[0]) {
                    alert('Please select a CSV file');
                    return;
                }
                
                if (!queryInput.value.trim()) {
                    alert('Please enter a query');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                formData.append('query', queryInput.value);
                
                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        throw new Error('Analysis failed');
                    }
                    
                    const result = await response.json();
                    displayResult(result);
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            }
            
            function displayResult(result) {
                document.getElementById('summary').innerHTML = '<p><strong>Summary:</strong> ' + result.summary + '</p>';
                
                // Display chart
                if (result.chart_base64) {
                    document.getElementById('chart').innerHTML = '<img src="data:image/png;base64,' + result.chart_base64 + '" style="max-width: 100%;" />';
                }
                
                // Display insights
                let insightsHtml = '<h4>Key Insights:</h4><ul>';
                result.insights.forEach(insight => {
                    insightsHtml += '<li>' + insight + '</li>';
                });
                insightsHtml += '</ul>';
                document.getElementById('insights').innerHTML = insightsHtml;
                
                document.getElementById('result').style.display = 'block';
            }
        </script>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"🚀 Starting server on {host}:{port}")
    print(f"📊 CSV Chart Agent API available at: http://{host}:{port}")
    print(f"🔧 CopilotKit endpoint: http://{host}:{port}/copilotkit")
    print(f"🧪 Demo page: http://{host}:{port}/demo")
    
    uvicorn.run(
        "backend:app",
        host=host,
        port=port,
        reload=True
    )