
"""Validates extracted CV information against the original CV text."""

import re
import unicodedata


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""

    text = unicodedata.normalize("NFKC", text)
    text = text.casefold()
    text = re.sub(r"[^\w\s+#.]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def is_supported(value: str, cv_text: str) -> bool:
    """Check whether a value appears in the original CV text."""

    normalized_value = normalize_text(value)
    normalized_cv = normalize_text(cv_text)

    if not normalized_value:
        return True

    return normalized_value in normalized_cv


def validate_profile(cv_text: str, profile_data: dict) -> dict:
    """
    Compare extracted profile information with the original CV.

    Unsupported information is reported as a warning,
    not automatically rejected.
    """

    issues = []
    warnings = []

    total_checks = 0
    passed_checks = 0

    def check_value(value, field_name):
        nonlocal total_checks, passed_checks

        if not isinstance(value, str) or not value.strip():
            return

        total_checks += 1

        if is_supported(value, cv_text):
            passed_checks += 1
        else:
            warnings.append({
                "field": field_name,
                "value": value,
                "message": "This information was not found directly in the CV text."
            })

    def check_list(values, field_name):
        if not isinstance(values, list):
            issues.append({
                "field": field_name,
                "message": "Expected a list."
            })
            return

        for index, value in enumerate(values):
            if isinstance(value, str):
                check_value(value, f"{field_name}[{index}]")

    # 1. Validate personal information
    personal_info = profile_data.get("personal_info", {})

    if isinstance(personal_info, dict):
        for field, value in personal_info.items():
            if field in {"linkedin", "github"}:
                # URLs may be extracted from document hyperlinks
                # and are not always present in the extracted CV text.
                continue

            check_value(value, f"personal_info.{field}")

    else:
        issues.append({
            "field": "personal_info",
            "message": "Expected an object."
        })

    # 2. Validate simple list fields
    for field in ["skills", "all_skills", "languages"]:
        check_list(profile_data.get(field, []), field)

    # 3. Check duplicate skills
    skills = profile_data.get("skills", [])

    if isinstance(skills, list):
        normalized_skills = [
            normalize_text(skill)
            for skill in skills
            if isinstance(skill, str)
        ]

        if len(normalized_skills) != len(set(normalized_skills)):
            issues.append({
                "field": "skills",
                "message": "Duplicate skills were found."
            })

    # 4. Validate professional summary
    summary = profile_data.get("professional_summary")

    if summary:
        check_value(summary, "professional_summary")

    # 5. Validate structured sections
    sections = {
        "education": ["degree", "field_of_study", "institution", "grade"],
        "experience": ["job_title", "company", "responsibilities"],
        "projects": ["name", "description", "technologies", "links"],
        "certifications": ["name", "issuer"],
        "courses_and_trainings": ["name", "provider"],
        "volunteer_work": ["role", "organization", "responsibilities"],
        "awards_and_achievements": ["title", "description"],
        "competitions": ["name", "result"],
        "additional_sections": ["title", "content"]
    }

    for section, fields in sections.items():

        items = profile_data.get(section, [])

        if not isinstance(items, list):
            issues.append({
                "field": section,
                "message": "Expected a list."
            })
            continue

        for index, item in enumerate(items):

            if not isinstance(item, dict):
                issues.append({
                    "field": f"{section}[{index}]",
                    "message": "Expected an object."
                })
                continue

            for field in fields:
                value = item.get(field)

                field_name = f"{section}[{index}].{field}"

                if isinstance(value, str):
                    check_value(value, field_name)

                elif isinstance(value, list):
                    check_list(value, field_name)

    return {
        "is_valid": len(issues) == 0 and len(warnings) == 0,
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "unsupported_count": len(warnings),
        "issues_count": len(issues),
        "issues": issues,
        "warnings": warnings
    }
