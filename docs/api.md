# API demonstrativa

- `GET /health`: verifica disponibilidade do serviço.
- `POST /v1/infer`: recebe oito sinais numéricos e retorna HTTP 202 com `job_id`.
- `GET /v1/jobs/{job_id}`: consulta o resultado.

Exemplo de payload:

```json
{
  "temperatura_solda_c": 217,
  "corrente_solda_a": 164,
  "tensao_solda_v": 24,
  "pressao_gas_bar": 4.5,
  "vibracao_mm_s": 1.1,
  "velocidade_linha_m_min": 12,
  "area_porosidade_px": 2,
  "temperatura_max_haz_c": 226
}
```

Contrato ilustrativo, pois não foi anexada especificação oficial. A implementação usa armazenamento em memória e é apenas demonstrativa.
