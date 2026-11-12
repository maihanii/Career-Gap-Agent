
"""Career Discovery Agent."""

from module2.schemas import UserSkills, CareerDiscoveryResponse
from module2.career_loader import load_careers
from module2.career_matcher import calculate_match


def discover_careers(
    user: UserSkills,
    top_n: int = 5
) -> CareerDiscoveryResponse:
    """
    Discover and rank suitable careers based on user skills.
    """

    if top_n < 1:
        raise ValueError("top_n must be at least 1.")

    # Load all available careers.
    careers = load_careers()

    # Calculate the match for every career.
    results = [
        calculate_match(user, career)
        for career in careers
    ]

    # Sort careers from highest to lowest match.
    results.sort(
        key=lambda result: result.match_percentage,
        reverse=True
    )

    # Keep only the top recommendations.
    recommendations = results[:top_n]

    return CareerDiscoveryResponse(
        cv_id=user.cv_id,
        recommendations=recommendations
    )
