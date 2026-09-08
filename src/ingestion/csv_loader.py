from pathlib import Path
import pandas as pd


def load_csv(file_path: str) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.

    Parameters
    ----------
    file_path : str
        Path to the CSV file.

    Returns
    -------
    pd.DataFrame
        Loaded dataset.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the file is not a CSV file.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    if path.suffix.lower() != ".csv":
        raise ValueError(
            f"Expected a CSV file, received: {path.suffix}"
        )

    try:
        df = pd.read_csv(path)
    except Exception as exc:
        raise ValueError(
            f"Unable to read CSV file: {exc}"
        ) from exc

    if df.empty:
        raise ValueError("The dataset is empty.")

    return df


def get_csv_metadata(file_path: str) -> dict:
    """
    Return basic metadata about a CSV dataset.
    """

    df = load_csv(file_path)

    return {
        "file_name": Path(file_path).name,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "memory_usage_mb": round(
            df.memory_usage(deep=True).sum() / (1024 * 1024),
            3
        ),
    }