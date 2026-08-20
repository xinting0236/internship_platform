"""
matcher.py
----------
Feature 1: AI Internship Matcher
Feature 2: AI "Should I Apply?" Decision
Feature 3: Skill Gap Analyzer

All three features share the same underlying weighted-overlap scoring
engine, so they live together here. Every score comes with a plain
-English "why" so the recommendation is never a black box.
"""

from services.skill_bank import extract_skills_from_text, learnability_of

# ---- Tunable weights -------------------------------------------------
W_SKILLS = 0.65          # weight of skill match in the overall score
W_EXPERIENCE = 0.15       # weight of experience-level fit
W_INTEREST_LOCATION = 0.20  # weight of interest/location/degree fit


def student_skill_set(student: dict) -> set:
    """Union of skills typed into the profile + skills detected in the CV."""
    profile_skills = extract_skills_from_text(student.get("skills_text", ""))
    cv_skills = extract_skills_from_text(student.get("cv_text", ""))
    return profile_skills | cv_skills


def compute_match(student: dict, internship: dict) -> dict:
    """
    Returns a full match report:
      score (0-100), matched_skills, missing_skills (weighted),
      experience_fit, interest_fit, breakdown text
    """
    s_skills = student_skill_set(student)
    required = internship["required_skills"]        # {skill: weight 1-3}
    nice_to_have = internship.get("nice_to_have_skills", {})

    # --- Skill component ---
    total_weight = sum(required.values()) or 1
    matched_weight = 0
    matched, missing = [], []
    for skill, weight in required.items():
        if skill in s_skills:
            matched_weight += weight
            matched.append(skill)
        else:
            missing.append({"skill": skill, "weight": weight,
                             "learn_effort": learnability_of(skill)})
    skill_score = matched_weight / total_weight  # 0..1

    bonus = sum(0.5 for skill in nice_to_have if skill in s_skills)
    skill_score = min(1.0, skill_score + bonus * 0.05)

    # --- Experience component ---
    exp_map = {"none": 0, "some": 1, "solid": 2}
    student_exp = exp_map.get(student.get("experience_level", "none"), 0)
    required_exp = exp_map.get(internship.get("experience_level", "none"), 0)
    if student_exp >= required_exp:
        experience_score = 1.0
    elif required_exp - student_exp == 1:
        experience_score = 0.55
    else:
        experience_score = 0.2

    # --- Interest / location / degree fit ---
    interest_score = 0.5
    interests = [i.strip().lower() for i in student.get("interests", "").split(",") if i.strip()]
    if internship["category"].lower() in interests:
        interest_score += 0.3
    student_location = student.get("location", "").strip().lower()
    internship_state = internship.get("state", internship["location"]).strip().lower()
    if internship["location"].lower() == "remote" or student_location == internship_state \
       or (student_location and student_location in internship["location"].lower()):
        interest_score += 0.2
    interest_score = min(1.0, interest_score)

    final = (skill_score * W_SKILLS +
             experience_score * W_EXPERIENCE +
             interest_score * W_INTEREST_LOCATION)
    score_pct = round(final * 100)

    missing.sort(key=lambda m: (-m["weight"], m["learn_effort"]))

    return {
        "score": score_pct,
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_score": round(skill_score * 100),
        "experience_score": round(experience_score * 100),
        "interest_score": round(interest_score * 100),
    }


def should_apply_decision(match: dict) -> dict:
    """
    Feature 2: Apply / Improve First / Skip, with a human-readable reason.
    """
    score = match["score"]
    critical_missing = [m for m in match["missing_skills"] if m["weight"] >= 3]

    if score >= 75 and not critical_missing:
        label, tone = "Apply", "success"
        reason = ("You meet most of the requirements and have no critical "
                   "skill gaps. This is a strong match worth your time.")
    elif score >= 50:
        label, tone = "Improve First", "warning"
        top_gap = match["missing_skills"][0]["skill"] if match["missing_skills"] else None
        reason = (f"You meet some requirements, but a gap in "
                   f"'{top_gap}' is holding your score back. "
                   "Close that gap (or highlight a related project) before applying "
                   "for the best chance.") if top_gap else \
                  "Your overall fit is moderate - strengthen your profile before applying."
    else:
        label, tone = "Skip", "danger"
        reason = ("The gap between your current profile and this role's "
                   "requirements is large right now. Your time is likely "
                   "better spent on closer matches, or come back after "
                   "building the missing skills.")

    return {"label": label, "tone": tone, "reason": reason}


def priority_tier(score: int) -> dict:
    """Feature (bonus): Application Priority Ranking badge for list views."""
    if score >= 80:
        return {"emoji": "🥇", "label": "Apply First"}
    if score >= 60:
        return {"emoji": "🥈", "label": "Good Option"}
    if score >= 40:
        return {"emoji": "🥉", "label": "Consider Later"}
    return {"emoji": "❌", "label": "Low Match"}


def rank_internships(student: dict, internships: list) -> list:
    """Returns internships annotated with match + decision + tier, sorted best-first."""
    results = []
    for i in internships:
        match = compute_match(student, i)
        decision = should_apply_decision(match)
        tier = priority_tier(match["score"])
        results.append({**i, "match": match, "decision": decision, "tier": tier})
    results.sort(key=lambda r: r["match"]["score"], reverse=True)
    return results
