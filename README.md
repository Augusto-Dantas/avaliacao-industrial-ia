# Avaliação Industrial com IA

Projeto de avaliação prática com análise de dados industriais, indicadores OEE, classificação multiclasse de falhas, detecção de anomalias, API demonstrativa e proposta de visão computacional com considerações éticas.

## Escopo

- Análise exploratória de um dataset tabular de produção industrial.
- Cálculo e interpretação de Disponibilidade, Desempenho, Qualidade e OEE.
- Classificação multiclasse com Random Forest e tratamento do desbalanceamento por pesos de classe.
- Detecção de anomalias com Isolation Forest.
- Inferência operacional e API demonstrativa em FastAPI.
- Detecção visual experimental de defeitos em soldas com Ultralytics YOLO (dataset híbrido real + sintético, documentado separadamente).
- Análise de segurança/impacto social e limites de uso.

## Requisitos

Python 3.10 ou superior. Para o detector YOLO, instale também as dependências incluídas em `requirements.txt`.

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
# Detector YOLO (prepare antes o dataset conforme docs/dataset_yolo.md)
python src/train_yolo.py --data data/yolo/data.yaml --weights yolo26n.pt --epochs 100 --imgsz 640
# Inferência em uma imagem após o treinamento
python src/predict_yolo.py --weights runs/detect/welding-yolo/weights/best.pt --source caminho/para/imagem.jpg
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Endpoints: `GET /health`, `POST /v1/infer` (retorna HTTP 202 e `job_id`) e `GET /v1/jobs/{job_id}`.

## Estrutura

- `src/`: análise, treinamento, inferência e API.
- `docs/`: relatório técnico, API, guia do dataset YOLO híbrido, visão computacional/ética e prompts de imagens para Gemini.
- `data/`: CSV tabular e dataset YOLO local (imagens e anotações não são versionados neste repositório).
- `models/`: artefatos produzidos pelo treinamento (não versionados; gerados localmente).

## Resultados e limitações

O baseline usa split estratificado aleatório 75/25. Métricas observadas nesse split: balanced accuracy de 96,51% e macro-F1 de 93,94%. Esses números não demonstram generalização temporal ou por lote; faça essa validação antes de qualquer uso real. O modelo exclui OEE, seus componentes, contagens finais e rótulos auxiliares das features para reduzir vazamento.

Isolation Forest é uma ferramenta de triagem, não um diagnóstico de falha. A API é demonstrativa: a fila é mantida em memória e não oferece persistência, autenticação ou garantias de produção. O dataset tabular fornecido não contém imagens e não treina o detector YOLO. O pipeline visual foi adicionado, mas só poderá ser treinado após preparar imagens e anotações conforme `docs/dataset_yolo.md`; nenhum desempenho de visão computacional é alegado neste momento. Nenhuma saída comanda máquinas: a decisão humana é obrigatória.

## Imagens para documentação

O arquivo [docs/prompts_gemini_imagens.md](docs/prompts_gemini_imagens.md) contém prompts prontos para gerar capa, diagramas, mockups e imagens conceituais no Gemini. Identifique imagens ilustrativas como tais e não as apresente como evidência experimental.

## Licença

Consulte [LICENSE](LICENSE).
