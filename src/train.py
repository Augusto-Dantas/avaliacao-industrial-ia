from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, balanced_accuracy_score, f1_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dataset_industrial_cibersistemas_15k.csv"
MODELS = ROOT / "models"
MODELS.mkdir(exist_ok=True)

def main() -> None:
    data = pd.read_csv(DATA)
    target = data.classe_falha
    excluded = {
        "timestamp", "lote_id", "classe_falha", "anomalia_isolamento",
        "disponibilidade_pct", "desempenho_pct", "qualidade_pct", "oee_pct",
        "pecas_produzidas", "pecas_boas", "pecas_defeituosas",
        "tempo_planejado_min", "tempo_parada_min",
    }
    features = [c for c in data.select_dtypes("number") if c not in excluded]
    X = data[features]
    X_train, X_test, y_train, y_test = train_test_split(
        X, target, test_size=0.25, random_state=42, stratify=target
    )
    classifier = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("rf", RandomForestClassifier(
            n_estimators=400, class_weight="balanced_subsample",
            min_samples_leaf=2, random_state=42, n_jobs=-1
        )),
    ]).fit(X_train, y_train)

    predictions = classifier.predict(X_test)
    metrics = {
        "features": features,
        "balanced_accuracy": float(balanced_accuracy_score(y_test, predictions)),
        "macro_f1": float(f1_score(y_test, predictions, average="macro")),
        "report": classification_report(y_test, predictions, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=classifier.classes_).tolist(),
        "class_order": classifier.classes_.tolist(),
    }
    joblib.dump({"pipeline": classifier, "features": features}, MODELS / "classifier.joblib")
    (MODELS / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2))

    anomaly = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("iforest", IsolationForest(
            n_estimators=300, contamination=0.05, random_state=42, n_jobs=-1
        )),
    ]).fit(X[target == "Sem Falha"])
    joblib.dump({"pipeline": anomaly, "features": features}, MODELS / "anomaly.joblib")
    print("balanced accuracy:", metrics["balanced_accuracy"])
    print("macro F1:", metrics["macro_f1"])

if __name__ == "__main__":
    main()
