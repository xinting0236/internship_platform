"""
app.py
------
AI Internship Decision & Career Assistant - Flask entrypoint.

Implements the 5 MVP features:
  1. AI Internship Matcher      -> /internships
  2. Should I Apply? Decision   -> /internship/<id>
  3. Skill Gap Analyzer         -> /internship/<id>
  4. AI CV Optimizer            -> /internship/<id>/cv-optimizer
  5. AI Interview Preparation   -> /internship/<id>/interview-prep

Run with:  python app.py
Then open  http://localhost:5000
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import date

import database as db
from services.matcher import compute_match, should_apply_decision, priority_tier, rank_internships
from services.cv_optimizer import analyze_cv
from services.interview_prep import generate_interview_set

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-me"  # fine for a course MVP demo


@app.before_request
def ensure_db():
    db.init_db()


def current_student():
    return db.get_student(session.get("student_id"))


@app.context_processor
def inject_student():
    return {"current_student": current_student()}


# ---------------------------------------------------------------- Home
@app.route("/")
def index():
    student = current_student()
    if not student:
        return redirect(url_for("profile"))
    internships = db.load_internships()
    ranked = rank_internships(student, internships)
    top_matches = ranked[:3]
    applications = db.get_applications(student["id"])
    return render_template("index.html", student=student, top_matches=top_matches,
                            application_count=len(applications))


# ---------------------------------------------------------------- Profile (student input)
@app.route("/profile", methods=["GET", "POST"])
def profile():
    student = current_student()
    if request.method == "POST":
        data = {
            "name": request.form.get("name", "").strip() or "Student",
            "degree": request.form.get("degree", "").strip(),
            "location": request.form.get("location", "").strip(),
            "interests": request.form.get("interests", "").strip(),
            "experience_level": request.form.get("experience_level", "none"),
            "skills_text": request.form.get("skills_text", "").strip(),
            "cv_text": request.form.get("cv_text", "").strip(),
        }
        student_id = db.create_or_update_student(session.get("student_id"), data)
        session["student_id"] = student_id
        flash("Profile saved!", "success")
        return redirect(url_for("internships"))
    return render_template("profile.html", student=student)


# ---------------------------------------------------------------- Feature 1: Matcher (list)
@app.route("/internships")
def internships():
    student = current_student()
    if not student:
        return redirect(url_for("profile"))
    all_internships = db.load_internships()
    ranked = rank_internships(student, all_internships)

    category = request.args.get("category")
    if category:
        ranked = [r for r in ranked if r["category"] == category]

    categories = sorted({i["category"] for i in all_internships})
    applications = {a["internship_id"]: a["status"] for a in db.get_applications(student["id"])}
    return render_template("internships.html", ranked=ranked, categories=categories,
                            selected_category=category, applications=applications)


# ---------------------------------------------------------------- Feature 2 & 3: Match detail
@app.route("/internship/<int:internship_id>")
def internship_detail(internship_id):
    student = current_student()
    if not student:
        return redirect(url_for("profile"))
    internship = db.get_internship(internship_id)
    if not internship:
        flash("Internship not found.", "danger")
        return redirect(url_for("internships"))

    match = compute_match(student, internship)
    decision = should_apply_decision(match)
    tier = priority_tier(match["score"])
    status = db.get_application_status(student["id"], internship_id)

    return render_template("match_detail.html", internship=internship, match=match,
                            decision=decision, tier=tier, status=status)


# ---------------------------------------------------------------- Feature 4: CV Optimizer
@app.route("/internship/<int:internship_id>/cv-optimizer")
def cv_optimizer(internship_id):
    student = current_student()
    if not student:
        return redirect(url_for("profile"))
    internship = db.get_internship(internship_id)
    if not internship:
        flash("Internship not found.", "danger")
        return redirect(url_for("internships"))
    analysis = analyze_cv(student, internship)
    return render_template("cv_optimizer.html", internship=internship, analysis=analysis)


# ---------------------------------------------------------------- Feature 5: Interview Prep
@app.route("/internship/<int:internship_id>/interview-prep")
def interview_prep(internship_id):
    student = current_student()
    if not student:
        return redirect(url_for("profile"))
    internship = db.get_internship(internship_id)
    if not internship:
        flash("Internship not found.", "danger")
        return redirect(url_for("internships"))
    match = compute_match(student, internship)
    prep = generate_interview_set(internship, match["missing_skills"])
    return render_template("interview_prep.html", internship=internship, prep=prep)


# ---------------------------------------------------------------- Application tracker (bonus)
@app.route("/internship/<int:internship_id>/track", methods=["POST"])
def track_application(internship_id):
    student = current_student()
    if not student:
        return redirect(url_for("profile"))
    status = request.form.get("status", "Saved")
    applied_date = date.today().isoformat() if status == "Applied" else None
    db.upsert_application(student["id"], internship_id, status, applied_date)
    flash(f"Marked as '{status}'.", "success")
    return redirect(request.referrer or url_for("internships"))


@app.route("/tracker")
def tracker():
    student = current_student()
    if not student:
        return redirect(url_for("profile"))
    apps = db.get_applications(student["id"])
    all_internships = {i["id"]: i for i in db.load_internships()}
    enriched = []
    for a in apps:
        internship = all_internships.get(a["internship_id"])
        if internship:
            enriched.append({**a, "internship": internship})
    return render_template("tracker.html", applications=enriched)


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
