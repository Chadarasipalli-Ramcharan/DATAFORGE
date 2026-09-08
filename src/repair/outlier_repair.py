import pandas as pd


def repair_outliers(
    df: pd.DataFrame,
    multiplier: float = 1.5,
) -> tuple[pd.DataFrame, dict]:
    """
    Repair numerical outliers using IQR-based capping.

    Values below the lower IQR boundary are replaced with
    the lower boundary.

    Values above the upper IQR boundary are replaced with
    the upper boundary.

    Missing values are left unchanged.

    Returns:
        repaired dataframe and repair report.
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    if multiplier <= 0:
        raise ValueError(
            "Multiplier must be greater than zero."
        )

    repaired_df = df.copy()

    report = {
        "total_repaired": 0,
        "columns": {},
    }

    numeric_columns = repaired_df.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:

        series = repaired_df[column]

        non_null = series.dropna()

        if non_null.empty:
            continue

        q1 = non_null.quantile(0.25)
        q3 = non_null.quantile(0.75)

        iqr = q3 - q1

        lower_bound = (
            q1 - multiplier * iqr
        )

        upper_bound = (
            q3 + multiplier * iqr
        )

        lower_mask = (
            series < lower_bound
        )

        upper_mask = (
            series > upper_bound
        )

        lower_count = int(
            lower_mask.sum()
        )

        upper_count = int(
            upper_mask.sum()
        )

        repaired_count = (
            lower_count + upper_count
        )

        # Convert the column to float before assigning
        # decimal IQR boundaries.
        if repaired_count > 0:
            repaired_df[column] = (
                repaired_df[column].astype(float)
            )

            repaired_df.loc[
                lower_mask,
                column,
            ] = lower_bound

            repaired_df.loc[
                upper_mask,
                column,
            ] = upper_bound

        report["total_repaired"] += (
            repaired_count
        )

        report["columns"][column] = {
            "q1": float(q1),
            "q3": float(q3),
            "iqr": float(iqr),
            "lower_bound": float(
                lower_bound
            ),
            "upper_bound": float(
                upper_bound
            ),
            "lower_outliers": lower_count,
            "upper_outliers": upper_count,
            "outliers_repaired": repaired_count,
        }

    return repaired_df, report