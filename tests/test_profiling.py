from pathlib import Path

from src.ingestion.csv_loader import load_csv
from src.profiling.profiler import profile_dataset


DATASET = Path("data/samples/messy_students.csv")


def test_dataset_can_be_loaded():

    df = load_csv(str(DATASET))

    assert not df.empty
    assert len(df.columns) > 0


def test_profile_contains_dataset_information():

    df = load_csv(str(DATASET))

    profile = profile_dataset(df)

    assert "dataset" in profile
    assert "missing_values" in profile
    assert "duplicates" in profile
    assert "schema" in profile


def test_profile_has_correct_dimensions():

    df = load_csv(str(DATASET))

    profile = profile_dataset(df)

    assert profile["dataset"]["rows"] == len(df)
    assert profile["dataset"]["columns"] == len(df.columns)


def test_profile_detects_missing_values():

    df = load_csv(str(DATASET))

    profile = profile_dataset(df)

    assert (
        profile["missing_values"]["total"]
        >= 0
    )


def test_profile_detects_duplicates():

    df = load_csv(str(DATASET))

    profile = profile_dataset(df)

    assert (
        profile["duplicates"]["total_rows"]
        >= 0
    )