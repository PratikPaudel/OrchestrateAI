from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json

router = APIRouter()

@router.websocket("/ws/jobs")
async def websocket_job(websocket: WebSocket):
    await websocket.accept()
    try:
        # Receive the initial message (e.g., the query)
        data = await websocket.receive_json()
        query = data.get("query")
        # Start the research job (simulate with async generator)
        async for update in run_job_with_progress(query):
            await websocket.send_json(update)
        await websocket.send_json({"status": "complete"})
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
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