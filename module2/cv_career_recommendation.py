
"""Generate career recommendations from a user's stored CV."""

from module1.database import get_cv

from module2.schemas import UserSkills, CareerDiscoveryResponse
from module2.career_discovery_agent import discover_careers


def get_career_recommendations(
    cv_id: int,
    top_n: int = 5
) -> CareerDiscoveryResponse:
    """Retrieve the complete CV and generate career recommendations."""

    cv = get_cv(cv_id)

    if cv is None:
        raise ValueError(f"CV with ID {cv_id} was not found.")

    extracted_data = cv.get("extracted_data", {})

    if not isinstance(extracted_data, dict):
        raise ValueError("Invalid extracted CV data.")

    skills = extracted_data.get("all_skills") or extracted_data.get("skills", [])

    if not isinstance(skills, list) or not skills:
        raise ValueError("No skills were found in this CV.")

    user = UserSkills(
        cv_id=cv_id,
        skills=skills,
        professional_summary=extracted_data.get("professional_summary"),
        education=extracted_data.get("education", []),
        experience=extracted_data.get("experience", []),
        projects=extracted_data.get("projects", []),
        courses_and_trainings=extracted_data.get(
            "courses_and_trainings", []
        )
    )

    return discover_careers(user=user, top_n=top_n)
