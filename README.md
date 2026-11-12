# Avaliação Industrial com IA

Projeto de avaliação prática com análise de dados industriais, indicadores OEE, classificação multiclasse de falhas, detecção de anomalias, API demonstrativa e proposta experimental de visão computacional para soldagem.

## Escopo

- Análise exploratória e validação de dados industriais.
- Análise de Disponibilidade, Desempenho, Qualidade e OEE.
- Classificação multiclasse e detecção de anomalias.
- API de inferência assíncrona demonstrativa.
- Pipeline experimental de visão computacional com Ultralytics YOLO.
- Documentação de proveniência, licenças, segurança, ética e limites de uso.

## Requisitos

Python 3.10 ou superior. Dependências tabulares/API em `requirements.txt`; dependências pesadas de visão em `requirements-vision.txt`.

## Instalação e execução principal

O CSV fornecido já está versionado em `Requisição/`. O código também aceita uma cópia em `data/`.

```bash
python -m venv .venv

# Linux/macOS/WSL
source .venv/bin/activate

# Windows PowerShell:
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Análise: gera reports/analysis.json
python src/analysis.py

# Treinamento: gera models/*.joblib e models/metrics.json
python src/train.py

# Inferência de exemplo
python src/inference.py

# API
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Acesse http://localhost:8000/docs. Consulte [docs/api.md](docs/api.md) para submeter e consultar trabalhos assíncronos.

## Validação e interpretação dos modelos

O treinamento prefere holdout temporal (75% inicial para treino e 25% final para teste), quando todas as classes estão presentes nos dois períodos. Se isso não for possível, registra explicitamente o fallback para split aleatório estratificado em `models/metrics.json`. O fallback não comprova generalização temporal. Mesmo o holdout temporal ainda precisa de validação independente por lote, máquina e período antes de qualquer uso operacional.

O classificador usa Random Forest com pesos por classe e imputação pela mediana. O Isolation Forest é ajustado somente com registros rotulados como `Sem Falha`. Identificadores, timestamp, rótulo, indicadores OEE e quantidades finais são excluídos das features para reduzir vazamento de informação.

A análise gera `reports/analysis.json` com qualidade básica dos dados, período, distribuição das classes, correlações de Pearson com OEE e, quando existem os numeradores necessários, componentes que podem ser reconstruídos. Desempenho só pode ser recalculado quando houver ciclo ideal/produção teórica disponível; não se deve inventar esse dado.

## Visão computacional: limites importantes

O CSV industrial é tabular e não contém imagens. O conjunto YOLO auxiliar disponível é genérico e suas classes não comprovam detecção específica de porosidade nem medição termográfica de HAZ. A documentação em [docs/visao_computacional_etica.md](docs/visao_computacional_etica.md) é uma proposta técnica, não evidência de um modelo específico de porosidade/HAZ treinado e validado. Para validar essa capacidade, são necessários frames RGB e termográficos representativos, metadados de calibração e rótulos revisados por especialistas.

## Instalação automatizada dos datasets YOLO

Com a virtualenv ativada:

```bash
python src/setup_yolo.py
```

Para preparar e iniciar o treino:

```bash
python src/setup_yolo.py --train --epochs 50 --imgsz 640 --device cpu
```

O instalador mantém fontes isoladas e registra proveniência/licenças em `data/yolo/datasets-manifest.json`. O limite combinado padrão é 25 GiB. Algumas fontes exigem acesso e aprovação manual no Hugging Face; o script não contorna essas restrições. Consulte [docs/dataset_yolo.md](docs/dataset_yolo.md) antes de redistribuir dados.

Os pesos ficam em `runs/detect/welding-yolo/weights/`. Inferência:

```bash
python src/predict_yolo.py --weights runs/detect/welding-yolo/weights/best.pt --source caminho/para/imagem.jpg
```

Use `requirements-vision.txt` apenas para a etapa visual; ela não é necessária para análise tabular, treinamento Random Forest ou API.

## Estrutura

- `src/`: análise, treinamento, preparação de datasets, inferência e API.
- `docs/`: relatório técnico, contrato da API, proveniência dos datasets e proposta de visão computacional/ética.
- `Requisição/`: enunciado e dataset original da avaliação.
- `data/`: dados visuais locais, não versionados.
- `models/`: artefatos tabulares gerados localmente.
- `reports/`: relatórios de análise gerados localmente.
- `runs/`: resultados e pesos YOLO locais.

## Segurança, ética e limitações

- Resultados de IA são apoio à decisão; inspeção/liberação de peças exige supervisão humana.
- Não usar o sistema para vigilância ou avaliação individual de trabalhadores.
- Dados ausentes, câmera sem calibração ou modelo indisponível devem resultar em inspeção alternativa/estado indeterminado.
- Não conectar a saída experimental diretamente a CLP/atuadores sem análise de risco e validação independente.
- A API usa fila em memória demonstrativa; não é adequada para produção.
- Métricas de holdout não substituem validação externa por lote e período.

## Licença

Consulte [LICENSE](LICENSE) e as licenças individuais de cada dataset antes de redistribuir, publicar ou usar comercialmente os dados.
