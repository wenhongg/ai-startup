"""
Main entry point for the AI Startup Self-Improvement System.
"""

import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn
from src.orchestrator import SystemOrchestrator
from src.rate_limits import rate_limiter
from src.config import settings

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

async def main():
    """Run the AI startup system."""
    try:
        # Initialize the orchestrator
        orchestrator = SystemOrchestrator()
        
        # Run improvement cycles
        while True:
            try:
                # Run a single improvement cycle
                orchestrator.run_improvement_cycle()
                
                # Clean up rate limiter
                rate_limiter.cleanup()
                
                # Wait before next cycle
                await asyncio.sleep(60 * 60 * 24)  # 1 day between cycles
                
            except Exception as e:
                logger.error(f"Error in improvement cycle: {e}")
                await asyncio.sleep(300)  # 5 minutes before retry
                
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

@app.get("/")
async def root():
    return {"message": "AI Self-Improvement System is running"}

@app.post("/improve")
async def run_improvement_cycle():
    """
    Trigger a single improvement cycle
    """
    try:
        result = orchestrator.improvement_cycle()
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
    asyncio.run(main()) 