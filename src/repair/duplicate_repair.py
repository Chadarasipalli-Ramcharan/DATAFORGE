import pandas as pd


def repair_duplicate_rows(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """
    Remove duplicate rows from a dataset.

    Keeps the first occurrence of each row and removes
    subsequent duplicates.

    Returns:
        repaired dataframe and repair report.
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    if df.empty:
        return df.copy(), {
            "rows_before": 0,
            "rows_after": 0,
            "duplicates_removed": 0,
            "duplicate_percentage": 0.0,
        }

    rows_before = len(df)

    duplicate_count = int(
        df.duplicated().sum()
    )

    repaired_df = df.drop_duplicates(
        keep="first"
    ).reset_index(drop=True)

    rows_after = len(repaired_df)

    duplicate_percentage = round(
        (duplicate_count / rows_before) * 100,
        2,
    )

    report = {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "duplicates_removed": duplicate_count,
        "duplicate_percentage": duplicate_percentage,
    }

    return repaired_df, report