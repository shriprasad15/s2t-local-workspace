from functools import cache

from mcp.server.sse import SseServerTransport

from core.config import settings
from .sse_server import SSEServer


@cache
def get_mcp_sse_server() -> SSEServer:
    return SSEServer(settings.APP_NAME + ":mcp")


@cache
def get_mcp_sse_transport(endpoint: str) -> SseServerTransport:
    return SseServerTransport(endpoint)
