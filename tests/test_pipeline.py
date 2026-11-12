from pathlib import Path

import pandas as pd
import pytest

from src import train


def _sample_frame(rows=40):
    timestamps = pd.date_range("2026-01-01", periods=rows, freq="h")
    labels = ["Sem Falha", "Falha A"] * (rows // 2)
    return pd.DataFrame({
        "timestamp": timestamps,
        "temperatura_solda_c": range(rows),
        "classe_falha": labels,
    })


def test_find_dataset_prefers_first_existing_candidate(monkeypatch, tmp_path):
    first = tmp_path / "data.csv"
    second = tmp_path / "other.csv"
    first.touch()
    second.touch()
    monkeypatch.setattr(train, "CANDIDATE_DATA", [first, second])

    assert train.find_dataset() == first


def test_find_dataset_raises_when_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(
        train, "CANDIDATE_DATA", [tmp_path / "missing.csv"]
    )
    with pytest.raises(FileNotFoundError, match="Dataset não encontrado"):
        train.find_dataset()


def test_split_data_uses_temporal_holdout_when_all_classes_exist():
    data = _sample_frame()
    X_train, X_test, y_train, y_test, strategy = train.split_data(
        data, ["temperatura_solda_c"]
    )

    assert strategy == "temporal_holdout_75_25"
    assert len(X_train) + len(X_test) == len(data)
    assert set(y_train) == set(data["classe_falha"])
    assert set(y_test) == set(data["classe_falha"])
    assert X_train.index.max() < X_test.index.min()


def test_split_data_falls_back_when_temporal_test_lacks_class():
    data = _sample_frame()
    data.loc[data.index >= 30, "classe_falha"] = "Falha B"

    X_train, X_test, y_train, y_test, strategy = train.split_data(
        data, ["temperatura_solda_c"]
    )

    assert strategy == "stratified_random_fallback"
    assert len(X_train) + len(X_test) == len(data)
    assert set(y_train) == set(data["classe_falha"])
    assert set(y_test) == set(data["classe_falha"])
