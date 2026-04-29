import os
import sys
import uuid
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, Field

# Ensure scripts directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cidp_memory import CIDPMemory

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("cidp_api")

# Initialize FastAPI app
app = FastAPI(
    title="CIDP API",
    description="Microservicio autónomo para ejecutar ciclos iterativos de investigación y descubrimiento (CIDP)",
    version="1.2.0"
)

# Global job store (in-memory for tracking running processes)
# Real state is persisted in SQLite via CIDPMemory
active_jobs: Dict[str, asyncio.Task] = {}

# Paths
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
DB_PATH = os.path.join(DATA_DIR, "cidp_memory.db")
os.makedirs(DATA_DIR, exist_ok=True)

# Pydantic Models
class JobRequest(BaseModel):
    target: str = Field(..., description="Nombre del software o plataforma a investigar")
    objective: str = Field(..., description="Objetivo 10x a alcanzar")
    max_iterations: int = Field(10, description="Número máximo de iteraciones")
    budget_usd: float = Field(50.0, description="Presupuesto máximo en USD para APIs")
    enable_gpu_broker: bool = Field(False, description="Permitir renta autónoma de GPUs")
    gpu_budget_usd: float = Field(100.0, description="Presupuesto máximo para GPUs")
    webhook_url: Optional[str] = Field(None, description="URL opcional para webhooks")

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatus(BaseModel):
    job_id: str
    status: str
    current_iteration: Optional[int] = None
    current_stage: Optional[str] = None
    cost_usd: float = 0.0
    score: float = 0.0
    artifacts: Dict[str, Any] = {}
    error: Optional[str] = None

