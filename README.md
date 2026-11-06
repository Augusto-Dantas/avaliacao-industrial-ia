# Avaliação Industrial com IA

Projeto de avaliação prática com análise de dados industriais, indicadores OEE, classificação multiclasse de falhas, detecção de anomalias, API demonstrativa e pipeline experimental de visão computacional para soldagem.

## Escopo

- Análise exploratória de dataset tabular de produção industrial.
- Cálculo e interpretação de Disponibilidade, Desempenho, Qualidade e OEE.
- Classificação multiclasse e detecção de anomalias.
- API demonstrativa em FastAPI.
- Detecção visual experimental com Ultralytics YOLO.
- Preparação automatizada de múltiplos datasets públicos de soldagem, com limite total configurável de download (padrão: 25 GB).
- Documentação de proveniência, licenças, segurança e limites de uso.

## Requisitos

Python 3.10 ou superior. As dependências tabulares/API estão em `requirements.txt`; as dependências pesadas de visão ficam em `requirements-vision.txt`.

## Instalação principal

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

# API
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Abra http://localhost:8000, /docs, /redoc ou /health.

## Instalação automatizada dos datasets YOLO

Com a virtualenv ativada, execute na raiz:

```bash
python src/setup_yolo.py --train
```

O instalador:
1. Mantém PyTorch funcional ou instala a build CPU caso esteja ausente/quebrada.
2. Instala Ultralytics e Hugging Face Hub.
3. Consulta os tamanhos dos repositórios e aplica limite combinado padrão de 25 GiB.
4. Baixa as três fontes públicas catalogadas: `rikkarth/welding-defect-object-detection`, `AI4Manufacturing/217`, `AI4Manufacturing/218`, `AI4Manufacturing/105` e `AI4Manufacturing/219` (as duas últimas exigem liberação manual).
5. Mantém cada fonte isolada e registra tamanho, licença e caminho em `data/yolo/datasets-manifest.json`.
6. Prepara para o detector atual somente a fonte CC0 com anotações YOLO nativas.
7. Com `--train`, inicia o treinamento após a preparação; salva `last.pt` e `best.pt` e checkpoints periódicos para retomada.

Para apenas baixar/preparar, sem treinar:

```bash
python src/setup_yolo.py
```

Ajustar o teto:

```bash
python src/setup_yolo.py --max-gb 10
```

Selecionar fontes:

```bash
python src/setup_yolo.py --datasets rikkarth/welding-defect-object-detection AI4Manufacturing/217
```

Treinar com parâmetros próprios:

```bash
python src/setup_yolo.py --train --epochs 100 --imgsz 640 --batch 8 --device cpu

# Salvar checkpoints a cada época (padrão) e retomar após interrupção
python src/setup_yolo.py --train --resume

# Retomar de um checkpoint específico
python src/setup_yolo.py --train --resume-from runs/detect/welding-yolo/weights/last.pt
```

Para GPU NVIDIA, use `--device 0` somente se PyTorch CUDA compatível já estiver instalado. O padrão é CPU.

**Importante:** os datasets têm tarefas e esquemas diferentes. A fonte principal CC0 é detecção com caixas YOLO. AI4Manufacturing/217 contém caixas em pixels em registros parquet e requer conversão; AI4Manufacturing/218 é classificação de imagem, não detecção. Ambos são baixados separadamente e não são misturados automaticamente ao treino YOLO. O limite é calculado a partir dos tamanhos publicados pelo Hugging Face e pode diferir ligeiramente do espaço efetivamente ocupado.

Fontes com licença pouco clara não são baixadas automaticamente: LoHi-WELD (Google Drive; licença de dados não identificada no repositório consultado) e Intel Robotic Welding (acesso gated e licença Intel Research Use). Consulte [docs/dataset_yolo.md](docs/dataset_yolo.md).

Os pesos e checkpoints ficam em `runs/detect/welding-yolo/weights/`. `last.pt` é atualizado durante o treinamento e `best.pt` guarda o melhor resultado de validação. Se o processo for interrompido, execute novamente com `--resume`; para outro nome de execução, informe o mesmo `--name` usado originalmente. Não apague a pasta `runs/detect/` antes de retomar.\n\nApós o treinamento bem-sucedido, faça inferência:

```bash
python src/predict_yolo.py --weights runs/detect/welding-yolo/weights/best.pt --source caminho/para/imagem.jpg
```

## Estrutura

- `src/`: análise, treino, preparação dos datasets, inferência e API.
- `docs/`: relatório técnico, documentação da API, datasets e notas éticas.
- `data/`: CSV tabular e dados visuais locais (não versionados).
- `models/`: artefatos do treinamento tabular.
- `runs/`: resultados e pesos YOLO locais.

## Resultados e limitações

O baseline tabular usa split estratificado aleatório 75/25. Métricas observadas nesse split: balanced accuracy de 96,51% e macro-F1 de 93,94%. Esses números não demonstram generalização temporal ou por lote; faça essa validação antes de qualquer uso real.

O CSV tabular não contém imagens e não treina o detector YOLO. A classe genérica `defect` não deve ser interpretada automaticamente como porosidade ou causa específica. Fotografias convencionais não comprovam sobrecarga elétrica, vibração ou desvio térmico interno. Nenhuma saída comanda máquinas: a decisão humana é obrigatória.

## Licença

Consulte [LICENSE](LICENSE) e as licenças individuais de cada dataset antes de redistribuir, publicar ou usar comercialmente os dados.


### Fontes adicionais de grande volume (acesso restrito)

O catálogo também tenta baixar, respeitando o teto total, duas fontes maiores. Elas exigem login e aprovação/aceitação manual no Hugging Face; o instalador não tenta contornar o gate e continua com as fontes públicas se o acesso ainda não estiver liberado:

- [AI4Manufacturing/105 — TIG Stainless Steel 304](https://huggingface.co/datasets/AI4Manufacturing/105): cerca de 9,93 GB, 45.058 quadros de 58 execuções TIG e seis rótulos em nível de execução. Licença upstream CC BY-SA 4.0; splits devem permanecer por execução, nunca por quadro.
- [AI4Manufacturing/219 — BAM hot-cracking metallography](https://huggingface.co/datasets/AI4Manufacturing/219): cerca de 11,6 GB, 609 imagens microscópicas de seções de solda. Licença upstream CC BY 4.0; separar por corpo de prova.

Para habilitar: abra cada página, entre na conta Hugging Face, solicite/aceite as condições e aguarde aprovação. Depois execute novamente `python src/setup_yolo.py`. Se não houver acesso, o instalador registra o item como ignorado e continua. O manifesto indica status e tamanho. Esses conjuntos são auxiliares e não são convertidos para YOLO automaticamente.

O catálogo conhecido soma aproximadamente 22,8 GB se todos os cinco conjuntos forem acessíveis, abaixo do limite padrão de 25 GB. O limite real é recalculado a cada execução usando os tamanhos informados pelo Hub. Não incluí o MIAD (32,3 GB), pois sozinho excede o teto; nem conjuntos com licença/condições incompatíveis ou duplicatas.
