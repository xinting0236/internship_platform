"""
skill_bank.py
--------------
Master list of skills the platform understands, plus lightweight
normalization / synonym handling. This is the backbone of the
"AI" matching engine: everything (student skills, CV text, internship
requirements) gets mapped onto this common vocabulary so scores are
comparable.

No external NLP libraries are required - matching is done through
normalized keyword lookup + synonym expansion, which is fast, fully
explainable (important for the "Why" behind every recommendation)
and needs no internet access / API key to run.
"""

import re

# skill -> list of synonyms / alternate spellings that should map to it
SKILL_SYNONYMS = {
    "python": ["python", "py"],
    "sql": ["sql", "mysql", "postgresql", "postgres", "t-sql"],
    "excel": ["excel", "ms excel", "spreadsheets", "google sheets"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "data analysis": ["data analysis", "data analytics", "analyzing data"],
    "machine learning": ["machine learning", "ml", "scikit-learn", "sklearn"],
    "deep learning": ["deep learning", "neural networks", "pytorch", "tensorflow"],
    "statistics": ["statistics", "statistical analysis", "stats"],
    "java": ["java"],
    "javascript": ["javascript", "js", "node.js", "nodejs"],
    "react": ["react", "react.js", "reactjs"],
    "html/css": ["html", "css", "html/css", "html5", "css3"],
    "c++": ["c++", "cpp"],
    "c": ["c programming", " c "],
    "git": ["git", "github", "gitlab", "version control"],
    "api development": ["api", "rest api", "restful", "api development"],
    "cloud computing": ["aws", "azure", "gcp", "cloud", "cloud computing"],
    "docker": ["docker", "containers", "containerization"],
    "project management": ["project management", "agile", "scrum", "kanban"],
    "communication": ["communication", "presentation skills", "public speaking"],
    "teamwork": ["teamwork", "collaboration", "cross-functional"],
    "marketing": ["marketing", "digital marketing", "seo", "social media marketing"],
    "content writing": ["content writing", "copywriting", "content creation"],
    "ui/ux design": ["ui/ux", "ux design", "ui design", "user experience", "figma", "wireframing"],
    "financial modeling": ["financial modeling", "financial analysis", "valuation"],
    "accounting": ["accounting", "bookkeeping", "gaap"],
    "excel vba": ["vba", "excel vba", "macros"],
    "r": ["r programming", " r "],
    "product management": ["product management", "product strategy", "roadmapping"],
    "customer service": ["customer service", "client support"],
    "leadership": ["leadership", "team lead", "managed a team"],
    "problem solving": ["problem solving", "analytical thinking", "critical thinking"],
    "research": ["research", "market research", "academic research"],
}

# Skills grouped by category (useful for interview-question selection & CV tips)
SKILL_CATEGORY = {
    "python": "technical", "sql": "technical", "excel": "technical",
    "power bi": "technical", "tableau": "technical", "data analysis": "technical",
    "machine learning": "technical", "deep learning": "technical", "statistics": "technical",
    "java": "technical", "javascript": "technical", "react": "technical",
    "html/css": "technical", "c++": "technical", "c": "technical", "git": "technical",
    "api development": "technical", "cloud computing": "technical", "docker": "technical",
    "excel vba": "technical", "r": "technical", "financial modeling": "technical",
    "accounting": "technical", "ui/ux design": "technical", "content writing": "technical",
    "marketing": "technical", "product management": "technical",
    "project management": "soft", "communication": "soft", "teamwork": "soft",
    "customer service": "soft", "leadership": "soft", "problem solving": "soft",
    "research": "soft",
}

# Rough "how quickly can this be learned" weighting used by the CV / skill-gap
# advice engine (1 = quick to pick up, 3 = takes a while) - purely heuristic.
LEARNABILITY = {
    "power bi": 1, "tableau": 1, "excel": 1, "git": 1, "html/css": 1,
    "excel vba": 2, "sql": 2, "python": 2, "r": 2, "cloud computing": 2,
    "docker": 2, "financial modeling": 2, "ui/ux design": 2,
    "machine learning": 3, "deep learning": 3, "statistics": 2,
    "java": 2, "javascript": 2, "react": 2, "c++": 3, "c": 2,
    "product management": 2, "marketing": 2, "content writing": 1,
    "accounting": 2, "communication": 1, "teamwork": 1, "leadership": 2,
    "problem solving": 2, "research": 1, "project management": 1,
    "customer service": 1, "api development": 2,
}

ALL_SKILLS = sorted(SKILL_SYNONYMS.keys())


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def extract_skills_from_text(text: str):
    """
    Scan free text (CV paste, profile 'skills' field, internship description)
    and return the set of canonical skill names found in it.
    """
    if not text:
        return set()
    norm = " " + _normalize(text) + " "
    found = set()
    for canonical, synonyms in SKILL_SYNONYMS.items():
        for syn in synonyms:
            pattern = r"(?<![a-z0-9])" + re.escape(syn.strip()) + r"(?![a-z0-9])"
            if re.search(pattern, norm):
                found.add(canonical)
                break
    return found


def category_of(skill: str) -> str:
    return SKILL_CATEGORY.get(skill, "technical")


def learnability_of(skill: str) -> int:
    return LEARNABILITY.get(skill, 2)