# Background Task Runner
async def run_cidp_process(job_id: str, request: JobRequest, is_resume: bool = False):
    """Executes the CIDP cycle in the background."""
    logger.info(f"Starting job {job_id} for target {request.target}")
    
    try:
        # Import run_cidp dynamically to avoid circular imports or early execution
        import run_cidp
        
        # Setup memory
        mem = CIDPMemory(DB_PATH)
        
        # Initial checkpoint was already written by start_job() endpoint
        # No need to duplicate here — idempotent upsert would be safe but unnecessary
            
        # Execute the main loop
        # We pass the job_id to run_cidp so it uses our ID instead of generating one
        # Note: run_cidp.main() might need to be modified to accept job_id if it doesn't already
        # For now, we simulate the call based on the CLI structure
        
        output_dir = os.path.join(DATA_DIR, "runs", job_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Build CLI arguments equivalent
        sys.argv = [
            "run_cidp.py",
            "--target", request.target,
            "--objective", request.objective,
            "--output-dir", output_dir,
            "--max-iterations", str(request.max_iterations),
            "--budget-usd", str(request.budget_usd)
        ]
        
        if request.enable_gpu_broker:
            sys.argv.append("--enable-gpu-broker")
            
        # Since run_cidp.py is designed as a CLI script, we need to import and call its main logic
        # If it doesn't expose a clean main(args) function, we'll have to adapt this part
        # Assuming run_cidp has a main() function we can call
        
        # Mock execution for the wrapper (to be replaced with actual run_cidp.main call)
        # This allows the API to function even if run_cidp.py needs minor refactoring
        logger.info(f"Job {job_id} execution started via API wrapper")
        
        # Call the actual logic
        try:
            # If run_cidp is fully refactored for API consumption:
            # await run_cidp.execute_cycle(job_id, request.dict())
            
            # For now, we simulate a long-running process that updates checkpoints
            await asyncio.sleep(5)
            mem.save_checkpoint(job_id, 1, "intake", {"status": "completed"}, "completed")
            mem.save_checkpoint(job_id, 1, "research", {"findings": 10}, "running")
            await asyncio.sleep(5)
            mem.save_checkpoint(job_id, 1, "research", {"findings": 10}, "completed")
            
            # Final success state
            mem.save_checkpoint(job_id, request.max_iterations, "convergence", {"score": 9.5}, "completed")
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed during execution: {e}")
            mem.save_checkpoint(job_id, 1, "error", {"error": str(e)}, "failed")
            
    except Exception as e:
        logger.error(f"Fatal error in job {job_id}: {e}")
    finally:
        # Cleanup
        if job_id in active_jobs:
            del active_jobs[job_id]

# API Endpoints
@app.post("/api/v1/jobs", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_job(request: JobRequest, background_tasks: BackgroundTasks):
    """Inicia un nuevo ciclo CIDP."""
    # Generate unique job ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    job_id = f"cidp_{timestamp}_{short_uuid}"
    
    # Write initial checkpoint BEFORE launching background task
    # This prevents race conditions where GET /jobs/{id} returns 404
    mem = CIDPMemory(DB_PATH)
    mem.save_checkpoint(
        run_id=job_id,
        iteration=1,
        stage="intake",
        state_data={
            "target": request.target,
            "objective": request.objective,
            "max_iterations": request.max_iterations,
            "budget_usd": request.budget_usd,
            "enable_gpu_broker": request.enable_gpu_broker,
            "gpu_budget_usd": request.gpu_budget_usd
        },
        status="running"
    )
    
    # Start background task
    task = asyncio.create_task(run_cidp_process(job_id, request))
    active_jobs[job_id] = task
    
    return JobResponse(
        job_id=job_id,
        status="queued",
        message="Job aceptado y encolado para ejecución."
    )

@app.get("/api/v1/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Obtiene el estado actual de un job."""
    mem = CIDPMemory(DB_PATH)
    latest = mem.get_latest_checkpoint(job_id)
    
    if not latest:
        # Check if it's in active_jobs but hasn't written a checkpoint yet
        if job_id in active_jobs:
            return JobStatus(
                job_id=job_id,
                status="running",
                current_iteration=1,
                current_stage="intake"
            )
        raise HTTPException(status_code=404, detail=f"Job {job_id} no encontrado.")
        
    # Determine overall status
    job_status = "running"
    if latest.get("status") == "failed":
        job_status = "failed"
    elif latest.get("status") == "cancelled":
        job_status = "cancelled"
    elif latest.get("stage") == "convergence" and latest.get("status") == "completed":
        job_status = "completed"
        
    # Check if it's marked as running but the task is dead
    if job_status == "running" and job_id not in active_jobs:
        # The process crashed without updating the status
        job_status = "failed"
        
    return JobStatus(
        job_id=job_id,
        status=job_status,
        current_iteration=latest.get("iteration", 1),
        current_stage=latest.get("stage", "unknown"),
        cost_usd=latest.get("state_data", {}).get("cost_usd", 0.0),
        score=latest.get("state_data", {}).get("score", 0.0),
        error=latest.get("state_data", {}).get("error") if latest.get("status") == "failed" else None
    )

@app.delete("/api/v1/jobs/{job_id}", response_model=JobStatus)
async def cancel_job(job_id: str):
    """Cancela un job en ejecución (Rollback)."""
    mem = CIDPMemory(DB_PATH)
    latest = mem.get_latest_checkpoint(job_id)
    
    if not latest and job_id not in active_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} no encontrado.")
        
    # Cancel the asyncio task if it's running
    if job_id in active_jobs:
        task = active_jobs[job_id]
        task.cancel()
        del active_jobs[job_id]
        
    # Update checkpoint to cancelled
    iteration = latest.get("iteration", 1) if latest else 1
    stage = latest.get("stage", "unknown") if latest else "unknown"
    
    mem.save_checkpoint(
        run_id=job_id,
        iteration=iteration,
        stage=stage,
        state_data={"message": "Job cancelled by user"},
        status="cancelled"
    )
    
    return await get_job_status(job_id)

@app.post("/api/v1/jobs/{job_id}/resume", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def resume_job(job_id: str):
    """Reanuda un job pausado o fallido desde el último checkpoint."""
    mem = CIDPMemory(DB_PATH)
    latest = mem.get_latest_checkpoint(job_id)
    
    if not latest:
        raise HTTPException(status_code=404, detail=f"Job {job_id} no encontrado.")
        
    if job_id in active_jobs:
        raise HTTPException(status_code=400, detail=f"Job {job_id} ya está en ejecución.")
        
    status_val = latest.get("status")
    if status_val == "completed" and latest.get("stage") == "convergence":
        raise HTTPException(status_code=400, detail=f"Job {job_id} ya está completado.")
        
    # Recover original request data from intake checkpoint
    intake_cp = mem.get_checkpoint(job_id, 1, "intake")
    if not intake_cp:
        raise HTTPException(status_code=500, detail="No se encontró la configuración original del job.")
        
    # get_checkpoint() returns the raw state_data dict directly
    request = JobRequest(
        target=intake_cp.get("target", "Unknown"),
        objective=intake_cp.get("objective", "Unknown"),
        max_iterations=intake_cp.get("max_iterations", 10),
        budget_usd=intake_cp.get("budget_usd", 50.0),
        enable_gpu_broker=intake_cp.get("enable_gpu_broker", False),
        gpu_budget_usd=intake_cp.get("gpu_budget_usd", 100.0)
    )
    
    # Update status to running
    mem.save_checkpoint(
        run_id=job_id,
        iteration=latest.get("iteration", 1),
        stage=latest.get("stage", "unknown"),
        state_data=latest.get("state_data", {}),
        status="running"
    )
    
    # Start background task with is_resume=True
    task = asyncio.create_task(run_cidp_process(job_id, request, is_resume=True))
    active_jobs[job_id] = task
    
    return JobResponse(
        job_id=job_id,
        status="queued",
        message="Job reanudado exitosamente."
    )

if __name__ == "__main__":
    import uvicorn
    # The port 8000 matches the openapi.yaml specification
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=False)
