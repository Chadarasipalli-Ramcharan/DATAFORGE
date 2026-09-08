import pandas as pd


def detect_outliers(
    df: pd.DataFrame,
    multiplier: float = 1.5,
) -> dict:
    """
    Detect numerical outliers using the IQR method.

    IQR = Q3 - Q1

    Lower bound = Q1 - multiplier * IQR
    Upper bound = Q3 + multiplier * IQR
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    if multiplier <= 0:
        raise ValueError(
            "Multiplier must be greater than zero."
        )

    results = {}

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:

        series = df[column].dropna()

        if series.empty:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        lower_bound = (
            q1 - multiplier * iqr
        )

        upper_bound = (
            q3 + multiplier * iqr
        )

        mask = (
            (df[column] < lower_bound)
            | (df[column] > upper_bound)
        )

        indices = df.index[mask].tolist()

        results[column] = {
            "q1": float(q1),
            "q3": float(q3),
            "iqr": float(iqr),
            "lower_bound": float(
                lower_bound
            ),
            "upper_bound": float(
                upper_bound
            ),
            "outlier_count": len(indices),
            "outlier_indices": indices,
            "has_outliers": len(indices) > 0,
        }

    return results