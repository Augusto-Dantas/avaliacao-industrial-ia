# Avaliação Industrial com IA

Projeto de avaliação prática com análise de dados industriais, indicadores OEE, classificação multiclasse de falhas, detecção de anomalias, API demonstrativa e pipeline experimental de visão computacional.

## Escopo

- Análise exploratória de um dataset tabular de produção industrial.
- Cálculo e interpretação de Disponibilidade, Desempenho, Qualidade e OEE.
- Classificação multiclasse com Random Forest e tratamento do desbalanceamento por pesos de classe.
- Detecção de anomalias com Isolation Forest.
- Inferência operacional e API demonstrativa em FastAPI.
- Pipeline opcional de detecção visual de defeitos em soldas com Ultralytics YOLO.
- Análise de segurança/impacto social e limites de uso.

## Requisitos

Python 3.10 ou superior. As dependências da API e da análise tabular estão em `requirements.txt`. As dependências pesadas de visão computacional ficam separadas em `requirements-vision.txt` e só precisam ser instaladas para treinar ou executar YOLO.

## Instalação e execução principal

Na raiz do repositório:

```bash
python -m venv .venv

# Linux/macOS/WSL
source .venv/bin/activate

# Windows PowerShell
# .venv\\Scripts\\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

# Coloque dataset_industrial_cibersistemas_15k.csv em data/
python src/analysis.py
python src/train.py
python src/inference.py

# Inicie a API
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Com a API em execução, abra no navegador **http://localhost:8000**. A raiz mostra os links úteis:
- `/`: informações e links da API.
- `/health`: verificação de disponibilidade.
- `/docs`: documentação interativa Swagger.
- `/redoc`: documentação ReDoc.
- `/v1/infer`: endpoint POST de inferência.
- `/v1/jobs/{job_id}`: consulta do resultado.

> `0.0.0.0` é o endereço de escuta do servidor; no navegador local, use `localhost` ou `127.0.0.1`.

## Pipeline YOLO (opcional)

O dataset de imagens **não é incluído no Git**. Antes de treinar, baixe/preencha as imagens e anotações conforme [docs/dataset_yolo.md](docs/dataset_yolo.md). O script agora valida se as pastas de treino e validação existem e contêm imagens antes de iniciar; se faltarem, informa exatamente o que preparar.

Instale primeiro a pilha visual:

```bash
# Para ambiente sem GPU NVIDIA, instale PyTorch CPU antes do restante:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements-vision.txt
```

Em ambiente com CUDA, siga a instalação de PyTorch compatível com seu driver/GPU em https://pytorch.org/get-started/locally/ e depois instale `requirements-vision.txt`.

Treinamento e inferência:

```bash
python src/train_yolo.py --data data/yolo/data.yaml --weights yolo26n.pt --epochs 100 --imgsz 640
python src/predict_yolo.py --weights runs/detect/welding-yolo/weights/best.pt --source caminho/para/imagem.jpg
```

Não execute inferência com `best.pt` antes de um treinamento concluído com sucesso. O arquivo só é criado depois que o YOLO termina o treinamento.

## Estrutura

- `src/`: análise, treinamento, inferência e API.
- `docs/`: relatório técnico, documentação da API, guia do dataset YOLO, visão computacional/ética e prompts de imagens para Gemini.
- `data/`: CSV tabular e dataset YOLO local (imagens e anotações não são versionados neste repositório).
- `models/`: artefatos produzidos pelo treinamento tabular (não versionados; gerados localmente).
- `runs/`: resultados e pesos YOLO locais (não versionados).

## Resultados e limitações

O baseline tabular usa split estratificado aleatório 75/25. Métricas observadas nesse split: balanced accuracy de 96,51% e macro-F1 de 93,94%. Esses números não demonstram generalização temporal ou por lote; faça essa validação antes de qualquer uso real. O modelo exclui OEE, seus componentes, contagens finais e rótulos auxiliares das features para reduzir vazamento.

Isolation Forest é uma ferramenta de triagem, não um diagnóstico de falha. A API é demonstrativa: a fila é mantida em memória e não oferece persistência, autenticação ou garantias de produção. O dataset tabular fornecido não contém imagens e não treina o detector YOLO. O pipeline visual só poderá ser treinado após preparar imagens e anotações; nenhum desempenho de visão computacional é alegado neste momento. Nenhuma saída comanda máquinas: a decisão humana é obrigatória.

## Licença

Consulte [LICENSE](LICENSE).
