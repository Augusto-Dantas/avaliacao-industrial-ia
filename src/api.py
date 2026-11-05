from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.inference import infer


app = FastAPI(
    title="Industrial AI",
    version="1.0.1",
    description="API demonstrativa para inferência de falhas industriais.",
)
jobs: dict[str, dict] = {}


class Payload(BaseModel):
    temperatura_solda_c: float
    corrente_solda_a: float
    tensao_solda_v: float
    pressao_gas_bar: float
    vibracao_mm_s: float
    velocidade_linha_m_min: float
    area_porosidade_px: float
    temperatura_max_haz_c: float


@app.get("/", tags=["status"])
async def root():
    """Página inicial com links para a documentação e verificações da API."""
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
async def submit(payload: Payload):
    job_id = str(uuid4())
    jobs[job_id] = {
        "status": "completed",
        "result": infer(payload.model_dump()),
    }
    return {
        "job_id": job_id,
        "status": "accepted",
        "result_url": f"/v1/jobs/{job_id}",
    }


@app.get("/v1/jobs/{job_id}", tags=["inference"])
async def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="job not found")
    return {"job_id": job_id, **jobs[job_id]}
