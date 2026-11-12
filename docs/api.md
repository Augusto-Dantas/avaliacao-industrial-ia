# API demonstrativa

Inicie o servidor a partir da raiz do repositório:

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Abra **http://localhost:8000** no navegador (não use `0.0.0.0` como endereço de destino).

- `GET /`: informações do serviço.
- `GET /health`: disponibilidade do serviço.
- `GET /docs`: documentação interativa Swagger.
- `GET /redoc`: documentação ReDoc.
- `POST /v1/infer`: valida os oito sinais, cria um trabalho em segundo plano e responde HTTP 202 com `job_id`.
- `GET /v1/jobs/{job_id}`: consulta `pending`, `completed` ou `failed` e, quando concluído, o resultado.

Exemplo de submissão:

```bash
curl -X POST http://localhost:8000/v1/infer \
  -H "Content-Type: application/json" \
  -d '{
    "temperatura_solda_c": 217,
    "corrente_solda_a": 164,
    "tensao_solda_v": 24,
    "pressao_gas_bar": 4.5,
    "vibracao_mm_s": 1.1,
    "velocidade_linha_m_min": 12,
    "area_porosidade_px": 2,
    "temperatura_max_haz_c": 226
  }'
```

A resposta contém `job_id`. Consulte o trabalho até o estado deixar de ser `pending`:

```bash
curl http://localhost:8000/v1/jobs/SEU_JOB_ID
```

O resultado inclui classe prevista, probabilidades, sinalizador de anomalia e ação sugerida. A saída é apoio à decisão e não comanda máquina/CLP.

**Limitações:** a execução em segundo plano usa `BackgroundTasks` e o estado dos trabalhos fica em memória. Reiniciar o processo perde os trabalhos; múltiplos workers não compartilham o estado. Isso demonstra o ciclo assíncrono, mas não substitui uma fila durável. Para produção, usar broker/fila e armazenamento compartilhado, autenticação, TLS, controle de acesso, idempotência, observabilidade, versionamento e validação de segurança.

O contrato é ilustrativo: não foi fornecida uma especificação oficial da API no conjunto de anexos.
