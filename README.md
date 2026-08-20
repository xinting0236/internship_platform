# AI Internship Decision & Career Assistant

**"Stop wasting time applying to internships you're unlikely to get. AI tells you
which opportunities are worth applying for and what you need to improve."**

A Python/Flask MVP built for the AI Venture course, implementing the 5 core
features from the product plan:

1. **AI Internship Matcher** — matches internship listings to the student's skills, degree, interests, and location.
2. **Should I Apply? Decision** — gives a match score and an Apply / Improve First / Skip recommendation, with a plain-English reason.
3. **Skill Gap Analyzer** — shows exactly which required skills are missing, ranked by how much they impact the application and how hard they are to learn.
4. **AI CV Optimizer** — compares the student's CV against a specific internship's requirements and suggests what to add, emphasize, or trim — without inventing experience.
5. **AI Interview Preparation** — generates technical and behavioral interview questions tailored to the specific role and the student's skill gaps.

A basic **Application Tracker** (Saved / Applied / Interview / Accepted / Rejected)
is included as a bonus, matching the roadmap's tracker idea.

## How the "AI" works

There's no external LLM API call in this MVP — matching, decisions, CV
tips, and interview questions are all produced by an explainable, rule-based
scoring engine (`services/matcher.py`, `services/cv_optimizer.py`,
`services/interview_prep.py`) built on a shared skill vocabulary
(`services/skill_bank.py`). This keeps the app:

- **Fully explainable** — every recommendation shows its "why."
- **Free to run** — no API key or internet connection needed for the demo.
- **Easy to upgrade** — swap in a real LLM call (see `anthropic_api_in_artifacts`
  pattern, or the Anthropic/OpenAI Python SDK) inside those service files later
  without touching the routes or templates.

## Project structure

```
internship_platform/
├── app.py                     # Flask routes / entrypoint
├── database.py                # SQLite persistence (students, applications)
├── requirements.txt
├── data/
│   └── internships.json       # Seed internship listings
├── services/
│   ├── skill_bank.py          # Shared skill vocabulary + text parsing
│   ├── matcher.py              # Feature 1 & 2 & 3: matching, decision, gap analysis
│   ├── cv_optimizer.py         # Feature 4: CV tailoring
│   └── interview_prep.py       # Feature 5: interview question generation
├── templates/                 # Jinja2 HTML templates
└── static/css/style.css       # Styling
```

## Setup

```bash
cd internship_platform
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000** in your browser.

The SQLite database (`platform.db`) is created automatically on first run.

## Using the app

1. Go to **Profile** and enter your degree, interests, skills, and paste your CV text.
2. Go to **Matches** to see every internship ranked by fit, with a 🥇🥈🥉❌ priority badge.
3. Click into any internship to see:
   - Your match score breakdown
   - The **Should I Apply?** decision and reasoning
   - The **Skill Gap Analyzer**
   - The **CV Optimizer** tab
   - The **Interview Prep** tab
4. Use the status dropdown on the match page to track your application.

## Deploying publicly (Render)

1. Push this repo to GitHub (see the "uploading to GitHub" steps above).
2. Go to [render.com](https://render.com) and sign up (GitHub login works).
3. **New +** → **Web Service** → connect your GitHub repo.
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app` (already in the `Procfile`, Render usually detects it automatically)
5. Add an environment variable `SECRET_KEY` set to any random string (Render can generate one).
6. Click **Deploy**. You'll get a public URL like `https://your-app-name.onrender.com`.

**Note on the database:** this MVP uses SQLite (`platform.db`), which is fine for
a demo but is stored on the app's local disk. On Render's free tier that disk
is wiped whenever the service restarts or redeploys, so profiles/tracker data
won't persist long-term. That's fine for a course demo. If you need data to
persist for real users, swap SQLite for Render's free PostgreSQL add-on later
(only `database.py` needs to change).

## Extending this MVP

- Swap the seed `data/internships.json` for a real internship-listing API or scraper.
- Add real user accounts/auth (currently a single profile per browser session).
- Add feature 6–9 from the roadmap (Mock Interview simulation with AI feedback,
  Internship Comparison view, Personalized Skill Improvement Plan, Deadline reminders).
- Replace the rule-based engine with LLM calls for more nuanced CV feedback and
  interview question generation, using the extracted skills as structured context.
