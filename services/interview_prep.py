"""
interview_prep.py
------------------
Feature 5: AI Interview Preparation
Generates a tailored question set for a specific internship, based on
its required skills, category, and the student's own gaps (so weak
spots get practiced, not just strengths).
"""

from services.skill_bank import category_of

GENERAL_BEHAVIORAL = [
    "Tell me about yourself and why you're interested in this internship.",
    "Describe a time you worked in a team to solve a problem. What was your role?",
    "Tell me about a time you faced a setback or failure. What did you learn?",
    "Why do you want to work at this company specifically?",
    "Where do you see yourself developing over the next 1-2 years?",
]

SKILL_QUESTION_BANK = {
    "python": [
        "Walk me through a Python project you've built - what problem did it solve?",
        "How would you read and clean a messy CSV file in Python?",
    ],
    "sql": [
        "Write (or describe) a SQL query to find duplicate rows in a table.",
        "What's the difference between an INNER JOIN and a LEFT JOIN?",
    ],
    "excel": [
        "How would you use Excel to summarize sales data by region?",
        "What's the difference between VLOOKUP and INDEX/MATCH?",
    ],
    "power bi": [
        "How would you design a dashboard for a non-technical manager?",
        "What's the difference between a measure and a calculated column in Power BI?",
    ],
    "data analysis": [
        "Describe a time you found an insight in data that changed a decision.",
        "How do you check whether a dataset is reliable before analyzing it?",
    ],
    "machine learning": [
        "Explain overfitting to someone with no ML background.",
        "How would you decide which model to use for a classification problem?",
    ],
    "marketing": [
        "How would you measure whether a marketing campaign was successful?",
        "Describe a campaign (real or hypothetical) you'd run to reach students.",
    ],
    "ui/ux design": [
        "Walk me through your design process from brief to final mockup.",
        "How do you decide what feedback to act on during user testing?",
    ],
    "financial modeling": [
        "Walk me through how you'd build a simple 3-statement financial model.",
        "What assumptions matter most when forecasting revenue?",
    ],
    "product management": [
        "How would you prioritize a backlog with limited engineering time?",
        "Describe how you'd gather requirements for a new feature.",
    ],
}

DEFAULT_TECHNICAL_Q = "Tell me about a project where you used {skill}. What was your specific contribution?"


def generate_interview_set(internship: dict, missing_skills=None) -> dict:
    required = list(internship["required_skills"].keys())
    missing_skills = {m["skill"] for m in (missing_skills or [])}

    technical_questions = []
    for skill in required:
        bank = SKILL_QUESTION_BANK.get(skill)
        if bank:
            technical_questions.append({"skill": skill, "question": bank[0],
                                         "practice_gap": skill in missing_skills})
        else:
            technical_questions.append({
                "skill": skill,
                "question": DEFAULT_TECHNICAL_Q.format(skill=skill),
                "practice_gap": skill in missing_skills,
            })

    role_question = (f"What excites you about the {internship['title']} role at "
                      f"{internship['company']}, specifically?")

    tips = []
    if missing_skills:
        tips.append("You have a gap in " + ", ".join(sorted(missing_skills)) +
                     " - be ready to explain how you'd get up to speed quickly, "
                     "or point to a related skill/project instead of avoiding the topic.")
    tips.append("Use the STAR method (Situation, Task, Action, Result) for behavioral questions.")
    tips.append("Prepare 2-3 questions to ask the interviewer about the team or role.")

    return {
        "role_question": role_question,
        "technical_questions": technical_questions,
        "behavioral_questions": GENERAL_BEHAVIORAL,
        "tips": tips,
    }
