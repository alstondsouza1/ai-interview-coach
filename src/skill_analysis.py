"""Rule-based skill extraction and resume-to-job comparison."""

from __future__ import annotations

import re

from src.models import SkillMatch

# This focused catalog covers common internship and junior software roles.
SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "AWS": ("aws", "amazon web services"),
    "Agile": ("agile", "scrum"),
    "C": ("c programming",),
    "C#": ("c#", "c sharp"),
    "C++": ("c++", "cpp"),
    "CSS": ("css", "css3"),
    "Communication": ("communication", "presented", "presentation"),
    "Data Structures": ("data structures",),
    "Django": ("django",),
    "Docker": ("docker", "containerization"),
    "Flask": ("flask",),
    "Git": ("git", "github", "gitlab"),
    "Google Cloud": ("gcp", "google cloud"),
    "HTML": ("html", "html5"),
    "Java": ("java",),
    "JavaScript": ("javascript",),
    "Kubernetes": ("kubernetes", "k8s"),
    "Linux": ("linux", "unix"),
    "Machine Learning": ("machine learning",),
    "MongoDB": ("mongodb", "mongo"),
    "Node.js": ("node.js", "nodejs"),
    "Object-Oriented Programming": (
        "object-oriented programming",
        "object oriented programming",
        "oop",
    ),
    "PostgreSQL": ("postgresql", "postgres"),
    "Python": ("python",),
    "React": ("react", "react.js", "reactjs"),
    "REST APIs": ("rest api", "restful api", "rest apis", "restful apis"),
    "Ruby": ("ruby",),
    "SQL": ("sql", "relational database"),
    "Teamwork": ("teamwork", "collaboration", "worked with a team"),
    "Testing": ("unit testing", "unit tests", "pytest", "junit", "testing"),
    "TypeScript": ("typescript",),
    "Vue.js": ("vue.js", "vuejs"),
}


def extract_skills(text: str) -> list[str]:
    """Return canonical skill names found in text."""

    normalized_text = text.casefold()
    found = [
        skill
        for skill, aliases in SKILL_ALIASES.items()
        if any(_contains_term(normalized_text, alias.casefold()) for alias in aliases)
    ]
    return sorted(found, key=str.casefold)


def compare_skills(resume_text: str, job_description: str) -> SkillMatch:
    """Compare explicit resume skills against explicit job requirements."""

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)
    resume_set = set(resume_skills)
    job_set = set(job_skills)
    matched = sorted(resume_set & job_set, key=str.casefold)
    missing = sorted(job_set - resume_set, key=str.casefold)
    percentage = round((len(matched) / len(job_set)) * 100, 1) if job_set else 0.0

    return SkillMatch(
        resume_skills=resume_skills,
        job_skills=job_skills,
        matched_skills=matched,
        missing_skills=missing,
        match_percentage=percentage,
    )


def _contains_term(text: str, term: str) -> bool:
    """Match a skill as a full term instead of as part of another word."""

    pattern = rf"(?<!\w){re.escape(term)}(?!\w)"
    return re.search(pattern, text) is not None
