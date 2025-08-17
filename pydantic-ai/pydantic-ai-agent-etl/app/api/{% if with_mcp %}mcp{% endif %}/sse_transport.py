from fastapi import APIRouter, Request

from core.mcp import get_mcp_sse_transport, get_mcp_server

_MCP_ENDPOINT = "/mcp"
router = APIRouter(prefix=_MCP_ENDPOINT, tags=["mcp"])
sse_transport = get_mcp_sse_transport(_MCP_ENDPOINT + "/messages")
mcp_app = get_mcp_server()


@router.get("/sse")
async def handle_sse(req: Request):
    async with sse_transport.connect_sse(req.scope, req.receive, req._send) as streams:
        await mcp_app.run(streams[0], streams[1], mcp_app.create_initialization_options())


@router.post("/messages")
async def handle_messages(req: Request):
    await sse_transport.handle_post_message(req.scope, req.receive, req._send)
