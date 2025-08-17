# core/websocket_manager.py
from fastapi import WebSocket, Request
from typing import Dict
from core.middleware import CorrelationIdMiddleware, LoggingMiddleware

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        # Create mock app for middleware
        mock_app = type('MockApp', (), {'__call__': lambda x, y, z, w: None})()
        self.correlation_middleware = CorrelationIdMiddleware(app=mock_app)
        self.logging_middleware = LoggingMiddleware(app=mock_app)
        
    async def connect(self, websocket: WebSocket) -> str:
        """Accept connection and handle correlation ID"""
        correlation_id = websocket.headers.get('x-correlation-id')
        if not correlation_id:
            mock_request = Request(scope={
                'type': 'http',
                'headers': websocket.headers.raw,
                'method': 'GET',
                'path': '/ws',
                'server': ('testserver', 80),
                'scheme': 'http'
            })
            
            async def mock_call_next(request):
                return type('Response', (), {'headers': {}, 'status_code': 101})()
                
            response = await self.correlation_middleware.dispatch(mock_request, mock_call_next)
            correlation_id = response.headers.get('x-correlation-id')
            await self.logging_middleware.dispatch(mock_request, mock_call_next)
        
        try:
            await websocket.accept()
            self.active_connections[correlation_id] = websocket
            
            mock_request = Request(scope={
                'type': 'http',
                'headers': [(b'x-correlation-id', correlation_id.encode())],
                'method': 'GET',
                'path': '/ws',
                'server': ('testserver', 80),
                'scheme': 'http'
            })
            await self.logging_middleware._log_request(mock_request)
            
        except Exception as e:
            mock_response = type('Response', (), {
                'status_code': 500,
                'headers': {'x-correlation-id': correlation_id}
            })()
            await self.logging_middleware._log_response(mock_response, 0)
            raise
            
        return correlation_id

    async def disconnect(self, correlation_id: str):
        if correlation_id in self.active_connections:
            mock_request = Request(scope={
                'type': 'http',
                'headers': [(b'x-correlation-id', correlation_id.encode())],
                'method': 'GET',
                'path': '/ws',
                'server': ('testserver', 80),
                'scheme': 'http'
            })
            
            async def mock_call_next(request):
                return type('Response', (), {'status_code': 200, 'headers': {}})()
            
            await self.logging_middleware.dispatch(mock_request, mock_call_next)
            del self.active_connections[correlation_id]
