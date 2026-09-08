import pandas as pd


def create_repair_log(
    original_df: pd.DataFrame,
    repaired_df: pd.DataFrame,
    repair_report: dict,
) -> pd.DataFrame:
    """
    Create a row-level log describing changes made during repair.
    """

    if original_df is None:
        raise ValueError("Original dataset cannot be None.")

    if repaired_df is None:
        raise ValueError("Repaired dataset cannot be None.")

    if original_df.shape != repaired_df.shape:
        raise ValueError(
            "Original and repaired datasets must have the same shape."
        )

    changes = []

    for index in original_df.index:
        for column in original_df.columns:
            original_value = original_df.loc[index, column]
            repaired_value = repaired_df.loc[index, column]

            if pd.isna(original_value) and pd.isna(repaired_value):
                changed = False
            elif pd.isna(original_value) or pd.isna(repaired_value):
                changed = True
            else:
                changed = original_value != repaired_value

            if changed:
                changes.append(
                    {
                        "row_index": index,
                        "column": column,
                        "original_value": original_value,
                        "repaired_value": repaired_value,
                    }
                )

    return pd.DataFrame(
        changes,
        columns=[
            "row_index",
            "column",
            "original_value",
            "repaired_value",
        ],
    )