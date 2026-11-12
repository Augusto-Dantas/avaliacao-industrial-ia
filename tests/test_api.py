from fastapi.testclient import TestClient

from src import api


def test_health_endpoint():
    client = TestClient(api.app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_inference_job_lifecycle(monkeypatch):
    monkeypatch.setattr(
        api, "infer",
        lambda payload: {
            "classe_prevista": "Sem Falha",
            "confianca": 0.99,
            "anomalia": False,
            "automatic_machine_action": False,
        },
    )
    client = TestClient(api.app)
    payload = {
        "temperatura_solda_c": 217,
        "corrente_solda_a": 164,
        "tensao_solda_v": 24,
        "pressao_gas_bar": 4.5,
        "vibracao_mm_s": 1.1,
        "velocidade_linha_m_min": 12,
        "area_porosidade_px": 2,
        "temperatura_max_haz_c": 226,
    }

    submitted = client.post("/v1/infer", json=payload)
    assert submitted.status_code == 202
    job_id = submitted.json()["job_id"]

    result = client.get(f"/v1/jobs/{job_id}")
    assert result.status_code == 200
    assert result.json()["status"] == "completed"
    assert result.json()["result"]["classe_prevista"] == "Sem Falha"


def test_inference_rejects_unexpected_fields():
    client = TestClient(api.app)
    response = client.post(
        "/v1/infer",
        json={
            "temperatura_solda_c": 217,
            "corrente_solda_a": 164,
            "tensao_solda_v": 24,
            "pressao_gas_bar": 4.5,
            "vibracao_mm_s": 1.1,
            "velocidade_linha_m_min": 12,
            "area_porosidade_px": 2,
            "temperatura_max_haz_c": 226,
            "unexpected": True,
        },
    )

    assert response.status_code == 422


def test_unknown_job_returns_404():
    client = TestClient(api.app)
    response = client.get("/v1/jobs/not-a-real-job")

    assert response.status_code == 404
