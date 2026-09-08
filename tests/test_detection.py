from pathlib import Path

from src.ingestion.csv_loader import load_csv

from src.detection.missing_values import (
    detect_missing_values,
)

from src.detection.duplicates import (
    detect_duplicate_rows,
)

from src.detection.inconsistencies import (
    detect_inconsistent_values,
)

from src.detection.outliers import (
    detect_outliers,
)


DATASET = Path(
    "data/samples/messy_students.csv"
)


def get_dataset():

    return load_csv(
        str(DATASET)
    )


def test_missing_value_detection():

    df = get_dataset()

    result = detect_missing_values(df)

    assert isinstance(result, dict)

    assert set(result.keys()) == set(
        df.columns
    )


def test_duplicate_detection():

    df = get_dataset()

    result = detect_duplicate_rows(df)

    assert "duplicate_count" in result

    assert "has_duplicates" in result

    assert result[
        "duplicate_count"
    ] >= 0


def test_inconsistency_detection():

    df = get_dataset()

    result = detect_inconsistent_values(df)

    assert isinstance(result, dict)


def test_outlier_detection():

    df = get_dataset()

    result = detect_outliers(df)

    assert isinstance(result, dict)

    for column, details in result.items():

        assert (
            details["outlier_count"]
            >= 0
        )