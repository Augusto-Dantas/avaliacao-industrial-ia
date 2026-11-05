# Avaliação Industrial com IA

Projeto de avaliação prática com análise de dados industriais, indicadores OEE, classificação multiclasse de falhas, detecção de anomalias, API demonstrativa e proposta de visão computacional com considerações éticas.

## Escopo

- Análise exploratória de um dataset tabular de produção industrial.
- Cálculo e interpretação de Disponibilidade, Desempenho, Qualidade e OEE.
- Classificação multiclasse com Random Forest e tratamento do desbalanceamento por pesos de classe.
- Detecção de anomalias com Isolation Forest.
- Inferência operacional e API demonstrativa em FastAPI.
- Proposta conceitual de visão computacional e análise de segurança/impacto social.

## Requisitos

Python 3.10 ou superior.

## Execução local

Coloque o arquivo fornecido `dataset_industrial_cibersistemas_15k.csv` em `data/`, então execute:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/analysis.py
python src/train.py
python src/inference.py
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Endpoints: `GET /health`, `POST /v1/infer` (retorna HTTP 202 e `job_id`) e `GET /v1/jobs/{job_id}`.

## Estrutura

- `src/`: análise, treinamento, inferência e API.
- `docs/`: relatório técnico, API, visão computacional/ética e prompts de imagens para Gemini.
- `data/`: diretório esperado para o CSV de entrada (o dataset não está versionado neste repositório).
- `models/`: artefatos produzidos pelo treinamento (não versionados; gerados localmente).

## Resultados e limitações

O baseline usa split estratificado aleatório 75/25. Métricas observadas nesse split: balanced accuracy de 96,51% e macro-F1 de 93,94%. Esses números não demonstram generalização temporal ou por lote; faça essa validação antes de qualquer uso real. O modelo exclui OEE, seus componentes, contagens finais e rótulos auxiliares das features para reduzir vazamento.

Isolation Forest é uma ferramenta de triagem, não um diagnóstico de falha. A API é demonstrativa: a fila é mantida em memória e não oferece persistência, autenticação ou garantias de produção. O dataset fornecido é tabular e não contém imagens; portanto, visão computacional é proposta conceitual e não um modelo treinado neste estudo. Nenhuma saída comanda máquinas: a decisão humana é obrigatória.

## Imagens para documentação

O arquivo [docs/prompts_gemini_imagens.md](docs/prompts_gemini_imagens.md) contém prompts prontos para gerar capa, diagramas, mockups e imagens conceituais no Gemini. Identifique imagens ilustrativas como tais e não as apresente como evidência experimental.

## Licença

Consulte [LICENSE](LICENSE).
