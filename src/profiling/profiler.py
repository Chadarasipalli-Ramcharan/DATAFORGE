import pandas as pd

from .statistics import (
    calculate_missing_values,
    calculate_unique_values,
    calculate_duplicate_rows,
    calculate_numeric_statistics,
    calculate_column_statistics,
)

from .schema import infer_schema


def profile_dataset(df: pd.DataFrame) -> dict:
    """
    Generate a complete quality-oriented profile of a dataset.
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    if df.empty:
        raise ValueError("Dataset cannot be empty.")

    missing = calculate_missing_values(df)
    unique = calculate_unique_values(df)

    profile = {
        "dataset": {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "memory_usage_mb": round(
                df.memory_usage(deep=True).sum()
                / (1024 * 1024),
                3,
            ),
        },

        "missing_values": {
            "total": int(df.isna().sum().sum()),
            "by_column": missing.to_dict(
                orient="index"
            ),
        },

        "duplicates": {
            "total_rows": calculate_duplicate_rows(df),
        },

        "schema": infer_schema(df),

        "unique_values": {
            column: int(count)
            for column, count in unique.items()
        },

        "numeric_statistics": (
            calculate_numeric_statistics(df)
            .to_dict(orient="index")
        ),

        "column_statistics": (
            calculate_column_statistics(df)
            .to_dict(orient="index")
        ),
    }

    return profile