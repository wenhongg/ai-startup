from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn
from .orchestrator import SystemOrchestrator
from .config import settings

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Self-Improvement System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = SystemOrchestrator()

@app.get("/")
async def root():
    return {"message": "AI Self-Improvement System is running"}

@app.post("/improve")
async def run_improvement_cycle():
    """
    Trigger a single improvement cycle
    """
    try:
        result = await orchestrator.improvement_cycle()
        if result:
            return {
                "status": "success",
                "message": "Improvement cycle completed successfully",
                "details": result
            }
        else:
            return {
                "status": "failed",
                "message": "Improvement cycle failed or was aborted"
            }
    except Exception as e:
        logger.error(f"Error in improvement cycle: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.environment == "development" else False
    ) 