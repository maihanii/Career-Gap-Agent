
from pydantic import BaseModel, Field


class RequiredSkill(BaseModel):
    name: str
    weight: int = Field(default=1, ge=1, le=5)



class CareerSchema(BaseModel):
    career_id: str
    title: str
    description: str

    required_skills: list[RequiredSkill]

    optional_skills: list[str] = Field(default_factory=list)

    relevant_project_keywords: list[str] = Field(
        default_factory=list
    )

    relevant_experience_keywords: list[str] = Field(
        default_factory=list
    )

    relevant_education_fields: list[str] = Field(
        default_factory=list
    )

    career_direction_keywords: list[str] = Field(
        default_factory=list
    )



class UserSkills(BaseModel):
    cv_id: int | None = None

    skills: list[str] = Field(default_factory=list)

    professional_summary: str | None = None

    education: list[dict] = Field(default_factory=list)

    experience: list[dict] = Field(default_factory=list)

    projects: list[dict] = Field(default_factory=list)

    courses_and_trainings: list[dict] = Field(default_factory=list)


class CareerMatchResult(BaseModel):
    career_id: str
    title: str

    match_percentage: float = Field(ge=0, le=100)

    matched_required_skills: list[str] = Field(default_factory=list)
    missing_required_skills: list[str] = Field(default_factory=list)
    matched_optional_skills: list[str] = Field(default_factory=list)

    skills_score: float = 0
    projects_score: float = 0
    education_score: float = 0
    experience_score: float = 0
    career_direction_score: float = 0

    explanation: str = ""


class CareerDiscoveryResponse(BaseModel):
    cv_id: int | None = None
    recommendations: list[CareerMatchResult] = Field(default_factory=list)
