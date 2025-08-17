# app/api/v1/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.websocket_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    correlation_id = await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
                
    except WebSocketDisconnect:
        await manager.disconnect(correlation_id)
    except Exception as e:
        await manager.disconnect(correlation_id)
