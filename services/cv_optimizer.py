"""
cv_optimizer.py
----------------
Feature 4: AI CV Optimizer
Compares the student's CV text against a specific internship's
requirements and suggests what to add / emphasize / trim.
Never invents experience the student didn't provide - it only
reorders emphasis, suggests phrasing, and flags missing keywords.
"""

from services.skill_bank import extract_skills_from_text, category_of

BULLET_TEMPLATES = {
    "technical": "Applied {skill} to solve a real problem (e.g. a class project, "
                 "personal project, or coursework) - quantify the result if you can "
                 "(time saved, accuracy, size of dataset, users reached).",
    "soft": "Demonstrated {skill} while working in a team, club, or part-time role - "
            "describe the situation, your action, and the outcome (S-A-R format).",
}

ATS_TIP = ("Recruiting software often scans for exact keywords. Make sure the "
           "skill name itself (not just a related tool) appears somewhere in "
           "your CV - in your skills list, a project bullet, or a course title.")


def analyze_cv(student: dict, internship: dict) -> dict:
    cv_text = student.get("cv_text", "")
    cv_skills = extract_skills_from_text(cv_text)
    profile_skills = extract_skills_from_text(student.get("skills_text", ""))
    have = cv_skills | profile_skills

    required = internship["required_skills"]
    missing_in_cv = []
    present_but_not_in_cv = []
    for skill, weight in sorted(required.items(), key=lambda kv: -kv[1]):
        if skill in cv_skills:
            continue
        elif skill in profile_skills:
            # student claims to have it but it's not written in the CV text
            present_but_not_in_cv.append(skill)
        else:
            missing_in_cv.append({"skill": skill, "weight": weight,
                                   "category": category_of(skill),
                                   "suggestion": BULLET_TEMPLATES[category_of(skill)].format(skill=skill)})

    # Things to potentially trim: very generic filler phrases
    filler_phrases = ["hard worker", "team player", "detail oriented", "fast learner"]
    lower_cv = cv_text.lower()
    trim_suggestions = [p for p in filler_phrases if p in lower_cv]

    word_count = len(cv_text.split())
    length_tip = None
    if word_count == 0:
        length_tip = "No CV text was provided yet - paste your CV to get tailored suggestions."
    elif word_count < 120:
        length_tip = "Your CV looks quite short - consider adding 1-2 more project or experience bullets."
    elif word_count > 900:
        length_tip = "Your CV is long for an internship application - aim to trim it to one page (roughly 400-600 words)."

    match_keywords_present = [s for s in required if s in have]
    ats_score = round(100 * len(match_keywords_present) / max(1, len(required)))

    return {
        "missing_in_cv": missing_in_cv,
        "present_but_not_in_cv": present_but_not_in_cv,
        "trim_suggestions": trim_suggestions,
        "length_tip": length_tip,
        "ats_score": ats_score,
        "ats_tip": ATS_TIP,
        "word_count": word_count,
    }
