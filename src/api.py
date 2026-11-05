from uuid import uuid4
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.inference import infer

app = FastAPI(title="Industrial AI", version="1.0")
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

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/v1/infer", status_code=202)
async def submit(payload: Payload):
    job_id = str(uuid4())
    jobs[job_id] = {"status": "completed", "result": infer(payload.model_dump())}
    return {"job_id": job_id, "status": "accepted", "result_url": f"/v1/jobs/{job_id}"}

@app.get("/v1/jobs/{job_id}")
async def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "job not found")
    return {"job_id": job_id, **jobs[job_id]}
