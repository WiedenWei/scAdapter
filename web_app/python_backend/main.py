import asyncio
import uuid
import os
import pathlib
from fastapi import FastAPI, UploadFile, File, Form
from typing import Dict
from contextlib import asynccontextmanager

from worker import process_job_queue

job_queue: asyncio.Queue = asyncio.Queue()
job_states: Dict[str, dict] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage background workers on server startup and shutdown."""
    os.makedirs("./data/uploads", exist_ok=True)
    os.makedirs("./data/results", exist_ok=True)
    
    worker_task = asyncio.create_task(process_job_queue(job_queue, job_states))
    yield
    worker_task.cancel()

app = FastAPI(title="scAdapter API", lifespan=lifespan)

@app.post("/api/upload")
async def create_job(
    annotation_type: str = Form(...),
    tissue_state: str = Form(...),
    tissue_type: str = Form(...),
    email: str = Form(...),
    file: UploadFile = File(...)
):
    job_id = str(uuid.uuid4())
    suffixes = "".join(pathlib.Path(file.filename).suffixes)
    if not suffixes:
        suffixes = ".csv"
    file_path = f"./data/uploads/{job_id}{suffixes}"
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    job_data = {
        "job_id": job_id,
        "email": email,
        "file_path": file_path,
        "annotation_type": annotation_type,
        "tissue_state": tissue_state,
        "tissue_type": tissue_type
    }
    
    job_states[job_id] = {"status": "Queued"}
    await job_queue.put(job_data)
    
    return {"job_id": job_id, "message": "Job successfully queued"}

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in job_states:
        return {"error": "Job not found", "status": "Failed"}
    
    position = 0
    if job_states[job_id]["status"] == "Queued":
        # Approximate queue position
        position = job_queue.qsize()
        
    return {
        "job_id": job_id,
        "status": job_states[job_id]["status"],
        "position": position
    }
