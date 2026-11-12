from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_DATA = [
    ROOT / "data" / "dataset_industrial_cibersistemas_15k.csv",
    ROOT / "Requisição" / "dataset_industrial_cibersistemas_15k.csv",
]
OUTPUT = ROOT / "reports"


def find_dataset() -> Path:
    for candidate in CANDIDATE_DATA:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "Dataset não encontrado em data/ ou Requisição/. "
        "Consulte a seção de instalação do README."
    )


def main() -> None:
    path = find_dataset()
    data = pd.read_csv(path)
    required = {"classe_falha"}
    missing_columns = sorted(required - set(data.columns))
    if missing_columns:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing_columns}")

    if "timestamp" in data:
        data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce")
        data = data.sort_values("timestamp")

    report = {
        "dataset": str(path.relative_to(ROOT)),
        "rows": int(len(data)),
        "columns": int(len(data.columns)),
        "missing_cells": int(data.isna().sum().sum()),
        "period_start": (
            data["timestamp"].min().isoformat()
            if "timestamp" in data and data["timestamp"].notna().any() else None
        ),
        "period_end": (
            data["timestamp"].max().isoformat()
            if "timestamp" in data and data["timestamp"].notna().any() else None
        ),
        "class_distribution": (
            data["classe_falha"].value_counts(dropna=False).to_dict()
        ),
    }

    numeric = data.select_dtypes(include="number")
    if "oee_pct" in data:
        report["oee_mean_pct"] = float(data["oee_pct"].mean())
        report["oee_median_pct"] = float(data["oee_pct"].median())
        correlations = numeric.corr(numeric_only=True)["oee_pct"].dropna()
        report["pearson_with_oee"] = correlations.sort_values(
            ascending=False
        ).round(4).to_dict()

    # Recompute OEE components only when the source has their underlying counts/times.
    required_oee = {
        "tempo_planejado_min", "tempo_parada_min",
        "pecas_produzidas", "pecas_boas",
    }
    if required_oee.issubset(data.columns):
        planned = data["tempo_planejado_min"].where(
            data["tempo_planejado_min"] > 0
        )
        operating = (data["tempo_planejado_min"] - data["tempo_parada_min"]).clip(
            lower=0
        )
        availability = operating.div(planned)
        quality = data["pecas_boas"].div(
            data["pecas_produzidas"].where(data["pecas_produzidas"] > 0)
        )
        report["oee_recomputed_available_components"] = {
            "availability_mean_pct": float(availability.mean() * 100),
            "quality_mean_pct": float(quality.mean() * 100),
            "note": (
                "Desempenho requer ciclo ideal/produção teórica; não foi "
                "reconstruído sem essa variável."
            ),
        }

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "analysis.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Relatório salvo em {OUTPUT / 'analysis.json'}")


if __name__ == "__main__":
    main()
