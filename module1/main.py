import json
import os

from database import initialize_database
from profile_agent import process_cv_file


def process_cv(file_path: str):
    cv = process_cv_file(file_path)

    # Save JSON copy
    json_filename = os.path.splitext(os.path.basename(file_path))[0] + ".json"
    with open(json_filename, "w", encoding="utf-8") as file:
        json.dump(cv["extracted_data"], file, indent=4, ensure_ascii=False)

    print(f"\nCV saved successfully! ID: {cv['id']}")
    print("\nExtracted CV Information:")
    print(json.dumps(cv["extracted_data"], indent=4, ensure_ascii=False))

    return cv


def main():
    initialize_database()

    file_path = r"C:\Users\hom\Documents\MaiHaniRamadan_CVv.pdf"
    process_cv(file_path)


if __name__ == "__main__":
    main()