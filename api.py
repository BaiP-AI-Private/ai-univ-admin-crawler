import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel

import config
from main import load_university_urls, process_universities

app = FastAPI(title="University Admin Crawler API")

class CrawlStatus(BaseModel):
    """Response model for crawl status"""
    job_id: str
    status: str
    total_universities: int
    processed_universities: int = 0
    last_updated: str = ""

# In-memory storage for job status
# In a production setting, you'd use a database
active_jobs = {}

@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {"message": "University Admin Crawler API", "version": "1.0.0"}

@app.post("/crawl", response_model=CrawlStatus)
async def start_crawl(background_tasks: BackgroundTasks):
    """Start a new crawling job"""
    job_id = f"job_{len(active_jobs) + 1}_{int(asyncio.get_event_loop().time())}"
    
    # Initialize job status
    active_jobs[job_id] = {
        "job_id": job_id,
        "status": "initializing",
        "total_universities": 0,
        "processed_universities": 0,
        "last_updated": "",
        "results": []
    }
    
    # Start the crawling in the background
    background_tasks.add_task(run_crawl_job, job_id)
    
    return active_jobs[job_id]

@app.get("/crawl/{job_id}", response_model=CrawlStatus)
async def get_crawl_status(job_id: str):
    """Get status of a crawling job"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return active_jobs[job_id]

@app.get("/crawl/{job_id}/results")
async def get_crawl_results(job_id: str):
    """Get results of a completed crawling job"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if active_jobs[job_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    return {"results": active_jobs[job_id]["results"]}

async def run_crawl_job(job_id: str):
    """Run the crawling job and update status"""
    import time
    from datetime import datetime
    
    # Update job status
    active_jobs[job_id]["status"] = "loading_universities"
    active_jobs[job_id]["last_updated"] = datetime.now().isoformat()
    
    # Load university data
    universities = load_university_urls()
    
    if not universities:
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["last_updated"] = datetime.now().isoformat()
        return
    
    # Validate URLs before processing
    valid_universities = []
    for uni in universities:
        if not uni.get("url"):
            continue
            
        # Ensure URL has proper format
        url = uni["url"]
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            uni["url"] = url
            
        valid_universities.append(uni)
    
    # Update job status
    active_jobs[job_id]["status"] = "crawling"
    active_jobs[job_id]["total_universities"] = len(valid_universities)
    active_jobs[job_id]["last_updated"] = datetime.now().isoformat()
    
    # Track processing status
    results = []
    
    # Process universities in batches
    batch_size = 5
    for i in range(0, len(valid_universities), batch_size):
        batch = valid_universities[i:i+batch_size]
        
        # Process current batch
        batch_results = await process_universities(batch)
        results.extend(batch_results)
        
        # Update job status
        active_jobs[job_id]["processed_universities"] = len(results)
        active_jobs[job_id]["last_updated"] = datetime.now().isoformat()
    
    # Save results to file
    os.makedirs(config.DATA_DIR, exist_ok=True)
    output_file = f"{config.DATA_DIR}/results_{job_id}.json"
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
    except Exception as e:
        active_jobs[job_id]["status"] = "completed_with_errors"
        active_jobs[job_id]["error"] = str(e)
        active_jobs[job_id]["last_updated"] = datetime.now().isoformat()
        return
    
    # Update final job status
    active_jobs[job_id]["status"] = "completed"
    active_jobs[job_id]["results"] = results
    active_jobs[job_id]["output_file"] = output_file
    active_jobs[job_id]["last_updated"] = datetime.now().isoformat()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
