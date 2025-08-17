from fastapi import APIRouter

from .ai import router as ai_router
from .ping import router as ping_router
from .sse import router as sse_router
from .websocket import router as ws_router

v1_router = APIRouter()
v1_router.include_router(ping_router, tags=["healthcheck"])
v1_router.include_router(sse_router, tags=["sse"])
v1_router.include_router(ai_router, tags=["ai"], prefix="/ai")
v1_router.include_router(ws_router, tags=["websocket"])
