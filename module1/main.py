import json
import os
from cv_parser import read_cv
from skill_normalizer import normalize_skills
from ai_parser import parse_cv_with_ai
from database import initialize_database, save_cv, get_cv

def process_cv(file_path: str):

    cv_text = read_cv(file_path)

    if not cv_text:
        raise ValueError("No text found in the CV. It may be scanned.")

    result = parse_cv_with_ai(cv_text)

    result["skills"] = normalize_skills(result["skills"])
    result["all_skills"] = normalize_skills(result["all_skills"])

    # Save CV in database
    filename = os.path.basename(file_path)
    cv_id = save_cv(filename, result)

    # Save JSON copy
    json_filename = os.path.splitext(filename)[0] + ".json"

    with open(json_filename, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    # Retrieve saved CV
    cv = get_cv(cv_id)

    print(f"\nCV saved successfully! ID: {cv_id}")
    print("\nExtracted CV Information:")
    print(json.dumps(cv["extracted_data"], indent=4, ensure_ascii=False))

    return cv


def main():

    # Initialize database
    initialize_database()

    file_path = r"C:\Users\moham\Downloads\Ahmed-Madeh-Resume.pdf"
    process_cv(file_path)


if __name__ == "__main__":
    main()