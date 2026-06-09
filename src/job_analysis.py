"""Infer practical preparation signals from a job description."""

from __future__ import annotations

import re

from src.models import RoleProfile
from src.skill_analysis import extract_skills

ROLE_RULES = [
    ("Data / ML", ("data scientist", "machine learning", "data analyst", "ml engineer")),
    ("Frontend", ("frontend", "front-end", "ui engineer", "web designer")),
    ("Backend", ("backend", "back-end", "api engineer")),
    ("Mobile", ("mobile", "ios", "android")),
    ("DevOps / Cloud", ("devops", "site reliability", "cloud engineer", "sre")),
    ("Full Stack", ("full stack", "full-stack")),
    ("Software Engineering", ("software engineer", "software developer", "developer intern")),
]

EMPHASIS_RULES = {
    "Testing and quality": ("test", "quality", "qa", "reliable"),
    "Team collaboration": ("team", "collaborat", "cross-functional"),
    "Customer focus": ("customer", "user experience", "user needs"),
    "Ownership": ("ownership", "independent", "initiative", "self-starter"),
    "Communication": ("communicat", "present", "documentation"),
    "Problem solving": ("problem solving", "troubleshoot", "debug"),
}


def analyze_job_description(job_description: str) -> RoleProfile:
    """Build a role profile from common title and emphasis phrases."""

    normalized = " ".join(job_description.split())
    lower_text = normalized.casefold()
    role_family = next(
        (
            family
            for family, phrases in ROLE_RULES
            if any(phrase in lower_text for phrase in phrases)
        ),
        "Software Engineering",
    )
    seniority = _detect_seniority(lower_text)
    title = _detect_title(normalized, role_family, seniority)
    skills = extract_skills(job_description)
    emphasis = [
        label
        for label, phrases in EMPHASIS_RULES.items()
        if any(phrase in lower_text for phrase in phrases)
    ]
    return RoleProfile(
        role_family=role_family,
        seniority=seniority,
        detected_title=title,
        priority_skills=skills[:8],
        emphasis_areas=emphasis[:5],
    )


def _detect_seniority(text: str) -> str:
    if re.search(r"\b(intern|internship|co-op)\b", text):
        return "Internship"
    if re.search(r"\b(entry.level|junior|new grad|graduate)\b", text):
        return "Entry level"
    return "Not specified"


def _detect_title(text: str, role_family: str, seniority: str) -> str:
    first_lines = [line.strip(" -:") for line in text.splitlines()[:5] if line.strip()]
    for line in first_lines:
        if len(line.split()) <= 8 and any(
            term in line.casefold()
            for term in ("engineer", "developer", "intern", "analyst")
        ):
            return line
    return f"{role_family} {seniority}".strip()
