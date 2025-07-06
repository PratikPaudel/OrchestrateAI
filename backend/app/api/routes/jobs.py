from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.graph import research_graph

router = APIRouter()

class JobRequest(BaseModel):
    query: str

@router.post("/jobs")
def create_job(request: JobRequest):
    """
    Synchronously runs the research graph for the given query and returns the final report and state.
    (For production, this should be a background job with polling, but this is a minimal working version.)
    """
    try:
        inputs = {"query": request.query}
        # Run the graph and collect all states
        states = list(research_graph.stream(inputs, stream_mode="values"))
        final_state = states[-1]
        return {
            "final_report": final_state.get("final_report"),
            "state": final_state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job failed: {e}") 