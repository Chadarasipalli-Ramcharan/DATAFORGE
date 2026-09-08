"""
Validation rules for the data quality engine.
"""

import pandas as pd


def check_no_missing_values(
    df: pd.DataFrame,
) -> dict:
    """
    Validate that the dataset contains no missing values.
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    missing_total = int(
        df.isna().sum().sum()
    )

    return {
        "rule": "no_missing_values",
        "passed": missing_total == 0,
        "missing_count": missing_total,
    }


def check_no_duplicate_rows(
    df: pd.DataFrame,
) -> dict:
    """
    Validate that the dataset contains no duplicate rows.
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    duplicate_count = int(
        df.duplicated().sum()
    )

    return {
        "rule": "no_duplicate_rows",
        "passed": duplicate_count == 0,
        "duplicate_count": duplicate_count,
    }


def check_numeric_columns_valid(
    df: pd.DataFrame,
) -> dict:
    """
    Validate that numeric columns do not contain
    infinite values.
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    invalid_values = {}

    for column in numeric_columns:
        infinite_count = int(
            (~df[column].isin([
                float("inf"),
                float("-inf"),
            ])).eq(False).sum()
        )

        if infinite_count > 0:
            invalid_values[column] = infinite_count

    return {
        "rule": "numeric_values_valid",
        "passed": len(invalid_values) == 0,
        "invalid_values": invalid_values,
    }


def check_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
) -> dict:
    """
    Validate that all required columns exist.
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    if required_columns is None:
        required_columns = []

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    return {
        "rule": "required_columns",
        "passed": len(missing_columns) == 0,
        "missing_columns": missing_columns,
    }


def check_numeric_ranges(
    df: pd.DataFrame,
    ranges: dict | None = None,
) -> dict:
    """
    Validate numeric columns against optional
    minimum and maximum limits.

    Example:

        {
            "age": {"min": 0, "max": 120},
            "percentage": {"min": 0, "max": 100}
        }
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    if ranges is None:
        ranges = {}

    violations = {}

    for column, limits in ranges.items():

        if column not in df.columns:
            continue

        if not pd.api.types.is_numeric_dtype(
            df[column]
        ):
            continue

        minimum = limits.get("min")
        maximum = limits.get("max")

        mask = pd.Series(
            False,
            index=df.index,
        )

        if minimum is not None:
            mask |= df[column] < minimum

        if maximum is not None:
            mask |= df[column] > maximum

        count = int(mask.sum())

        if count > 0:
            violations[column] = {
                "violation_count": count,
                "indices": df.index[
                    mask
                ].tolist(),
            }

    return {
        "rule": "numeric_ranges",
        "passed": len(violations) == 0,
        "violations": violations,
    }