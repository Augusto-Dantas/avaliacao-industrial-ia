from pathlib import Path
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def infer(payload: dict) -> dict:
    classifier = joblib.load(ROOT / "models" / "classifier.joblib")
    anomaly_model = joblib.load(ROOT / "models" / "anomaly.joblib")
    row = pd.DataFrame([{key: payload.get(key) for key in classifier["features"]}])
    probabilities = classifier["pipeline"].predict_proba(row)[0]
    index = probabilities.argmax()
    label = str(classifier["pipeline"].classes_[index])
    anomaly = bool(anomaly_model["pipeline"].predict(row)[0] == -1)
    return {
        "classe_prevista": label,
        "confianca": round(float(probabilities[index]), 4),
        "probabilidades": {
            str(name): round(float(value), 4)
            for name, value in zip(classifier["pipeline"].classes_, probabilities)
        },
        "anomalia": anomaly,
        "acao": "inspecao humana" if label != "Sem Falha" or anomaly else "monitorar",
        "automatic_machine_action": False,
    }

if __name__ == "__main__":
    sample = {
        "temperatura_solda_c": 217, "corrente_solda_a": 164,
        "tensao_solda_v": 24, "pressao_gas_bar": 4.5,
        "vibracao_mm_s": 1.1, "velocidade_linha_m_min": 12,
        "area_porosidade_px": 2, "temperatura_max_haz_c": 226,
    }
    print(infer(sample))
