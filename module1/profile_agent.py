
"""Profile Agent: processes a CV and stores the extracted user profile."""

import os

from cv_parser import read_cv
from ai_parser import parse_cv_with_ai
from skill_normalizer import normalize_skills
from schemas import CVSchema
from database import save_cv, get_cv


def build_profile(
    file_path: str,
    original_filename: str | None = None
) -> dict:
    """
    Extract, validate, normalize, and store a CV profile.

    Args:
        file_path: Path to the uploaded CV file.
        original_filename: Original name of the uploaded file.

    Returns:
        The saved CV profile.
    """

    # Check if the CV file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"CV file not found: {file_path}")

    # 1. Extract text and hyperlinks from the CV
    cv_text = read_cv(file_path)

    if not cv_text or not cv_text.strip():
        raise ValueError(
            "No text was extracted from the CV. "
            "The file may be empty or scanned."
        )

    # 2. Extract structured information using the AI parser
    extracted_data = parse_cv_with_ai(cv_text)

    # 3. Validate extracted information against CVSchema
    validated_data = CVSchema.model_validate(extracted_data)

    # Convert the validated model into a dictionary
    profile_data = validated_data.model_dump(mode="json")

    # 4. Normalize skills and remove duplicates
    # Normalize the main skills.
    profile_data["skills"] = normalize_skills(
    profile_data["skills"]
    )

# Normalize all skills extracted from the CV.
    normalized_all_skills = normalize_skills(
    profile_data["all_skills"]
    )

# Make sure every main skill is included in all_skills.
    profile_data["all_skills"] = normalize_skills(
    normalized_all_skills + profile_data["skills"]
    )

    # 5. Save the profile in PostgreSQL
    filename = original_filename or os.path.basename(file_path)

    cv_id = save_cv(
        filename=filename,
        cv_data=profile_data
    )

    # 6. Retrieve the saved profile
    saved_profile = get_cv(cv_id)

    if saved_profile is None:
        raise RuntimeError(
            "CV was saved but could not be retrieved."
        )

    return saved_profile


def process_cv_file(
    file_path: str,
    original_filename: str | None = None
) -> dict:
    """Process an uploaded CV file and return its saved profile."""

    return build_profile(file_path, original_filename)
