from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes.jobs import router as jobs_router
from .api.ws.jobs import router as ws_router
from .utils.logger import logger

app = FastAPI(title="OrchestrateAI Research API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs_router, prefix="/api/v1", tags=["jobs"])
app.include_router(ws_router, prefix="/api/v1", tags=["websocket"])

@app.get("/")
async def root():
    return {"message": "OrchestrateAI Research API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)