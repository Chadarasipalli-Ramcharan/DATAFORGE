"""
Automated data repair engine.
"""

from .missing_value_repair import repair_missing_values
from .duplicate_repair import repair_duplicate_rows
from .outlier_repair import repair_outliers
from .type_repair import (
    repair_numeric_types,
    repair_boolean_types,
)


def run_repairs(
    df,
    repair_missing=True,
    repair_duplicates=True,
    repair_outliers_enabled=True,
    repair_types=True,
):
    """Run the complete automated data repair pipeline."""

    if df is None:
        raise ValueError("Dataset cannot be None.")

    repaired_df = df.copy()

    report = {
        "original_rows": int(len(df)),
        "original_columns": int(len(df.columns)),
        "operations": {},
        "total_repaired": 0,
    }

    # Missing values
    if repair_missing:
        repaired_df, missing_report = repair_missing_values(
            repaired_df
        )

        report["operations"]["missing_values"] = missing_report

        report["total_repaired"] += int(
            missing_report.get("total_repaired", 0)
        )

    # Duplicate rows
    if repair_duplicates:
        repaired_df, duplicate_report = repair_duplicate_rows(
            repaired_df
        )

        report["operations"]["duplicates"] = duplicate_report

        report["total_repaired"] += int(
            duplicate_report.get("duplicates_removed", 0)
        )

    # Outliers
    if repair_outliers_enabled:
        repaired_df, outlier_report = repair_outliers(
            repaired_df
        )

        report["operations"]["outliers"] = outlier_report

        report["total_repaired"] += int(
            outlier_report.get("total_repaired", 0)
        )

    # Data types
    if repair_types:
        repaired_df, numeric_report = repair_numeric_types(
            repaired_df
        )

        repaired_df, boolean_report = repair_boolean_types(
            repaired_df
        )

        report["operations"]["numeric_types"] = numeric_report
        report["operations"]["boolean_types"] = boolean_report

    # Final statistics
    report["final_rows"] = int(len(repaired_df))
    report["final_columns"] = int(len(repaired_df.columns))

    report["rows_removed"] = (
        report["original_rows"]
        - report["final_rows"]
    )

    report["remaining_missing_values"] = int(
        repaired_df.isna().sum().sum()
    )

    return repaired_df, report


__all__ = [
    "repair_missing_values",
    "repair_duplicate_rows",
    "repair_outliers",
    "repair_numeric_types",
    "repair_boolean_types",
    "run_repairs",
]