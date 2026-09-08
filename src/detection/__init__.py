"""
Detection engine.
"""

from .missing_values import (
    detect_missing_values,
    get_columns_with_missing_values,
)

from .duplicates import (
    detect_duplicate_rows,
    get_duplicate_rows,
)

from .outliers import detect_outliers


def run_detection(
    df,
    outlier_multiplier=1.5,
):
    """
    Run all data quality detection checks.
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    return {
        "missing_values": detect_missing_values(df),
        "duplicates": detect_duplicate_rows(df),
        "outliers": detect_outliers(
            df,
            multiplier=outlier_multiplier,
        ),
    }


__all__ = [
    "detect_missing_values",
    "get_columns_with_missing_values",
    "detect_duplicate_rows",
    "get_duplicate_rows",
    "detect_outliers",
    "run_detection",
]