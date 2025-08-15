"""
HTTP client helper for the ETL API service.
"""
import httpx
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel
import json


class APIClient:
    """HTTP client for making requests to the ETL API service."""
    
    def __init__(self, base_url: str = "http://localhost:8000", user_id: str = "default-user"):
        self.base_url = base_url.rstrip("/")
        self.user_id = user_id
        self.client = httpx.Client(timeout=30.0)
        
    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get standard headers for API requests."""
        headers = {
            "x-user-id": self.user_id,
            "Content-Type": "application/json"
        }
        if additional_headers:
            headers.update(additional_headers)
        return headers
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        url = f"{self.base_url}{endpoint}"
        response = self.client.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request."""
        url = f"{self.base_url}{endpoint}"
        response = self.client.post(
            url, 
            headers=self._get_headers(), 
            json=data if data else {}
        )
        response.raise_for_status()
        return response.json()
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request."""
        url = f"{self.base_url}{endpoint}"
        response = self.client.put(
            url, 
            headers=self._get_headers(), 
            json=data if data else {}
        )
        response.raise_for_status()
        return response.json()
    
    def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PATCH request."""
        url = f"{self.base_url}{endpoint}"
        response = self.client.patch(
            url, 
            headers=self._get_headers(), 
            json=data if data else {}
        )
        response.raise_for_status()
        return response.json()
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request."""
        url = f"{self.base_url}{endpoint}"
        response = self.client.delete(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Response models for better type safety
class ApiResponse(BaseModel):
    """Base API response model."""
    status: Optional[str] = None
    message: Optional[str] = None


class DataSource(BaseModel):
    """Data source model."""
    id: str
    source_type: str
    schema_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    status: str
    created_at: str
    updated_at: Optional[str] = None
    created_by: str
    tags: Optional[list[str]] = None


class User(BaseModel):
    """User model."""
    id: str
    username: str
    email: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
    is_active: bool
    data_sources: list[str]


class QueryResult(BaseModel):
    """Query result model."""
    status: str
    data_source_id: str
    schema_id: Optional[str] = None
    natural_language_query: str
    query_type: Optional[str] = None
    generated_query: Optional[Any] = None
    documents: Optional[list[Dict[str, Any]]] = None
    chart_config: Optional[Dict[str, Any]] = None
    chart_planning: Optional[Dict[str, Any]] = None