import pandas as pd


def detect_missing_values(df: pd.DataFrame) -> dict:
    """
    Detect missing and null values in every column.
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    if df.empty:
        return {}

    results = {}

    for column in df.columns:
        missing_count = int(df[column].isna().sum())

        results[column] = {
            "missing_count": missing_count,
            "missing_percentage": round(
                (missing_count / len(df)) * 100,
                2
            ),
            "has_missing": missing_count > 0,
        }

    return results


def get_columns_with_missing_values(
    df: pd.DataFrame,
) -> list[str]:
    """
    Return columns containing one or more missing values.
    """

    results = detect_missing_values(df)

    return [
        column
        for column, details in results.items()
        if details["has_missing"]
    ]