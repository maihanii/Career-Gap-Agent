
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
import profile_agent


def create_test_profile():
    return {
        "personal_info": {"name": "Mai"},
        "professional_summary": None,
        "skills": ["Python", "python", "SQL"],
        "all_skills": ["sklearn", "Scikit-learn"],
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


class FakeValidatedData:
    def model_dump(self, mode="json"):
        return create_test_profile()


class FakeSchema:
    @staticmethod
    def model_validate(data):
        return FakeValidatedData()


def test_build_profile_success(tmp_path, monkeypatch):
    # Create a temporary CV file
    cv_file = tmp_path / "test_cv.pdf"
    cv_file.write_text("Test CV")

    # Mock external operations
    monkeypatch.setattr(profile_agent, "read_cv",
                        lambda path: "Mai Python SQL English")

    monkeypatch.setattr(profile_agent, "parse_cv_with_ai",
                        lambda text: {"skills": ["Python"]})

    monkeypatch.setattr(profile_agent, "CVSchema", FakeSchema)

    saved_data = {}

    def fake_save_cv(filename, cv_data):
        saved_data["filename"] = filename
        saved_data["data"] = cv_data
        return 123

    monkeypatch.setattr(profile_agent, "save_cv", fake_save_cv)

    monkeypatch.setattr(
        profile_agent,
        "get_cv",
        lambda cv_id: {
            "id": cv_id,
            "filename": saved_data["filename"],
            "extracted_data": saved_data["data"]
        }
    )

    result = profile_agent.build_profile(
        str(cv_file),
        "Mai_CV.pdf"
    )

    assert result["id"] == 123
    assert result["filename"] == "Mai_CV.pdf"
    assert saved_data["data"]["skills"] == ["Python", "SQL"]
    assert saved_data["data"]["all_skills"] == ["Scikit-learn"]


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        profile_agent.build_profile("nonexistent_cv.pdf")


def test_empty_cv_file(tmp_path, monkeypatch):
    cv_file = tmp_path / "empty.pdf"
    cv_file.write_text("")

    monkeypatch.setattr(profile_agent, "read_cv", lambda path: "")

    with pytest.raises(ValueError, match="No text was extracted"):
        profile_agent.build_profile(str(cv_file))


def test_saved_profile_not_found(tmp_path, monkeypatch):
    cv_file = tmp_path / "test_cv.pdf"
    cv_file.write_text("Test CV")

    monkeypatch.setattr(
        profile_agent,
        "read_cv",
        lambda path: "Mai Python SQL English"
    )

    monkeypatch.setattr(
        profile_agent,
        "parse_cv_with_ai",
        lambda text: {}
    )

    monkeypatch.setattr(profile_agent, "CVSchema", FakeSchema)
    monkeypatch.setattr(profile_agent, "save_cv", lambda **kwargs: 123)
    monkeypatch.setattr(profile_agent, "get_cv", lambda cv_id: None)

    with pytest.raises(RuntimeError, match="could not be retrieved"):
        profile_agent.build_profile(str(cv_file))
