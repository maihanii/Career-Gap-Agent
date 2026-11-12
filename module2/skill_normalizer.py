
"""Normalize skill names before career matching."""


SKILL_ALIASES = {
    "python programming": "Python",
    "python language": "Python",

    "api": "APIs",
    "api integration": "APIs",
    "rest api": "APIs",
    "rest apis": "APIs",

    "ml": "Machine Learning",
    "machine learning techniques": "Machine Learning",

    "dl": "Deep Learning",
    "deep learning techniques": "Deep Learning",

    "scikit learn": "Scikit-learn",
    "sklearn": "Scikit-learn",

    "powerbi": "Power BI",
    "power bi desktop": "Power BI",

    "js": "JavaScript",
    "javascript programming": "JavaScript",

    "problem-solving": "Problem Solving",
    "problem solving skills": "Problem Solving",

    "data visualization techniques": "Data Visualization"
}


def normalize_skill(skill: str) -> str:
    """Return the standardized name of one skill."""

    if not isinstance(skill, str):
        return ""

    skill = " ".join(skill.strip().split())

    if not skill:
        return ""

    normalized = skill.casefold()

    if normalized in SKILL_ALIASES:
        return SKILL_ALIASES[normalized]

    return skill


def normalize_skills(skills: list[str]) -> list[str]:
    """Normalize skills and remove duplicates."""

    if not isinstance(skills, list):
        return []

    normalized_skills = []
    seen = set()

    for skill in skills:
        normalized = normalize_skill(skill)

        if not normalized:
            continue

        key = normalized.casefold()

        if key not in seen:
            normalized_skills.append(normalized)
            seen.add(key)

    return normalized_skills
