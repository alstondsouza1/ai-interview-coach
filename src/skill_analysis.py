"""Evidence-backed skill extraction and resume-to-job comparison."""

from __future__ import annotations

import re

from src.models import SkillMatch

# The catalog favors internship and junior software roles while keeping every
# detected skill explainable through explicit aliases.
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

PREFERRED_MARKERS = (
    "preferred",
    "nice to have",
    "bonus",
    "plus",
    "desired",
    "optional",
)
REQUIRED_MARKERS = (
    "required",
    "requirements",
    "minimum qualifications",
    "must have",
    "you have",
    "what you bring",
)


def extract_skills(text: str) -> list[str]:
    """Return canonical skill names explicitly found in text."""

    normalized_text = text.casefold()
    found = [
        skill
        for skill, aliases in SKILL_ALIASES.items()
        if any(_contains_term(normalized_text, alias.casefold()) for alias in aliases)
    ]
    return sorted(found, key=str.casefold)


def extract_skill_evidence(text: str, limit_per_skill: int = 2) -> dict[str, list[str]]:
    """Return concise source lines that prove why each skill was detected."""

    evidence: dict[str, list[str]] = {}
    for line in _evidence_lines(text):
        normalized_line = line.casefold()
        for skill, aliases in SKILL_ALIASES.items():
            if any(_contains_term(normalized_line, alias.casefold()) for alias in aliases):
                snippets = evidence.setdefault(skill, [])
                snippet = _trim_snippet(line)
                if snippet not in snippets and len(snippets) < limit_per_skill:
                    snippets.append(snippet)
    return evidence


def classify_job_skills(job_description: str) -> tuple[list[str], list[str]]:
    """Separate required skills from explicitly preferred qualifications."""

    required: set[str] = set()
    preferred: set[str] = set()
    current_section = "required"

    for line in _evidence_lines(job_description):
        lower_line = line.casefold()
        if any(marker in lower_line for marker in PREFERRED_MARKERS):
            current_section = "preferred"
        elif any(marker in lower_line for marker in REQUIRED_MARKERS):
            current_section = "required"

        line_skills = set(extract_skills(line))
        if current_section == "preferred":
            preferred.update(line_skills)
        else:
            required.update(line_skills)

    # Required always wins if a skill appears in both sections.
    preferred -= required
    return (
        sorted(required, key=str.casefold),
        sorted(preferred, key=str.casefold),
    )


def compare_skills(resume_text: str, job_description: str) -> SkillMatch:
    """Compare resume evidence against required and preferred job skills."""

    evidence = extract_skill_evidence(resume_text)
    resume_skills = sorted(evidence, key=str.casefold)
    required_skills, preferred_skills = classify_job_skills(job_description)
    job_skills = sorted(
        set(required_skills) | set(preferred_skills), key=str.casefold
    )
    resume_set = set(resume_skills)
    required_set = set(required_skills)
    job_set = set(job_skills)
    matched = sorted(resume_set & job_set, key=str.casefold)
    missing = sorted(job_set - resume_set, key=str.casefold)
    percentage = round((len(matched) / len(job_set)) * 100, 1) if job_set else 0.0
    required_match = (
        round((len(resume_set & required_set) / len(required_set)) * 100, 1)
        if required_set
        else percentage
    )

    return SkillMatch(
        resume_skills=resume_skills,
        job_skills=job_skills,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        matched_skills=matched,
        missing_skills=missing,
        matched_evidence={skill: evidence[skill] for skill in matched},
        match_percentage=percentage,
        required_match_percentage=required_match,
    )


def _evidence_lines(text: str) -> list[str]:
    lines = []
    for raw_line in text.splitlines():
        for sentence in re.split(r"(?<=[.!?])\s+", raw_line):
            cleaned = " ".join(sentence.split()).strip(" -•*\t")
            if cleaned:
                lines.append(cleaned)
    return lines


def _trim_snippet(text: str, max_length: int = 220) -> str:
    return text if len(text) <= max_length else text[: max_length - 1].rstrip() + "…"


def _contains_term(text: str, term: str) -> bool:
    pattern = rf"(?<!\w){re.escape(term)}(?!\w)"
    return re.search(pattern, text) is not None
