import re
import unicodedata

SKILL_ALIASES = {
    "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "ms excel": "Microsoft Excel",
    "microsoft excel": "Microsoft Excel",
    "py torch": "PyTorch",
}

def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def normalize_skills(skills: list[str]) -> list[str]:
    normalized = []
    seen = set()

    for skill in skills:
        if not isinstance(skill, str):
            continue

        original = normalize_text(skill)
        if not original:
            continue

        key = original.casefold()

        canonical = SKILL_ALIASES.get(key, original)
        canonical_key = canonical.casefold()

        if canonical_key not in seen:
            normalized.append(canonical)
            seen.add(canonical_key)

    return normalized