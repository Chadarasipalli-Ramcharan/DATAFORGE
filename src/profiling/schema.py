import pandas as pd


def infer_schema(df: pd.DataFrame) -> list[dict]:
    """
    Infer the schema of the dataset.

    Returns one dictionary per column containing
    basic structural information.
    """

    schema = []

    for column in df.columns:

        series = df[column]

        schema.append({
            "column": column,
            "dtype": str(series.dtype),
            "nullable": bool(series.isna().any()),
            "unique_values": int(series.nunique(dropna=True)),
            "sample_values": (
                series.dropna()
                .astype(str)
                .head(3)
                .tolist()
            ),
        })

    return schema