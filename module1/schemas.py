from pydantic import BaseModel, Field

class PersonalInfo(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None
    github: str | None = None


class EducationItem(BaseModel):
    degree: str | None = None
    field_of_study: str | None = None
    institution: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    grade: str | None = None


class ExperienceItem(BaseModel):
    job_title: str | None = None
    company: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    responsibilities: list[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    name: str | None = None
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)


class CertificationItem(BaseModel):
    name: str | None = None
    issuer: str | None = None
    issue_date: str | None = None


class CourseTrainingItem(BaseModel):
    name: str | None = None
    provider: str | None = None
    date: str | None = None


class VolunteerItem(BaseModel):
    role: str | None = None
    organization: str | None = None
    responsibilities: list[str] = Field(default_factory=list)


class AchievementItem(BaseModel):
    title: str | None = None
    date: str | None = None
    description: str | None = None


class CompetitionItem(BaseModel):
    name: str | None = None
    result: str | None = None
    date: str | None = None

class AdditionalSection(BaseModel):
    title: str | None = None
    content: list[str] = Field(default_factory=list)

class CVSchema(BaseModel):
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    professional_summary: str | None = None

    skills: list[str] = Field(default_factory=list)
    all_skills: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)

    education: list[EducationItem] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)

    certifications: list[CertificationItem] = Field(default_factory=list)
    courses_and_trainings: list[CourseTrainingItem] = Field(default_factory=list)

    volunteer_work: list[VolunteerItem] = Field(default_factory=list)
    awards_and_achievements: list[AchievementItem] = Field(default_factory=list)
    competitions: list[CompetitionItem] = Field(default_factory=list)
    
    additional_sections: list[AdditionalSection] = Field(default_factory=list)