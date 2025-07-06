from fastapi import FastAPI
from .api.routes.jobs import router as api_router
from dotenv import load_dotenv
import os

# Load environment variables and debug
load_dotenv()
print(f"EXA_API_KEY loaded: {bool(os.getenv('EXA_API_KEY'))}")
print(f"OPENAI_API_KEY loaded: {bool(os.getenv('OPENAI_API_KEY'))}")

app = FastAPI()

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "OrchestrateAI backend is running. API endpoints coming soon."}

@app.get("/debug/env")
def debug_env():
    return {
        "exa_key_set": bool(os.getenv("EXA_API_KEY")),
        "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "exa_key_preview": os.getenv("EXA_API_KEY")[:10] + "..." if os.getenv("EXA_API_KEY") else "Not set",
        "openai_key_preview": os.getenv("OPENAI_API_KEY")[:10] + "..." if os.getenv("OPENAI_API_KEY") else "Not set"
    }