import pandas as pd


def calculate_quality_score(
    df: pd.DataFrame,
    detection_results: dict,
) -> dict:
    """
    Calculate an overall data quality score.

    The score is based on:
    - Missing values
    - Duplicate rows
    - Outliers

    Score range:
        0   = Very Poor
        100 = Excellent
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    if not isinstance(detection_results, dict):
        raise TypeError(
            "detection_results must be a dictionary."
        )

    if df.empty:
        raise ValueError(
            "Dataset cannot be empty."
        )

    total_rows = len(df)
    total_cells = df.shape[0] * df.shape[1]

    # ---------------------------------------------------------
    # 1. Missing value penalty
    # ---------------------------------------------------------

    missing_results = detection_results.get(
        "missing_values",
        {},
    )

    total_missing = sum(
        details.get("missing_count", 0)
        for details in missing_results.values()
    )

    missing_percentage = (
        total_missing / total_cells * 100
        if total_cells > 0
        else 0
    )

    missing_penalty = min(
        missing_percentage,
        40,
    )

    # ---------------------------------------------------------
    # 2. Duplicate penalty
    # ---------------------------------------------------------

    duplicate_results = detection_results.get(
        "duplicates",
        {},
    )

    duplicate_count = int(
        duplicate_results.get(
            "duplicate_count",
            0,
        )
    )

    duplicate_percentage = (
        duplicate_count / total_rows * 100
        if total_rows > 0
        else 0
    )

    duplicate_penalty = min(
        duplicate_percentage,
        30,
    )

    # ---------------------------------------------------------
    # 3. Outlier penalty
    # ---------------------------------------------------------

    outlier_results = detection_results.get(
        "outliers",
        {},
    )

    total_outliers = sum(
        details.get("outlier_count", 0)
        for details in outlier_results.values()
    )

    outlier_percentage = (
        total_outliers / total_rows * 100
        if total_rows > 0
        else 0
    )

    outlier_penalty = min(
        outlier_percentage,
        30,
    )

    # ---------------------------------------------------------
    # Final score
    # ---------------------------------------------------------

    total_penalty = (
        missing_penalty
        + duplicate_penalty
        + outlier_penalty
    )

    score = max(
        0,
        min(
            100,
            100 - total_penalty,
        ),
    )

    # ---------------------------------------------------------
    # Quality grade
    # ---------------------------------------------------------

    if score >= 90:
        grade = "Excellent"
    elif score >= 75:
        grade = "Good"
    elif score >= 60:
        grade = "Fair"
    elif score >= 40:
        grade = "Poor"
    else:
        grade = "Critical"

    return {
        "score": round(score, 2),
        "grade": grade,
        "metrics": {
            "total_rows": total_rows,
            "total_columns": df.shape[1],
            "total_cells": total_cells,
            "missing_values": total_missing,
            "missing_percentage": round(
                missing_percentage,
                2,
            ),
            "duplicate_rows": duplicate_count,
            "duplicate_percentage": round(
                duplicate_percentage,
                2,
            ),
            "outliers": total_outliers,
            "outlier_percentage": round(
                outlier_percentage,
                2,
            ),
        },
        "penalties": {
            "missing_values": round(
                missing_penalty,
                2,
            ),
            "duplicates": round(
                duplicate_penalty,
                2,
            ),
            "outliers": round(
                outlier_penalty,
                2,
            ),
            "total": round(
                total_penalty,
                2,
            ),
        },
    }