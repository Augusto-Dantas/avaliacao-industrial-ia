#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

RUN_TESTS=1
RUN_VISION=0
SERVE_API=0
INSTALL_DEPS=1
VISION_EPOCHS="${VISION_EPOCHS:-50}"
VISION_IMGSZ="${VISION_IMGSZ:-640}"
VISION_BATCH="${VISION_BATCH:-8}"
VISION_DEVICE="${VISION_DEVICE:-cpu}"

usage() {
  cat <<'EOF'
Uso: bash scripts/run_pipeline.sh [opções]

Pipeline principal:
  1. instala dependências tabulares e de teste
  2. executa análise industrial
  3. treina Random Forest e Isolation Forest
  4. executa testes pytest
  5. confere os artefatos gerados

Opções:
  --vision          também prepara o dataset e treina o YOLO (download grande)
  --vision-epochs N épocas do YOLO (padrão: 50)
  --no-tests        não executa pytest
  --no-install      não instala dependências
  --serve           inicia a API ao final, na porta 8000
  -h, --help        mostra esta ajuda

Variáveis:
  PYTHON_BIN        executável Python a utilizar
  USE_SYSTEM_PYTHON=1 não cria virtualenv automaticamente (útil no Colab)
  VISION_DEVICE     cpu (padrão) ou 0 para GPU CUDA configurada
EOF
}

while (($#)); do
  case "$1" in
    --vision) RUN_VISION=1 ;;
    --vision-epochs)
      shift
      VISION_EPOCHS="${1:?Informe o número de épocas após --vision-epochs}"
      ;;
    --no-tests) RUN_TESTS=0 ;;
    --no-install) INSTALL_DEPS=0 ;;
    --serve) SERVE_API=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Opção desconhecida: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

if [[ -n "${PYTHON_BIN:-}" ]]; then
  PYTHON="$PYTHON_BIN"
elif [[ "${USE_SYSTEM_PYTHON:-0}" == "1" ]] || [[ -n "${COLAB_RELEASE_TAG:-}" ]] || [[ -d "/content" ]]; then
  PYTHON="$(command -v python3 || command -v python)"
else
  if [[ ! -x .venv/bin/python ]]; then
    echo "[setup] Criando ambiente virtual .venv"
    python3 -m venv .venv
  fi
  PYTHON="$ROOT_DIR/.venv/bin/python"
fi

if [[ -z "${PYTHON:-}" || ! -x "$PYTHON" ]]; then
  echo "Python não encontrado. Instale Python 3.10+ ou defina PYTHON_BIN." >&2
  exit 1
fi

echo "[1/5] Python selecionado: $("$PYTHON" --version)"

if (( INSTALL_DEPS )); then
  echo "[2/5] Instalando dependências"
  "$PYTHON" -m pip install --upgrade pip
  "$PYTHON" -m pip install -r requirements-dev.txt
fi

echo "[3/5] Validando dataset e executando análise"
"$PYTHON" - <<'PY'
from pathlib import Path
candidates = [
    Path("data/dataset_industrial_cibersistemas_15k.csv"),
    Path("Requisição/dataset_industrial_cibersistemas_15k.csv"),
]
found = next((p for p in candidates if p.is_file()), None)
if found is None:
    raise SystemExit(
        "Dataset não encontrado. Esperado em data/ ou Requisição/."
    )
print(f"Dataset encontrado: {found}")
PY
"$PYTHON" src/analysis.py

echo "[4/5] Treinando modelos tabulares"
"$PYTHON" src/train.py

if (( RUN_TESTS )); then
  echo "[5/5] Executando testes automatizados"
  "$PYTHON" -m pytest
else
  echo "[5/5] Testes ignorados (--no-tests)"
fi

if (( RUN_VISION )); then
  echo "[vision] Instalando dependências opcionais de visão computacional"
  "$PYTHON" -m pip install -r requirements-vision.txt
  echo "[vision] Preparando dataset e treinando YOLO"
  "$PYTHON" src/setup_yolo.py --train \
    --epochs "$VISION_EPOCHS" \
    --imgsz "$VISION_IMGSZ" \
    --batch "$VISION_BATCH" \
    --device "$VISION_DEVICE"
fi

echo
echo "Pipeline concluído."
echo "Relatório: reports/analysis.json"
echo "Classificador: models/classifier.joblib"
echo "Detector de anomalias: models/anomaly.joblib"
echo "Métricas: models/metrics.json"

if (( SERVE_API )); then
  echo "Iniciando API em http://0.0.0.0:8000"
  exec "$PYTHON" -m uvicorn src.api:app --host 0.0.0.0 --port 8000
fi
