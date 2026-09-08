import json
from pathlib import Path


def generate_quality_report(
    profile: dict,
    detection: dict,
    scoring: dict,
    validation: dict,
    repair_report: dict | None = None,
) -> dict:
    """
    Generate a complete data quality report.
    """

    if profile is None:
        raise ValueError("Profile cannot be None.")

    if detection is None:
        raise ValueError("Detection results cannot be None.")

    if scoring is None:
        raise ValueError("Scoring results cannot be None.")

    if validation is None:
        raise ValueError("Validation results cannot be None.")

    return {
        "profile": profile,
        "detection": detection,
        "scoring": scoring,
        "validation": validation,
        "repair": repair_report or {},
    }


def save_quality_report(
    report: dict,
    output_path: str = "quality_report.json",
) -> str:
    """
    Save the quality report as a JSON file.
    """

    if report is None:
        raise ValueError("Report cannot be None.")

    path = Path(output_path)

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
            default=str,
        )

    return str(path)