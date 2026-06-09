"""Measure resume readiness using clear, deterministic checks."""

from __future__ import annotations

import re

from src.models import ResumeInsights

SECTION_PATTERNS = {
    "Education": r"\b(education|academic background)\b",
    "Skills": r"\b(skills|technical skills|technologies)\b",
    "Projects": r"\b(projects|personal projects|academic projects)\b",
    "Experience": r"\b(experience|work experience|employment)\b",
}

ACTION_VERBS = {
    "analyzed",
    "automated",
    "built",
    "collaborated",
    "created",
    "debugged",
    "designed",
    "developed",
    "implemented",
    "improved",
    "integrated",
    "led",
    "optimized",
    "presented",
    "reduced",
    "tested",
    "wrote",
}


def analyze_resume(resume_text: str) -> ResumeInsights:
    """Return resume quality signals suitable for student resumes."""

    lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    lower_text = resume_text.casefold()
    detected_sections = [
        name
        for name, pattern in SECTION_PATTERNS.items()
        if re.search(pattern, lower_text, re.IGNORECASE)
    ]
    missing_sections = [
        name for name in SECTION_PATTERNS if name not in detected_sections
    ]
    bullets = [line for line in lines if re.match(r"^[-*•]\s+", line)]
    quantified_bullets = [
        line
        for line in bullets
        if re.search(r"\b\d+(?:\.\d+)?(?:%|\+|x)?\b", line, re.IGNORECASE)
    ]
    action_verb_count = sum(
        1
        for line in bullets
        if _first_meaningful_word(line).casefold() in ACTION_VERBS
    )
    word_count = len(resume_text.split())

    score = 25
    score += min(28, len(detected_sections) * 7)
    score += min(18, len(bullets) * 2)
    score += min(16, len(quantified_bullets) * 4)
    score += min(13, action_verb_count * 2)
    if word_count < 120 or word_count > 900:
        score -= 8
    score = max(0, min(100, score))

    return ResumeInsights(
        word_count=word_count,
        bullet_count=len(bullets),
        quantified_bullet_count=len(quantified_bullets),
        action_verb_count=action_verb_count,
        detected_sections=detected_sections,
        missing_sections=missing_sections,
        score=score,
        recommendations=_recommendations(
            word_count,
            len(bullets),
            len(quantified_bullets),
            action_verb_count,
            missing_sections,
        ),
    )


def _first_meaningful_word(line: str) -> str:
    cleaned = re.sub(r"^[-*•]\s+", "", line)
    match = re.search(r"[A-Za-z]+", cleaned)
    return match.group(0) if match else ""


def _recommendations(
    word_count: int,
    bullet_count: int,
    quantified_count: int,
    action_verb_count: int,
    missing_sections: list[str],
) -> list[str]:
    recommendations = []
    if missing_sections:
        recommendations.append(
            "Add or clearly label: " + ", ".join(missing_sections) + "."
        )
    if bullet_count < 5:
        recommendations.append(
            "Use at least five concise bullets across projects and experience."
        )
    if quantified_count < 2:
        recommendations.append(
            "Add numbers to at least two bullets, such as users, tests, time saved, or team size."
        )
    if action_verb_count < max(2, bullet_count // 2):
        recommendations.append(
            "Start more bullets with strong verbs such as Built, Implemented, Tested, or Improved."
        )
    if word_count < 120:
        recommendations.append("Add enough project detail to show decisions, tools, and outcomes.")
    elif word_count > 900:
        recommendations.append("Shorten the resume by removing repeated or low-impact details.")
    return recommendations or [
        "The basic resume structure is strong. Tailor the top project bullets to the target role."
    ]
