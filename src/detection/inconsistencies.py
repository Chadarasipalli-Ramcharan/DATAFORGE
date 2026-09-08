import pandas as pd


def detect_inconsistent_values(
    df: pd.DataFrame,
) -> dict:
    """
    Detect common formatting inconsistencies
    in categorical and text columns.

    Examples:

    Male
    male
    MALE

    are treated as different raw values but
    flagged as potentially inconsistent.
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    results = {}

    for column in df.select_dtypes(
        include=["object", "string"]
    ).columns:

        series = df[column].dropna().astype(str)

        if series.empty:
            continue

        normalized = (
            series
            .str.strip()
            .str.lower()
        )

        raw_unique = set(series.unique())
        normalized_unique = set(
            normalized.unique()
        )

        inconsistent = (
            len(raw_unique)
            > len(normalized_unique)
        )

        results[column] = {
            "raw_unique_values": len(
                raw_unique
            ),
            "normalized_unique_values": len(
                normalized_unique
            ),
            "has_inconsistency": inconsistent,
        }

    return results