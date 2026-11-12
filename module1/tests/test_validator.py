
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validator import normalize_text, is_supported, validate_profile


def create_profile():
    return {
        "personal_info": {
            "name": "Mai"
        },
        "professional_summary": None,
        "skills": ["Python", "SQL"],
        "all_skills": [],
        "languages": ["English"],
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "courses_and_trainings": [],
        "volunteer_work": [],
        "awards_and_achievements": [],
        "competitions": [],
        "additional_sections": []
    }


def test_normalize_text():
    result = normalize_text("  PYTHON   Developer! ")

    assert result == "python developer"


def test_is_supported():
    assert is_supported("Python", cv_text="I know Python and SQL")


def test_is_not_supported():
    assert not is_supported("Java", cv_text="I know Python and SQL")


def test_valid_profile():
    cv_text = "Mai Python SQL English"

    result = validate_profile(cv_text, create_profile())

    assert result["is_valid"] is True
    assert result["total_checks"] == 4
    assert result["passed_checks"] == 4
    assert result["unsupported_count"] == 0
    assert result["issues_count"] == 0


def test_unsupported_skill():
    profile = create_profile()
    profile["skills"] = ["Python", "Java"]

    result = validate_profile(
        "Mai Python SQL English",
        profile
    )

    assert result["is_valid"] is False
    assert result["unsupported_count"] == 1
    assert result["warnings"][0]["value"] == "Java"


def test_duplicate_skills():
    profile = create_profile()
    profile["skills"] = ["Python", "python"]

    result = validate_profile(
        "Mai Python SQL English",
        profile
    )

    assert result["issues_count"] == 1
    assert result["issues"][0]["field"] == "skills"


def test_invalid_education_item():
    profile = create_profile()
    profile["education"] = ["Invalid item"]

    result = validate_profile(
        "Mai Python SQL English",
        profile
    )

    assert result["issues_count"] == 1
    assert result["issues"][0]["field"] == "education[0]"
