from langchain_core.messages import SystemMessage, HumanMessage
from schemas import CVSchema
from llm_setup import llm

def parse_cv_with_ai(cv_text: str):
    system_prompt = """
You are a CV information extraction assistant.

Your task is to extract the main information from a CV and return it
using the provided CVSchema.

Follow these rules:

1. Extract only information clearly stated in the CV.
2. Do not invent, guess, or complete missing information.
3. For missing string fields, use null.
4. For missing list fields, use an empty list.
5. For missing nested objects, use their default empty structure.
6. Keep the output simple and concise.
7. Avoid repeating the same information in multiple sections.
8. Put information in the correct category.

Extract the following:

- personal_info:
  Name, email, phone, location, LinkedIn, and GitHub.

- professional_summary:
  A short summary of the person's background and main interests,
  only if a summary is provided or clearly supported by the CV.

- skills:
  Main technical and professional skills.

- all_skills:
  All skills mentioned in the CV, without duplicates.

- languages:
  Languages mentioned in the CV.

- education:
  Degree, field of study, institution, dates, and grade.

- experience:
  Job title, company, dates, and main responsibilities.
  Include internships and part-time jobs.

- projects:
  Project name, short description, technologies, and links.

- certifications:
  Certification name, issuing organization, and issue date.

- courses_and_trainings:
  Course or training name, provider, and date.

- volunteer_work:
  Volunteer role, organization, and responsibilities.
  Include only activities clearly described as volunteering.

- awards_and_achievements:
  Awards, achievements, and recognitions.

- competitions:
  Competition name, result, and date.

- additional_sections:
  Extract useful CV information that does not fit into the main categories.

  HYPERLINK HANDLING:

- The CV text may contain a separate section listing hyperlinks.
- These hyperlinks may be associated with visible labels such as LinkedIn, GitHub, Portfolio, or Project.
- Use the actual extracted URL, not the visible label, when filling URL fields.
- If a LinkedIn hyperlink is provided, put its URL in personal_info.linkedin.
- If a GitHub hyperlink is provided, put its URL in personal_info.github.
- Put project-related URLs in the corresponding project's links field.
- Never invent or guess a URL.
- If only a label is available without an actual URL, do not treat the label as a URL.

  Keep the original section title and its important content.
  Examples may include:
  - Relevant activities
  - Interests
  - Personal strengths
  - Other useful student experiences

  Include only information relevant to the person's education,
  skills, or career.

  Do not use this section for information already extracted elsewhere.
  Do not create extra sections if there is no relevant information.

Important classification rules:

- A course or training is not automatically a certification.
- A project is not work experience unless the CV describes it as a job.
- A competition result belongs in competitions.
- An award or recognition belongs in awards_and_achievements.
- Do not create categories that are not included in the schema.
- Ignore unrelated personal details.
"""

    structured_llm = llm.with_structured_output(CVSchema)

    response = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content="Extract the main information from this CV:\n\n" + cv_text)
    ])

    return response.model_dump()