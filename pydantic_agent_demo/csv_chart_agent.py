import asyncio
import base64
import io
import os
from typing import Any, Dict, List, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import seaborn as sns
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set matplotlib to use Agg backend for server environments
plt.switch_backend('Agg')

class ChartRequest(BaseModel):
    """Request model for chart generation"""
    query: str = Field(description="Natural language query about the data")
    csv_data: Optional[str] = Field(None, description="CSV data as string")
    chart_type: Optional[str] = Field("auto", description="Type of chart to generate (bar, line, scatter, histogram, pie, auto)")

class ChartResponse(BaseModel):
    """Response model for chart generation"""
    chart_base64: str = Field(description="Base64 encoded chart image")
    chart_html: Optional[str] = Field(None, description="Interactive chart HTML")
    summary: str = Field(description="Summary of the analysis")
    data_insights: List[str] = Field(description="Key insights from the data")

class CSVChartAgent:
    """Pydantic AI Agent for CSV analysis and chart generation"""
    
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        
        # Configure OpenAI model with custom API key and base URL
        api_key = os.getenv('OPENAI_API_KEY')
        base_url = os.getenv('OPENAI_BASE_URL')
        
        if not api_key:
            api_key = os.getenv('DOSASHOP_API_KEY')
        if not base_url:
            base_url = os.getenv('DOSASHOP_URL')
            
        # Create OpenAI model with custom configuration
        model = OpenAIModel(
            'gpt-4o',
            api_key=api_key,
            base_url=base_url
        )
        
        self.agent = Agent(
            model=model,
            system_prompt="""
            You are a data analysis expert specializing in CSV data visualization.
            Your job is to analyze CSV data and create appropriate charts based on natural language queries.
            
            Key capabilities:
            - Load and analyze CSV data
            - Understand natural language queries about data
            - Generate appropriate chart types (bar, line, scatter, histogram, pie)
            - Provide data insights and summaries
            - Create both static (matplotlib) and interactive (plotly) charts
            
            When analyzing data:
            1. First understand the structure and content of the data
            2. Interpret the user's query to determine what they want to visualize
            3. Choose the most appropriate chart type
            4. Generate the chart with proper titles, labels, and formatting
            5. Provide meaningful insights about the data
            
            Always be helpful and provide clear explanations of your analysis.
            """,
            result_type=ChartResponse,
        )
    
    def load_csv_from_string(self, csv_string: str) -> pd.DataFrame:
        """Load CSV data from string"""
        try:
            # Try different encodings and separators
            for sep in [',', ';', '\t']:
                try:
                    df = pd.read_csv(io.StringIO(csv_string), sep=sep)
                    if len(df.columns) > 1:  # Successfully parsed with multiple columns
                        self.df = df
                        return df
                except:
                    continue
            
            # Fallback to comma separator
            df = pd.read_csv(io.StringIO(csv_string))
            self.df = df
            return df
        except Exception as e:
            raise ValueError(f"Failed to parse CSV data: {str(e)}")
    
    def load_csv_from_file(self, file_path: str) -> pd.DataFrame:
        """Load CSV data from file"""
        try:
            df = pd.read_csv(file_path)
            self.df = df
            return df
        except Exception as e:
            raise ValueError(f"Failed to load CSV file: {str(e)}")
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the loaded data"""
        if self.df is None:
            return {"error": "No data loaded"}
        
        return {
            "shape": self.df.shape,
            "columns": list(self.df.columns),
            "dtypes": dict(self.df.dtypes.astype(str)),
            "null_counts": dict(self.df.isnull().sum()),
            "summary_stats": self.df.describe().to_dict()
        }
    
    def determine_chart_type(self, query: str, requested_type: str = "auto") -> str:
        """Determine the most appropriate chart type based on query and data"""
        if requested_type != "auto":
            return requested_type
        
        query_lower = query.lower()
        
        # Keywords for different chart types
        if any(word in query_lower for word in ['trend', 'over time', 'time series', 'timeline']):
            return 'line'
        elif any(word in query_lower for word in ['compare', 'comparison', 'versus', 'vs']):
            return 'bar'
        elif any(word in query_lower for word in ['relationship', 'correlation', 'scatter']):
            return 'scatter'
        elif any(word in query_lower for word in ['distribution', 'frequency', 'histogram']):
            return 'histogram'
        elif any(word in query_lower for word in ['proportion', 'percentage', 'pie', 'share']):
            return 'pie'
        else:
            return 'bar'  # Default to bar chart
    
    def create_matplotlib_chart(self, chart_type: str, x_col: str, y_col: str, title: str) -> str:
        """Create a matplotlib chart and return as base64 string"""
        plt.figure(figsize=(10, 6))
        plt.style.use('seaborn-v0_8')
        
        # Make a copy to avoid modifying original data
        df_work = self.df.copy()
        
        # Convert y_col to numeric if possible
        if y_col in df_work.columns:
            df_work[y_col] = pd.to_numeric(df_work[y_col], errors='coerce')
        
        if chart_type == 'bar':
            try:
                if df_work[x_col].dtype == 'object' or len(df_work[x_col].unique()) < 20:
                    # Categorical data - aggregate by x_col
                    if df_work[y_col].dtype in ['int64', 'float64'] and not df_work[y_col].isna().all():
                        # Use sum for aggregation (consistent with business logic)
                        data_grouped = df_work.groupby(x_col)[y_col].sum().sort_values(ascending=False)
                        plt.bar(range(len(data_grouped)), data_grouped.values)
                        plt.xticks(range(len(data_grouped)), data_grouped.index, rotation=45, ha='right')
                    else:
                        # Fallback: use value counts for categorical y data
                        data_counts = df_work[x_col].value_counts().sort_values(ascending=False)
                        plt.bar(range(len(data_counts)), data_counts.values)
                        plt.xticks(range(len(data_counts)), data_counts.index, rotation=45, ha='right')
                else:
                    # Direct plotting for numerical x-axis
                    plt.bar(df_work[x_col], df_work[y_col])
                    plt.xticks(rotation=45, ha='right')
            except Exception as e:
                # Ultimate fallback: use value counts of x_col
                data_counts = df_work[x_col].value_counts().sort_values(ascending=False)
                plt.bar(range(len(data_counts)), data_counts.values)
                plt.xticks(range(len(data_counts)), data_counts.index, rotation=45, ha='right')
        
        elif chart_type == 'line':
            plt.plot(self.df[x_col], self.df[y_col], marker='o')
        
        elif chart_type == 'scatter':
            plt.scatter(self.df[x_col], self.df[y_col], alpha=0.6)
        
        elif chart_type == 'histogram':
            plt.hist(self.df[y_col], bins=30, alpha=0.7)
        
        elif chart_type == 'pie':
            if self.df[x_col].dtype == 'object':
                value_counts = self.df[x_col].value_counts().head(10)  # Top 10 categories
                plt.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%')
        
        plt.title(title)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return chart_base64
    
    def create_plotly_chart(self, chart_type: str, x_col: str, y_col: str, title: str) -> str:
        """Create a plotly chart and return as HTML string"""
        # Make a copy to avoid modifying original data
        df_work = self.df.copy()
        
        # Convert y_col to numeric if possible
        try:
            df_work[y_col] = pd.to_numeric(df_work[y_col], errors='coerce')
        except:
            pass
            
        if chart_type == 'bar':
            try:
                if df_work[x_col].dtype == 'object' or len(df_work[x_col].unique()) < 20:
                    if df_work[y_col].dtype in ['int64', 'float64'] and not df_work[y_col].isna().all():
                        # Use sum for aggregation (consistent with matplotlib)
                        data_grouped = df_work.groupby(x_col)[y_col].sum().reset_index().sort_values(y_col, ascending=False)
                        fig = px.bar(data_grouped, x=x_col, y=y_col, title=title)
                    else:
                        # Fallback: use value counts
                        data_counts = df_work[x_col].value_counts().reset_index()
                        data_counts.columns = [x_col, 'count']
                        data_counts = data_counts.sort_values('count', ascending=False)
                        fig = px.bar(data_counts, x=x_col, y='count', title=title)
                else:
                    fig = px.bar(df_work, x=x_col, y=y_col, title=title)
            except Exception as e:
                # Ultimate fallback: use value counts
                data_counts = df_work[x_col].value_counts().reset_index()
                data_counts.columns = [x_col, 'count']
                data_counts = data_counts.sort_values('count', ascending=False)
                fig = px.bar(data_counts, x=x_col, y='count', title=title)
        
        elif chart_type == 'line':
            fig = px.line(self.df, x=x_col, y=y_col, title=title, markers=True)
        
        elif chart_type == 'scatter':
            fig = px.scatter(self.df, x=x_col, y=y_col, title=title)
        
        elif chart_type == 'histogram':
            fig = px.histogram(self.df, x=y_col, title=title, nbins=30)
        
        elif chart_type == 'pie':
            if self.df[x_col].dtype == 'object':
                value_counts = self.df[x_col].value_counts().head(10)
                fig = px.pie(values=value_counts.values, names=value_counts.index, title=title)
        
        # Update layout for better appearance
        fig.update_layout(
            template="plotly_white",
            title_x=0.5,
            font=dict(size=12)
        )
        
        return pio.to_html(fig, include_plotlyjs='cdn', div_id="chart")
    
    def extract_insights(self, x_col: str, y_col: str, chart_type: str) -> List[str]:
        """Extract key insights from the data"""
        insights = []
        
        try:
            if chart_type in ['bar', 'line', 'scatter']:
                # Basic statistics
                insights.append(f"Dataset contains {len(self.df)} records")
                insights.append(f"Analyzing relationship between {x_col} and {y_col}")
                
                if self.df[y_col].dtype in ['int64', 'float64']:
                    mean_val = self.df[y_col].mean()
                    max_val = self.df[y_col].max()
                    min_val = self.df[y_col].min()
                    
                    insights.append(f"Average {y_col}: {mean_val:.2f}")
                    insights.append(f"Range: {min_val:.2f} to {max_val:.2f}")
                
                # Correlation for scatter plots
                if chart_type == 'scatter' and self.df[x_col].dtype in ['int64', 'float64']:
                    correlation = self.df[x_col].corr(self.df[y_col])
                    if abs(correlation) > 0.7:
                        strength = "strong"
                    elif abs(correlation) > 0.3:
                        strength = "moderate"
                    else:
                        strength = "weak"
                    insights.append(f"Correlation between {x_col} and {y_col}: {strength} ({correlation:.3f})")
            
            elif chart_type == 'histogram':
                insights.append(f"Distribution analysis of {y_col}")
                if self.df[y_col].dtype in ['int64', 'float64']:
                    skewness = self.df[y_col].skew()
                    if abs(skewness) < 0.5:
                        dist_shape = "approximately normal"
                    elif skewness > 0.5:
                        dist_shape = "right-skewed"
                    else:
                        dist_shape = "left-skewed"
                    insights.append(f"Distribution shape: {dist_shape}")
            
            elif chart_type == 'pie':
                insights.append(f"Proportion breakdown of {x_col}")
                top_category = self.df[x_col].value_counts().index[0]
                top_percentage = (self.df[x_col].value_counts().iloc[0] / len(self.df)) * 100
                insights.append(f"Most common category: {top_category} ({top_percentage:.1f}%)")
        
        except Exception as e:
            insights.append("Unable to extract detailed insights due to data complexity")
        
        return insights
    
    def identify_columns(self, query: str) -> tuple[str, str]:
        """Identify the most relevant columns for the query"""
        if self.df is None:
            raise ValueError("No data loaded")
        
        columns = list(self.df.columns)
        query_lower = query.lower()
        
        # Smart column identification based on query context
        x_col = None
        y_col = None
        
        # Look for specific column names in the query
        for col in columns:
            col_lower = col.lower()
            if col_lower in query_lower:
                # Determine if this should be x or y based on context
                if col_lower in ['region', 'category', 'product', 'type', 'date']:
                    x_col = col
                elif col_lower in ['sales', 'value', 'amount', 'count', 'price']:
                    y_col = col
                elif x_col is None:
                    x_col = col
                elif y_col is None:
                    y_col = col
        
        # If not found, use improved heuristics
        if x_col is None or y_col is None:
            # Make a copy to avoid modifying original data
            df_work = self.df.copy()
            
            # Convert potential numeric columns
            for col in columns:
                if col != x_col:  # Don't convert x_col if already set
                    try:
                        numeric_data = pd.to_numeric(df_work[col], errors='coerce')
                        if not numeric_data.isna().all():
                            df_work[col] = numeric_data
                    except:
                        pass
            
            numeric_cols = list(df_work.select_dtypes(include=['number']).columns)
            categorical_cols = list(df_work.select_dtypes(include=['object']).columns)
            
            # Better heuristics based on query type
            if any(word in query_lower for word in ['region', 'by region', 'region wise', 'by category', 'category wise']):
                # Look for categorical column for grouping
                if not x_col:
                    # Prioritize region/category columns
                    region_cols = [col for col in categorical_cols if any(keyword in col.lower() for keyword in ['region', 'category', 'product', 'type'])]
                    x_col = region_cols[0] if region_cols else (categorical_cols[0] if categorical_cols else columns[0])
                if not y_col:
                    # Prioritize numeric columns like sales, value, amount
                    value_cols = [col for col in numeric_cols if any(keyword in col.lower() for keyword in ['sales', 'value', 'amount', 'price', 'count'])]
                    y_col = value_cols[0] if value_cols else (numeric_cols[0] if numeric_cols else columns[-1])
            else:
                # Default logic
                if not x_col:
                    x_col = categorical_cols[0] if categorical_cols else columns[0]
                if not y_col:
                    y_col = numeric_cols[0] if numeric_cols else columns[-1]
        
        return x_col, y_col
    
    async def analyze_and_chart(self, request: ChartRequest) -> ChartResponse:
        """Main method to analyze data and generate charts"""
        try:
            # Load data if provided
            if request.csv_data:
                self.load_csv_from_string(request.csv_data)
            
            if self.df is None:
                raise ValueError("No CSV data provided or loaded")
            
            # Determine chart type
            chart_type = self.determine_chart_type(request.query, request.chart_type)
            
            # Identify relevant columns
            x_col, y_col = self.identify_columns(request.query)
            
            # Generate title
            title = f"{request.query.title()} - {chart_type.title()} Chart"
            
            # Create charts
            chart_base64 = self.create_matplotlib_chart(chart_type, x_col, y_col, title)
            chart_html = self.create_plotly_chart(chart_type, x_col, y_col, title)
            
            # Extract insights
            insights = self.extract_insights(x_col, y_col, chart_type)
            
            # Create summary
            summary = f"Generated a {chart_type} chart showing {x_col} vs {y_col}. "
            summary += f"The visualization reveals patterns in your data based on the query: '{request.query}'"
            
            return ChartResponse(
                chart_base64=chart_base64,
                chart_html=chart_html,
                summary=summary,
                data_insights=insights
            )
        
        except Exception as e:
            return ChartResponse(
                chart_base64="",
                chart_html="<div>Error generating chart</div>",
                summary=f"Error: {str(e)}",
                data_insights=[f"Failed to process request: {str(e)}"]
            )

# Global agent instance
csv_chart_agent = CSVChartAgent()