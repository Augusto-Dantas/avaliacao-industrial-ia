from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_DATA = [
    ROOT / "data" / "dataset_industrial_cibersistemas_15k.csv",
    ROOT / "Requisição" / "dataset_industrial_cibersistemas_15k.csv",
]
MODELS = ROOT / "models"


def find_dataset() -> Path:
    for candidate in CANDIDATE_DATA:
        if candidate.is_file():
            return candidate
    # Candidates may be redirected to temporary directories by tests or callers.
    locations = ", ".join(
        str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
        for path in CANDIDATE_DATA
    )
    raise FileNotFoundError(
        f"Dataset não encontrado. Coloque o CSV em uma destas pastas: {locations}"
    )


def split_data(data: pd.DataFrame, features: list[str]):
    """Prefer a forward-in-time holdout; fall back transparently if classes vanish."""
    X = data[features]
    y = data["classe_falha"].astype(str)

    if "timestamp" in data.columns:
        timestamps = pd.to_datetime(data["timestamp"], errors="coerce")
        valid = timestamps.notna()
        if valid.all():
            ordered = timestamps.sort_values()
            cutoff = ordered.iloc[int(len(ordered) * 0.75)]
            train_mask = timestamps < cutoff
            test_mask = timestamps >= cutoff
            if train_mask.sum() and test_mask.sum():
                train_classes = set(y[train_mask])
                test_classes = set(y[test_mask])
                if train_classes == set(y) and test_classes == set(y):
                    return (
                        X.loc[train_mask], X.loc[test_mask],
                        y.loc[train_mask], y.loc[test_mask],
                        "temporal_holdout_75_25",
                    )

    # Fallback is retained for small or temporally class-segregated datasets.
    # Its use is explicitly recorded; it is not evidence of temporal generalization.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    return X_train, X_test, y_train, y_test, "stratified_random_fallback"


def main() -> None:
    data_path = find_dataset()
    data = pd.read_csv(data_path)
    if "classe_falha" not in data:
        raise ValueError("O CSV precisa conter a coluna obrigatória 'classe_falha'.")
    data = data.dropna(subset=["classe_falha"]).copy()

    excluded = {
        "timestamp", "lote_id", "classe_falha", "anomalia_isolamento",
        "disponibilidade_pct", "desempenho_pct", "qualidade_pct", "oee_pct",
        "pecas_produzidas", "pecas_boas", "pecas_defeituosas",
        "tempo_planejado_min", "tempo_parada_min",
    }
    features = [
        column for column in data.select_dtypes(include="number").columns
        if column not in excluded
    ]
    if not features:
        raise ValueError("Nenhuma feature numérica elegível foi encontrada.")

    X_train, X_test, y_train, y_test, split_strategy = split_data(data, features)
    classifier = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("rf", RandomForestClassifier(
            n_estimators=400,
            class_weight="balanced_subsample",
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )),
    ])
    classifier.fit(X_train, y_train)
    predictions = classifier.predict(X_test)

    metrics = {
        "dataset": str(data_path.relative_to(ROOT)),
        "rows": int(len(data)),
        "features": features,
        "split_strategy": split_strategy,
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, predictions)),
        "macro_f1": float(f1_score(y_test, predictions, average="macro")),
        "report": classification_report(
            y_test, predictions, output_dict=True, zero_division=0
        ),
        "confusion_matrix": confusion_matrix(
            y_test, predictions, labels=classifier.classes_
        ).tolist(),
        "class_order": classifier.classes_.tolist(),
        "warning": (
            "Holdout aleatório estratificado: não comprova generalização temporal."
            if split_strategy == "stratified_random_fallback"
            else "Holdout temporal; ainda requer validação independente por lote."
        ),
    }

    MODELS.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"pipeline": classifier, "features": features},
        MODELS / "classifier.joblib",
    )

    normal_rows = data["classe_falha"].astype(str) == "Sem Falha"
    anomaly = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("iforest", IsolationForest(
            n_estimators=300, contamination=0.05, random_state=42, n_jobs=-1
        )),
    ])
    anomaly.fit(data.loc[normal_rows, features])
    joblib.dump(
        {"pipeline": anomaly, "features": features},
        MODELS / "anomaly.joblib",
    )

    (MODELS / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Dataset: {data_path.relative_to(ROOT)}")
    print(f"Split: {split_strategy}")
    print(f"Balanced accuracy: {metrics['balanced_accuracy']:.4f}")
    print(f"Macro F1: {metrics['macro_f1']:.4f}")
    print(f"Modelos e métricas salvos em: {MODELS}")


if __name__ == "__main__":
    main()
