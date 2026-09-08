import pandas as pd


def detect_type_errors(
    df: pd.DataFrame,
    expected_types: dict | None = None,
) -> dict:
    """
    Detect values that do not match expected
    column data types.

    Example:

    {
        "age": "numeric",
        "email": "string"
    }
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    if expected_types is None:
        expected_types = {}

    results = {}

    for column, expected_type in (
        expected_types.items()
    ):

        if column not in df.columns:
            continue

        series = df[column]

        if expected_type == "numeric":

            converted = pd.to_numeric(
                series,
                errors="coerce"
            )

            invalid_mask = (
                series.notna()
                & converted.isna()
            )

        elif expected_type == "integer":

            converted = pd.to_numeric(
                series,
                errors="coerce"
            )

            invalid_mask = (
                series.notna()
                & (
                    converted.isna()
                    | (
                        converted
                        % 1 != 0
                    )
                )
            )

        elif expected_type == "string":

            invalid_mask = series.map(
                lambda value:
                not isinstance(
                    value,
                    str
                )
                if pd.notna(value)
                else False
            )

        else:
            raise ValueError(
                f"Unsupported expected type: "
                f"{expected_type}"
            )

        indices = (
            df.index[invalid_mask]
            .tolist()
        )

        results[column] = {
            "expected_type": expected_type,
            "error_count": len(indices),
            "error_indices": indices,
            "has_type_errors": len(indices) > 0,
        }

    return results