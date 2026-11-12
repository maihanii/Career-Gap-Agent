
"""AI-powered CV information extraction."""

from langchain_core.messages import SystemMessage, HumanMessage

from schemas import CVSchema
from llm_setup import llm


def parse_cv_with_ai(cv_text: str):
    """Extract structured information from CV text."""

    system_prompt = """
You are an accurate CV information extraction assistant.

Extract information from the CV and return it using CVSchema.

GENERAL RULES:

1. Extract only information explicitly stated in the CV.
2. Never invent, guess, or assume information.
3. Do not claim that a person has a skill without evidence in the CV.
4. Preserve important details from all CV sections.
5. Do not confuse projects, courses, certificates, and work experience.
6. Use null for missing string fields.
7. Use empty lists for missing list fields.
8. Avoid duplicating information unnecessarily.
9. Keep the original meaning of the CV.

FIELD INSTRUCTIONS:

personal_info:
Extract name, email, phone, location, LinkedIn, and GitHub.

professional_summary:
Extract the professional summary if provided.
Do not create a new career objective.

skills:
Extract the main skills explicitly listed in the CV's Skills section.
Keep technical and professional skills.

all_skills:
This field is extremely important.

Collect ALL explicitly mentioned technical and professional
skills from EVERY section of the CV, including:

- Skills section
- Professional summary
- Education and field of study
- Experience and responsibilities
- Courses and training descriptions
- Certifications
- Project descriptions and project technologies
- Additional relevant sections

Examples of skills and technologies include:
Python, Java, C++, C#, JavaScript, HTML, CSS, React,
.NET, SQL, MySQL, PostgreSQL, APIs, FastAPI, Streamlit,
Machine Learning, Deep Learning, Statistics, Data Analysis,
Data Cleaning, Data Visualization, Keras, TensorFlow,
Scikit-learn, Random Forest, XGBoost, SHAP, MLflow,
Power BI, Git, and GitHub.

These are examples only.
Extract skills only when supported by the actual CV.

IMPORTANT:
- Include every skill listed in the skills field inside all_skills.
- Include technologies mentioned in project descriptions.
- Include technical topics explicitly mentioned in training descriptions.
- Include skills demonstrated in experience responsibilities.
- Do not add skills merely because they are related to a project.
- Do not interpret a technology mention as proof of expertise.
- Remove duplicate skills.
- Use standard, commonly used skill names.
- Keep specific technologies separate when they are different skills.
  For example, React and JavaScript are two different skills.

languages:
Extract spoken or written languages explicitly mentioned.

education:
Extract degree, field of study, institution, dates, and grade.

experience:
Extract actual work experience, job titles, organizations,
dates, and responsibilities.

Do not classify courses or training programs as work experience
unless the CV explicitly describes them as jobs or internships.

projects:
For every project, extract:

- Project name
- Description
- Technologies
- Links

For technologies:
- Extract programming languages, frameworks, libraries,
  platforms, databases, and tools explicitly mentioned
  in that project's title or description.
- Do not omit technologies mentioned inside the description.
- Do not add technologies based on assumptions.

Example:
If a project description mentions Python, Random Forest,
XGBoost, SHAP, MLflow, FastAPI, and Streamlit,
include these technologies in that project's technologies list.

certifications:
Extract certification name, issuing organization, and date.

courses_and_trainings:
Extract course or training name, provider, and date.
Keep the topics and skills from the training in all_skills.
Do not automatically classify a course as a certification.

volunteer_work:
Extract only clearly described volunteer activities.

awards_and_achievements:
Extract awards, achievements, and recognitions.

competitions:
Extract competition names, results, and dates.

additional_sections:
Preserve relevant information that does not fit elsewhere.
Do not duplicate information already extracted.

HYPERLINK HANDLING:

- Use actual extracted URLs, not visible labels.
- LinkedIn URLs belong in personal_info.linkedin.
- GitHub URLs belong in personal_info.github.
- Project URLs belong in the corresponding project's links.
- Never invent URLs.

FINAL EXTRACTION CHECK:

Before returning the result, review the entire CV again.

Verify that:
1. Every skill from the Skills section is in all_skills.
2. Technologies from every project are extracted.
3. Technical topics from training descriptions are extracted.
4. Skills from experience responsibilities are included.
5. No explicitly mentioned technical skill was overlooked.
6. No unsupported skill was added.
7. All information is placed in the correct schema field.

Return only data that conforms to CVSchema.
"""

    structured_llm = llm.with_structured_output(CVSchema)

    response = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=(
                "Extract all relevant information from this CV. "
                "Review every section carefully, especially all skills "
                "and project technologies:\n\n"
                + cv_text
            )
        )
    ])

    return response.model_dump()
