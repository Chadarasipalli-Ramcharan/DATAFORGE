import pandas as pd


def calculate_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate missing-value statistics for every column.
    """

    total = df.isna().sum()

    percentage = (
        (total / len(df)) * 100
    ).round(2)

    result = pd.DataFrame({
        "missing_count": total,
        "missing_percentage": percentage,
    })

    return result


def calculate_unique_values(df: pd.DataFrame) -> pd.Series:
    """
    Calculate the number of unique values in every column.
    """

    return df.nunique(dropna=True)


def calculate_duplicate_rows(df: pd.DataFrame) -> int:
    """
    Count duplicate rows.
    """

    return int(df.duplicated().sum())


def calculate_numeric_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate descriptive statistics for numeric columns.
    """

    numeric_df = df.select_dtypes(
        include="number"
    )

    if numeric_df.empty:
        return pd.DataFrame()

    return numeric_df.describe().T


def calculate_column_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate comprehensive statistics for every column.
    """

    missing = calculate_missing_values(df)
    unique = calculate_unique_values(df)

    result = pd.DataFrame({
        "data_type": df.dtypes.astype(str),
        "missing_count": missing["missing_count"],
        "missing_percentage": missing["missing_percentage"],
        "unique_values": unique,
    })

    return result