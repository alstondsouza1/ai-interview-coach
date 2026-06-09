"""Data structures shared by the application modules."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class QuestionCategory(str, Enum):
    """Interview question categories shown in the practice session."""

    TECHNICAL = "Technical"
    BEHAVIORAL = "Behavioral"
    SITUATIONAL = "Situational"


@dataclass
class SkillMatch:
    """Comparison between resume skills and job requirements."""

    resume_skills: list[str] = field(default_factory=list)
    job_skills: list[str] = field(default_factory=list)
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    match_percentage: float = 0.0


@dataclass
class InterviewQuestion:
    """A generated interview question and its purpose."""

    category: QuestionCategory
    question: str
    focus_area: str
    why_asked: str


@dataclass
class AnswerFeedback:
    """Transparent, rubric-based feedback for a practice answer."""

    score: int
    rubric_scores: dict[str, int]
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    improved_answer: str
    summary: str
    word_count: int
