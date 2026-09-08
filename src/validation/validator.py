"""
Dataset validation engine.
"""

import pandas as pd

from .rules import (
    check_no_missing_values,
    check_no_duplicate_rows,
    check_numeric_columns_valid,
    check_required_columns,
    check_numeric_ranges,
)


def validate_dataset(
    df: pd.DataFrame,
    required_columns: list[str] | None = None,
    numeric_ranges: dict | None = None,
) -> dict:
    """
    Run all validation rules against a dataset.

    Returns a complete validation report.
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    if df.empty:
        raise ValueError("Dataset cannot be empty.")

    required_columns = (
        required_columns
        if required_columns is not None
        else []
    )

    numeric_ranges = (
        numeric_ranges
        if numeric_ranges is not None
        else {}
    )

    results = {
        "no_missing_values":
            check_no_missing_values(df),

        "no_duplicate_rows":
            check_no_duplicate_rows(df),

        "numeric_values_valid":
            check_numeric_columns_valid(df),

        "required_columns":
            check_required_columns(
                df,
                required_columns,
            ),

        "numeric_ranges":
            check_numeric_ranges(
                df,
                numeric_ranges,
            ),
    }

    passed_rules = sum(
        1
        for result in results.values()
        if result["passed"]
    )

    total_rules = len(results)

    validation_score = (
        passed_rules / total_rules * 100
        if total_rules > 0
        else 100
    )

    return {
        "valid": passed_rules == total_rules,
        "validation_score": round(
            validation_score,
            2,
        ),
        "passed_rules": passed_rules,
        "failed_rules": (
            total_rules - passed_rules
        ),
        "total_rules": total_rules,
        "results": results,
    }