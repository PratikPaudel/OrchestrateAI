from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
from app.core.graph import execute_research
from app.utils.logger import logger

router = APIRouter()

@router.websocket("/ws/jobs")
async def websocket_job(websocket: WebSocket):
    await websocket.accept()
    try:
        # Receive the initial message (e.g., the query)
        data = await websocket.receive_json()
        query = data.get("query")
        logger.info(f"Received query: {query}")

        # Call the real workflow (blocking, but for test)
        result = execute_research(query)
        await websocket.send_json({"status": "complete", "final_report": result.get("final_report", "")})
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error in WebSocket: {e}")
        await websocket.send_json({"status": "error", "message": str(e)})

# Example async generator for progress (replace with your real logic)
async def run_job_with_progress(query):
    steps = [
        {"step": "planner", "status": "in_progress", "progress": 10, "message": "Planning..."},
        {"step": "searcher", "status": "in_progress", "progress": 40, "message": "Searching..."},
        {"step": "summarizer", "status": "in_progress", "progress": 70, "message": "Summarizing..."},
        {"step": "writer", "status": "in_progress", "progress": 100, "message": "Writing report..."},
    ]
    for step in steps:
        await asyncio.sleep(1)  # Simulate work
        yield step