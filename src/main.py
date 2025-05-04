import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from src.observability import Observability

app = FastAPI()
observability = Observability()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Improvement Cycle Monitoring System"}

@app.get("/status")
async def get_status():
    try:
        cycle_data = observability.get_cycle_data()
        if not cycle_data:
            return JSONResponse(content={"status": "idle", "message": "No active improvement cycle."}, status_code=200)

        # Sanitize potentially sensitive data
        sanitized_cycle_data = {
            "status": cycle_data.get("status", "unknown"),
            "stage": cycle_data.get("stage", "unknown"),
            "start_time": cycle_data.get("start_time"),
            "end_time": cycle_data.get("end_time"),
            "proposal": {
                "title": cycle_data.get("proposal", {}).get("title"),
                "description": cycle_data.get("proposal", {}).get("description"),
            },
            "pull_request_url": cycle_data.get("pull_request_url"),
            "errors": cycle_data.get("errors", []),
        }

        return JSONResponse(content=sanitized_cycle_data, status_code=200)
    except Exception as e:
        logging.error(f"Error retrieving status: {e}")
        return JSONResponse(content={"status": "error", "message": f"Error retrieving status: {e}"}, status_code=500)