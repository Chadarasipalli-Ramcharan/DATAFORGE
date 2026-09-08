import pandas as pd


def repair_numeric_types(
    df: pd.DataFrame,
    columns: list[str] | None = None,
) -> tuple[pd.DataFrame, dict]:
    """
    Convert columns containing numeric values stored as text
    into appropriate numeric dtypes.

    Only columns explicitly provided through `columns` are
    considered. If columns is None, all object/string columns
    are evaluated.

    Returns:
        repaired dataframe and repair report.
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    repaired_df = df.copy()

    if columns is None:
        candidate_columns = repaired_df.select_dtypes(
            include=["object", "string"]
        ).columns.tolist()
    else:
        candidate_columns = columns

    report = {
        "columns_checked": [],
        "columns_converted": [],
        "conversion_details": {},
    }

    for column in candidate_columns:

        if column not in repaired_df.columns:
            raise ValueError(
                f"Column '{column}' does not exist."
            )

        report["columns_checked"].append(column)

        original_dtype = str(
            repaired_df[column].dtype
        )

        converted = pd.to_numeric(
            repaired_df[column],
            errors="coerce",
        )

        original_non_null = (
            repaired_df[column].notna().sum()
        )

        converted_non_null = converted.notna().sum()

        # Convert only when every original non-null value
        # can be represented numerically.
        if (
            original_non_null > 0
            and converted_non_null == original_non_null
        ):

            repaired_df[column] = converted

            new_dtype = str(
                repaired_df[column].dtype
            )

            if new_dtype != original_dtype:

                report["columns_converted"].append(
                    column
                )

                report["conversion_details"][column] = {
                    "original_dtype": original_dtype,
                    "new_dtype": new_dtype,
                    "values_converted": int(
                        original_non_null
                    ),
                }

    return repaired_df, report


def repair_boolean_types(
    df: pd.DataFrame,
    columns: list[str] | None = None,
) -> tuple[pd.DataFrame, dict]:
    """
    Convert common textual boolean representations
    into boolean values.

    Supported values:

        true / false
        yes / no
        y / n
        1 / 0

    Conversion is performed only when all non-null values
    in a column belong to the supported representations.
    """

    if df is None:
        raise ValueError("Dataset cannot be None.")

    repaired_df = df.copy()

    if columns is None:
        candidate_columns = repaired_df.select_dtypes(
            include=["object", "string"]
        ).columns.tolist()
    else:
        candidate_columns = columns

    true_values = {
        "true",
        "yes",
        "y",
        "1",
    }

    false_values = {
        "false",
        "no",
        "n",
        "0",
    }

    report = {
        "columns_checked": [],
        "columns_converted": [],
        "conversion_details": {},
    }

    for column in candidate_columns:

        if column not in repaired_df.columns:
            raise ValueError(
                f"Column '{column}' does not exist."
            )

        report["columns_checked"].append(column)

        series = repaired_df[column]

        non_null = series.dropna()

        if non_null.empty:
            continue

        normalized = (
            non_null.astype(str)
            .str.strip()
            .str.lower()
        )

        unique_values = set(
            normalized.unique()
        )

        supported_values = (
            true_values | false_values
        )

        if not unique_values.issubset(
            supported_values
        ):
            continue

        repaired_df[column] = (
            series.astype(str)
            .str.strip()
            .str.lower()
            .map(
                lambda value:
                True
                if value in true_values
                else False
                if value in false_values
                else pd.NA
            )
            .astype("boolean")
        )

        report["columns_converted"].append(
            column
        )

        report["conversion_details"][column] = {
            "original_dtype": str(
                series.dtype
            ),
            "new_dtype": str(
                repaired_df[column].dtype
            ),
            "values_converted": int(
                len(non_null)
            ),
        }

    return repaired_df, report