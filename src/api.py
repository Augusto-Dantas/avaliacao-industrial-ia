from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from src.inference import infer

app = FastAPI(
    title="Industrial AI",
    version="1.1.0",
    description=(
        "API demonstrativa com submissão assíncrona de inferência. "
        "Resultados exigem revisão humana."
    ),
)
jobs: dict[str, dict] = {}
jobs_lock = Lock()


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    temperatura_solda_c: float = Field(ge=0, le=3000)
    corrente_solda_a: float = Field(ge=0, le=10000)
    tensao_solda_v: float = Field(ge=0, le=1000)
    pressao_gas_bar: float = Field(ge=0, le=100)
    vibracao_mm_s: float = Field(ge=0, le=1000)
    velocidade_linha_m_min: float = Field(ge=0, le=1000)
    area_porosidade_px: float = Field(ge=0)
    temperatura_max_haz_c: float = Field(ge=0, le=3000)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def execute_job(job_id: str, payload: dict) -> None:
    try:
        result = infer(payload)
        with jobs_lock:
            jobs[job_id].update(
                status="completed", result=result, completed_at=utc_now()
            )
    except Exception as exc:
        # Keep client response generic; detailed exception belongs in server logs.
        with jobs_lock:
            jobs[job_id].update(
                status="failed",
                error="inference_failed",
                completed_at=utc_now(),
            )
        print(f"Inference job {job_id} failed: {exc}")


@app.get("/", tags=["status"])
async def root():
    return {
        "service": "Industrial AI API",
        "status": "ok",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "inference": "/v1/infer",
    }


@app.get("/health", tags=["status"])
async def health():
    return {"status": "ok"}


@app.post("/v1/infer", status_code=202, tags=["inference"])
async def submit(payload: Payload, background_tasks: BackgroundTasks):
    job_id = str(uuid4())
    with jobs_lock:
        jobs[job_id] = {
            "status": "pending",
            "created_at": utc_now(),
            "result": None,
        }
    background_tasks.add_task(execute_job, job_id, payload.model_dump())
    return {
        "job_id": job_id,
        "status": "accepted",
        "status_url": f"/v1/jobs/{job_id}",
        "result_url": f"/v1/jobs/{job_id}",
    }


@app.get("/v1/jobs/{job_id}", tags=["inference"])
async def get_job(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="job not found")
        return {"job_id": job_id, **job}
