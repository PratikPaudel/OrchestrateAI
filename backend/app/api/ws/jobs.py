from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
from app.core.graph import execute_research_with_progress
from app.utils.logger import logger

router = APIRouter()

@router.websocket("/ws/jobs")
async def websocket_job(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        query = data.get("query")
        logger.info(f"Received query: {query}")

        async def send_progress(step, status, message=None, progress=None):
            payload = {"step": step, "status": status}
            if message:
                payload["message"] = message
            if progress is not None:
                payload["progress"] = progress
            await websocket.send_json(payload)

        # Call the async workflow and stream progress
        final_report = None
        async for update in execute_research_with_progress(query, send_progress):
            if update.get("final_report"):
                final_report = update["final_report"]
        await websocket.send_json({"status": "complete", "final_report": final_report or ""})
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error in WebSocket: {e}")
        await websocket.send_json({"status": "error", "message": str(e)})
    finally:
        # Gracefully close the connection if it's still open
        if websocket.client_state != "DISCONNECTED":
            await websocket.close()