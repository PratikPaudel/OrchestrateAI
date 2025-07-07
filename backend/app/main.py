from fastapi import FastAPI
from pathlib import Path
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from app.api.ws.jobs import router as ws_router  

# Load environment variables with explicit debugging
load_dotenv()

# Additional debug output that matches your original code
print(f"EXA_API_KEY loaded: {bool(os.getenv('EXA_API_KEY'))}")
print(f"OPENAI_API_KEY loaded: {bool(os.getenv('OPENAI_API_KEY'))}")
print(f"GEMINI_API_KEY loaded: {bool(os.getenv('GEMINI_API_KEY'))}")
print(f"GROQ_API_KEY loaded: {bool(os.getenv('GROQ_API_KEY'))}")

# Now try to import the modules that are failing
print("\nAttempting to import modules...")
try:
    from app.api.routes.jobs import router as api_router
    print("✅ Successfully imported api_router")
except Exception as e:
    print(f"❌ Failed to import api_router: {e}")
    print("This is where the error is occurring!")

try:
    from app.core.graph import research_graph
    print("✅ Successfully imported research_graph")
except Exception as e:
    print(f"❌ Failed to import research_graph: {e}")

app = FastAPI()

# Only add router if it was successfully imported
try:
    app.include_router(api_router, prefix="/api/v1")
    app.include_router(ws_router, prefix="/api/v1")
    print("✅ Successfully added api_router to app")
except NameError:
    print("❌ api_router not available, skipping router addition")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "OrchestrateAI backend is running. API endpoints coming soon."}

@app.get("/debug/env")
def debug_env():
    return {
        "exa_key_set": bool(os.getenv("EXA_API_KEY")),
        "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "exa_key_preview": os.getenv("EXA_API_KEY")[:2] + "..." if os.getenv("EXA_API_KEY") else "Not set",
        "openai_key_preview": os.getenv("OPENAI_API_KEY")[:2] + "..." if os.getenv("OPENAI_API_KEY") else "Not set",
        "gemini_key_preview": os.getenv("GEMINI_API_KEY")[:2] + "..." if os.getenv("GEMINI_API_KEY") else "Not set",
        "groq_key_preview": os.getenv("GROQ_API_KEY")[:2] + "..." if os.getenv("GROQ_API_KEY") else "Not set"
    }