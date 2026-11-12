
"""Load career data from the JSON knowledge base."""

import json
from pathlib import Path

from module2.schemas import CareerSchema


DATASET_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "career_dataset.json"
)


def load_careers(
    dataset_path: str | Path = DATASET_PATH
) -> list[CareerSchema]:
    """Load and validate all careers from the JSON dataset."""

    path = Path(dataset_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Career dataset not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    # Support either a list or an object containing "careers".
    if isinstance(data, dict):
        data = data.get("careers")

    if not isinstance(data, list):
        raise ValueError(
            "The career dataset must contain a list of careers."
        )

    careers = [
        CareerSchema.model_validate(item)
        for item in data
    ]

    return careers
