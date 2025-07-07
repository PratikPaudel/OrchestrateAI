from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
from app.core.graph import execute_research, research_graph
from app.utils.logger import logger

router = APIRouter()

@router.websocket("/ws/jobs")
async def websocket_job(websocket: WebSocket):
    await websocket.accept()
    
    # --- FIX 1: Keep track of steps we've already sent to the client ---
    sent_steps = set()

    try:
        data = await websocket.receive_json()
        query = data.get("query")
        if not query:
            await websocket.send_json({"status": "error", "message": "No query provided."})
            return
        
        logger.info(f"Received query: {query}")

        inputs = {"query": query}
        
        # --- FIX 2: Define the mapping from graph state keys to frontend step names ---
        step_map = {
            "plan": {"step": "planner", "message": "Research plan created.", "progress": 25},
            "search_results": {"step": "searcher", "message": "Initial search complete.", "progress": 50},
            "research_data": {"step": "summarizer", "message": "Sources summarized and reviewed.", "progress": 75},
            "final_report": {"step": "writer", "message": "Final report generated.", "progress": 100},
        }

        # Stream the graph's execution and send progress intelligently
        for state in research_graph.stream(inputs, stream_mode="values"):
            for state_key, step_info in step_map.items():
                # Check if the step is complete (key exists in state) AND we haven't sent it yet
                if state_key in state and state[state_key] and step_info["step"] not in sent_steps:
                    
                    # For the final report, include the report content
                    if step_info["step"] == "writer":
                        payload = {
                            "step": "writer",
                            "status": "complete",
                            "final_report": state["final_report"]
                        }
                    else:
                        payload = {
                           "step": step_info["step"],
                           "status": "complete",
                           "message": step_info["message"],
                           "progress": step_info["progress"]
                        }
                    
                    await websocket.send_json(payload)
                    sent_steps.add(step_info["step"])
                    logger.info(f"Sent update for step: {step_info['step']}")

        # The graph is finished, send a final completion status
        # Note: The 'writer' step already implies completion in the useJobWebSocket hook, 
        # but a final status message is good practice.
        await websocket.send_json({"status": "complete", "final_report": state.get("final_report")})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error in WebSocket: {e}", exc_info=True)
        await websocket.send_json({"status": "error", "message": str(e)})
    finally:
        # Gracefully close the connection if it's still open
        if websocket.client_state != "DISCONNECTED":
            await websocket.close()