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

Python 3.10 ou superior. As dependências da API e da análise tabular estão em `requirements.txt`. As dependências pesadas de visão computacional ficam separadas em `requirements-vision.txt`.

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

Com a API em execução, abra **http://localhost:8000**. A raiz mostra os links úteis: `/health`, `/docs`, `/redoc`, `/v1/infer` e `/v1/jobs/{job_id}`.

> `0.0.0.0` é o endereço de escuta do servidor; no navegador local, use `localhost` ou `127.0.0.1`.

## YOLO: instalação automatizada

O pipeline visual agora pode preparar tudo automaticamente. Na raiz do repositório, com a virtualenv ativada, execute:

```bash
python src/setup_yolo.py --train
```

Esse comando:

1. Mantém uma instalação PyTorch funcional; se PyTorch estiver ausente/quebrado, instala a versão CPU para evitar baixar pacotes CUDA desnecessários.
2. Instala Ultralytics e Hugging Face Hub.
3. Baixa o dataset público `rikkarth/welding-defect-object-detection` (aproximadamente 104 MB).
4. Converte a estrutura `train/valid/test` do download para `data/yolo/images` e `data/yolo/labels`.
5. Gera `data/yolo/data.yaml` com as classes `bad_weld`, `good_weld` e `defect`.
6. Inicia o treinamento com `yolo26n.pt`, 100 épocas, 640 px, batch 8 e CPU.

O primeiro download pode demorar. O dataset fica em `data/yolo/.download/`; imagens, labels, pesos e resultados continuam locais e não são enviados ao Git.

Para somente instalar as dependências e preparar o dataset, sem treinar:

```bash
python src/setup_yolo.py
```

Para usar GPU NVIDIA, caso o PyTorch CUDA já esteja corretamente instalado no ambiente:

```bash
python src/setup_yolo.py --train --device 0
```

Para ajustar o treinamento:

```bash
python src/setup_yolo.py --train --epochs 100 --imgsz 640 --batch 8 --device cpu
```

Se quiser substituir um dataset local já preparado e baixar uma cópia nova, use `--force`. Isso remove somente `data/yolo/images` e `data/yolo/labels` gerados localmente, além do cache baixado.

Após o treinamento, execute a inferência em uma imagem sua:

```bash
python src/predict_yolo.py --weights runs/detect/welding-yolo/weights/best.pt --source caminho/para/imagem.jpg
```

O dataset do Hugging Face informa 2.028 imagens anotadas, três classes e licença CC0. A classe genérica `defect` não deve ser interpretada automaticamente como porosidade ou causa específica. Consulte [docs/dataset_yolo.md](docs/dataset_yolo.md) para limitações, fontes e critérios de avaliação.

## Estrutura

- `src/`: análise, treinamento, preparação automática do YOLO, inferência e API.
- `docs/`: relatório técnico, documentação da API, guia do dataset YOLO e notas éticas.
- `data/`: CSV tabular e dataset YOLO local (imagens e anotações não são versionados).
- `models/`: artefatos produzidos pelo treinamento tabular.
- `runs/`: resultados e pesos YOLO locais.

## Resultados e limitações

O baseline tabular usa split estratificado aleatório 75/25. Métricas observadas nesse split: balanced accuracy de 96,51% e macro-F1 de 93,94%. Esses números não demonstram generalização temporal ou por lote; faça essa validação antes de qualquer uso real. O modelo exclui OEE, seus componentes, contagens finais e rótulos auxiliares das features para reduzir vazamento.

Isolation Forest é uma ferramenta de triagem, não um diagnóstico de falha. A API é demonstrativa: a fila é mantida em memória e não oferece persistência, autenticação ou garantias de produção. O dataset tabular não contém imagens e não treina o detector YOLO. Nenhuma saída comanda máquinas: a decisão humana é obrigatória.

## Licença

Consulte [LICENSE](LICENSE).
