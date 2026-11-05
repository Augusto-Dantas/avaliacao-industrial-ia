from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dataset_industrial_cibersistemas_15k.csv"

def main() -> None:
    data = pd.read_csv(DATA, parse_dates=["timestamp"])
    print("shape:", data.shape)
    print("missing:", int(data.isna().sum().sum()))
    print("period:", data.timestamp.min(), "->", data.timestamp.max())
    print("OEE mean:", data.oee_pct.mean())
    print("availability mean:", data.disponibilidade_pct.mean())
    print("performance mean:", data.desempenho_pct.mean())
    print("quality mean:", data.qualidade_pct.mean())
    print("classes (%):", (data.classe_falha.value_counts(normalize=True) * 100).round(2))
    print("Pearson with OEE:", data.select_dtypes("number").corr().oee_pct.sort_values(ascending=False).round(3))

if __name__ == "__main__":
    main()
