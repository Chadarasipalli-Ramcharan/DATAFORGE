import pandas as pd


def detect_duplicate_rows(df: pd.DataFrame) -> dict:
    """
    Detect duplicate rows in a dataset.
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    duplicate_mask = df.duplicated(keep=False)

    duplicate_rows = df[duplicate_mask]

    return {
        "duplicate_count": int(
            df.duplicated().sum()
        ),
        "duplicate_percentage": round(
            (
                df.duplicated().sum()
                / len(df) * 100
            )
            if len(df) > 0
            else 0,
            2,
        ),
        "has_duplicates": bool(
            df.duplicated().any()
        ),
        "duplicate_indices": (
            duplicate_rows.index.tolist()
        ),
    }


def get_duplicate_rows(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return all rows involved in duplication.
    """

    return df[
        df.duplicated(keep=False)
    ].copy()