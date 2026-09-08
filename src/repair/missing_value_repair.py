import pandas as pd


def repair_missing_values(
    df: pd.DataFrame,
    numerical_strategy: str = "median",
    categorical_strategy: str = "mode",
) -> tuple[pd.DataFrame, dict]:
    """
    Automatically repair missing values.

    Numerical columns:
        - median
        - mean

    Categorical columns:
        - mode
        - constant

    Returns:
        repaired dataframe and repair report.
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    if df.empty:
        return df.copy(), {
            "total_repaired": 0,
            "columns": {},
        }

    if numerical_strategy not in {"median", "mean"}:
        raise ValueError(
            "Numerical strategy must be 'median' or 'mean'."
        )

    if categorical_strategy not in {"mode", "constant"}:
        raise ValueError(
            "Categorical strategy must be 'mode' or 'constant'."
        )

    repaired_df = df.copy()

    report = {
        "total_repaired": 0,
        "columns": {},
    }

    for column in repaired_df.columns:

        missing_before = int(
            repaired_df[column].isna().sum()
        )

        if missing_before == 0:
            continue

        if pd.api.types.is_numeric_dtype(
            repaired_df[column]
        ):
            if numerical_strategy == "median":
                replacement = repaired_df[column].median()
            else:
                replacement = repaired_df[column].mean()

            if pd.isna(replacement):
                continue

        else:
            if categorical_strategy == "mode":
                modes = repaired_df[column].mode(
                    dropna=True
                )

                if modes.empty:
                    continue

                replacement = modes.iloc[0]

            else:
                replacement = "Unknown"

        repaired_df[column] = repaired_df[column].fillna(
            replacement
        )

        missing_after = int(
            repaired_df[column].isna().sum()
        )

        repaired_count = (
            missing_before - missing_after
        )

        report["total_repaired"] += repaired_count

        report["columns"][column] = {
            "missing_before": missing_before,
            "missing_after": missing_after,
            "repaired_count": repaired_count,
            "strategy": (
                numerical_strategy
                if pd.api.types.is_numeric_dtype(
                    df[column]
                )
                else categorical_strategy
            ),
            "replacement": (
                replacement
                if not pd.isna(replacement)
                else None
            ),
        }

    return repaired_df, report