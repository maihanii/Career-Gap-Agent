
from module2.schemas import UserSkills
from module2.career_discovery_agent import discover_careers


def test_discover_careers():

    user = UserSkills(
        cv_id=11,
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
            "Data Analysis",
            "Statistics"
        ]
    )

    result = discover_careers(user, top_n=5)

    assert result.cv_id == 11
    assert len(result.recommendations) == 5

    # Check that recommendations are sorted by match percentage.
    scores = [
        career.match_percentage
        for career in result.recommendations
    ]

    assert scores == sorted(scores, reverse=True)

    print("\nCareer Recommendations:")

    for career in result.recommendations:
        print(
            career.title,
            "-",
            career.match_percentage,
            "%"
        )

    print("\nCareer Discovery test passed!")


if __name__ == "__main__":
    test_discover_careers()
