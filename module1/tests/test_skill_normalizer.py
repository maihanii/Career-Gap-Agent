import sys
from pathlib import Path

# Allow importing files from module1
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill_normalizer import normalize_skills


def test_remove_duplicates():
    skills = ["Python", "python", "SQL", "SQL"]
    result = normalize_skills(skills)

    assert result == ["Python", "SQL"]


def test_normalize_skill_aliases():
    skills = ["sklearn", "ms excel", "py torch"]
    result = normalize_skills(skills)

    assert result == ["Scikit-learn", "Microsoft Excel", "PyTorch"]


def test_remove_empty_values():
    skills = ["Python", "", "  ", None, "SQL"]
    result = normalize_skills(skills)

    assert result == ["Python", "SQL"]


def test_empty_list():
    assert normalize_skills([]) == []