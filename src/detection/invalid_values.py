import pandas as pd


def detect_invalid_values(
    df: pd.DataFrame,
    rules: dict | None = None,
) -> dict:
    """
    Detect invalid values using configurable rules.

    Example rules:

    {
        "age": {
            "min": 0,
            "max": 120
        },
        "email": {
            "not_empty": True
        }
    }
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    if rules is None:
        rules = {}

    results = {}

    for column, column_rules in rules.items():

        if column not in df.columns:
            continue

        invalid_mask = pd.Series(
            False,
            index=df.index
        )

        series = df[column]

        # Minimum value
        if "min" in column_rules:
            numeric_values = pd.to_numeric(
                series,
                errors="coerce"
            )

            invalid_mask |= (
                numeric_values
                < column_rules["min"]
            )

        # Maximum value
        if "max" in column_rules:
            numeric_values = pd.to_numeric(
                series,
                errors="coerce"
            )

            invalid_mask |= (
                numeric_values
                > column_rules["max"]
            )

        # Empty strings
        if column_rules.get(
            "not_empty",
            False
        ):
            invalid_mask |= (
                series.astype(str)
                .str.strip()
                .eq("")
            )

        invalid_indices = (
            df.index[invalid_mask]
            .tolist()
        )

        results[column] = {
            "invalid_count": len(
                invalid_indices
            ),
            "invalid_indices": invalid_indices,
            "has_invalid_values": len(
                invalid_indices
            ) > 0,
        }

    return results