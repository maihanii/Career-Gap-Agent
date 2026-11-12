
"""Calculate career match scores using CV evidence."""

import re

from module2.schemas import UserSkills, CareerSchema, CareerMatchResult
from module2.skill_normalizer import normalize_skill


WEIGHTS = {
    "skills": 0.45,
    "projects": 0.20,
    "education": 0.15,
    "experience": 0.15,
    "career_direction": 0.05
}

# Number of relevant projects or experiences
# considered sufficient for a full evidence score.
MAX_EVIDENCE_ITEMS = 2


def contains_phrase(text: str, phrase: str) -> bool:
    """Check whether a complete phrase exists in text."""

    if not text or not phrase:
        return False

    pattern = (
        r"(?<![a-zA-Z0-9])"
        + re.escape(phrase.casefold())
        + r"(?![a-zA-Z0-9])"
    )

    return re.search(pattern, text.casefold()) is not None


def collect_text(data) -> str:
    """Convert nested CV data into searchable text."""

    if data is None:
        return ""

    if isinstance(data, str):
        return data

    if isinstance(data, dict):
        return " ".join(
            collect_text(value)
            for value in data.values()
        )

    if isinstance(data, (list, tuple)):
        return " ".join(
            collect_text(item)
            for item in data
        )

    return str(data)


def get_skill_score(user: UserSkills, career: CareerSchema):
    """Calculate weighted required-skill coverage."""

    user_skills = {
        normalize_skill(skill).casefold()
        for skill in user.skills
        if normalize_skill(skill)
    }

    total_weight = sum(
        skill.weight for skill in career.required_skills
    )

    matched_weight = 0
    matched_required = []
    missing_required = []

    for required_skill in career.required_skills:

        skill_name = normalize_skill(required_skill.name)

        if skill_name.casefold() in user_skills:
            matched_weight += required_skill.weight
            matched_required.append(required_skill.name)
        else:
            missing_required.append(required_skill.name)

    skills_score = (
        (matched_weight / total_weight) * 100
        if total_weight > 0 else 0
    )

    matched_optional = []

    for optional_skill in career.optional_skills:

        normalized = normalize_skill(optional_skill)

        if normalized.casefold() in user_skills:
            matched_optional.append(optional_skill)

    return (
        round(skills_score, 2),
        matched_required,
        missing_required,
        matched_optional
    )


def get_evidence_score(items: list, keywords: list[str]):
    """
    Score individual projects or experience entries.

    Each entry gets a relevance score based on its matching
    career-specific keywords.

    The two strongest entries determine the final score.
    Unrelated entries do not reduce the score.
    """

    if not items or not keywords:
        return 0.0, 0, len(items)

    entry_scores = []

    # Three distinct keyword matches are enough
    # to give one entry a full relevance score.
    keyword_threshold = min(3, len(keywords))

    for item in items:

        item_text = collect_text(item)

        matched_keywords = [
            keyword
            for keyword in keywords
            if contains_phrase(item_text, keyword)
        ]

        if not matched_keywords:
            continue

        entry_score = min(
            len(matched_keywords) / keyword_threshold,
            1.0
        ) * 100

        entry_scores.append(entry_score)

    entry_scores.sort(reverse=True)

    # Keep the strongest two pieces of evidence.
    strongest_scores = entry_scores[:MAX_EVIDENCE_ITEMS]

    # Divide by the maximum possible number of evidence items.
    score = sum(strongest_scores) / MAX_EVIDENCE_ITEMS

    return (
        round(score, 2),
        len(entry_scores),
        len(items)
    )


def get_education_score(
    education: list,
    relevant_fields: list[str]
) -> float:
    """Evaluate education relevance to a career."""

    if not education or not relevant_fields:
        return 0.0

    degree_text = " ".join(
        str(item.get("degree") or "")
        for item in education
        if isinstance(item, dict)
    )

    field_text = " ".join(
        str(item.get("field_of_study") or "")
        for item in education
        if isinstance(item, dict)
    )

    field_text = field_text.casefold().replace(
    "computer and information science",
    "computer science"
    )
    
    # Exact relevance in the major or field of study.
    if any(
        contains_phrase(field_text, field)
        for field in relevant_fields
    ):
        return 100.0

    # A related degree without a matching major
    # receives partial credit.
    if any(
        contains_phrase(degree_text, field)
        for field in relevant_fields
    ):
        return 60.0

    return 0.0



def get_career_direction_score(
    summary: str | None,
    direction_keywords: list[str]
) -> float:
    """
    Evaluate the user's stated career direction.

    The first keyword represents the direct career title.
    Other keywords represent related career directions.
    """

    if not summary or not direction_keywords:
        return 0.0

    # Direct career title match.
    direct_keyword = direction_keywords[0]

    if contains_phrase(summary, direct_keyword):
        return 100.0

    # Related direction matches.
    related_keywords = direction_keywords[1:]

    matched_count = sum(
        1
        for keyword in related_keywords
        if contains_phrase(summary, keyword)
    )

    return min(matched_count * 35, 70.0)


def calculate_match(
    user: UserSkills,
    career: CareerSchema
) -> CareerMatchResult:
    """Calculate the complete multi-factor career match."""

    # 1. Skills
    (
        skills_score,
        matched_required,
        missing_required,
        matched_optional
    ) = get_skill_score(user, career)

    # 2. Projects
    (
        projects_score,
        matched_projects,
        total_projects
    ) = get_evidence_score(
        user.projects,
        career.relevant_project_keywords
    )

    # 3. Education
    education_score = get_education_score(
        user.education,
        career.relevant_education_fields
    )

    # 4. Experience and training
    all_experience = (
        user.experience + user.courses_and_trainings
    )

    (
        experience_score,
        matched_experiences,
        total_experiences
    ) = get_evidence_score(
        all_experience,
        career.relevant_experience_keywords
    )

    # 5. Career direction
    career_direction_score = get_career_direction_score(
        user.professional_summary,
        career.career_direction_keywords
    )

    # Final weighted score
    final_score = (
        skills_score * WEIGHTS["skills"]
        + projects_score * WEIGHTS["projects"]
        + education_score * WEIGHTS["education"]
        + experience_score * WEIGHTS["experience"]
        + career_direction_score * WEIGHTS["career_direction"]
    )

    final_score = round(final_score, 2)

    explanation = (
        f"{len(matched_required)} out of "
        f"{len(career.required_skills)} required skills matched. "
        f"Relevant projects: {matched_projects}/{total_projects}. "
        f"Relevant experience and training: "
        f"{matched_experiences}/{total_experiences}. "
        f"Education score: {education_score}%. "
        f"Career direction score: {career_direction_score}%."
    )

    return CareerMatchResult(
        career_id=career.career_id,
        title=career.title,
        match_percentage=final_score,
        matched_required_skills=matched_required,
        missing_required_skills=missing_required,
        matched_optional_skills=matched_optional,
        skills_score=skills_score,
        projects_score=projects_score,
        education_score=education_score,
        experience_score=experience_score,
        career_direction_score=career_direction_score,
        explanation=explanation
    )
