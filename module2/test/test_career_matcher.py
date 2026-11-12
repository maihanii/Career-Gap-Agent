
from module2.schemas import CareerSchema, RequiredSkill, UserSkills
from module2.career_matcher import calculate_match


def test_calculate_match():

    user = UserSkills(
        cv_id=11,
        skills=["Python", "SQL"]
    )

    career = CareerSchema(
        career_id="data_scientist",
        title="Data Scientist",
        description="Analyzes data and builds predictive models.",
        required_skills=[
            RequiredSkill(name="Python", weight=5),
            RequiredSkill(name="SQL", weight=4),
            RequiredSkill(name="Statistics", weight=3),
            RequiredSkill(name="Machine Learning", weight=5)
        ],
        optional_skills=["Power BI", "Tableau"]
    )

    result = calculate_match(user, career)

    assert result.match_percentage == 52.94

    assert result.matched_required_skills == [
        "Python",
        "SQL"
    ]

    assert result.missing_required_skills == [
        "Statistics",
        "Machine Learning"
    ]

    assert result.matched_optional_skills == []

    print("Career matching test passed!")
    print(result.model_dump())


if __name__ == "__main__":
    test_calculate_match()
