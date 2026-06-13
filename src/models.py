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
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    matched_evidence: dict[str, list[str]] = field(default_factory=dict)
    match_percentage: float = 0.0
    required_match_percentage: float = 0.0


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


@dataclass
class ResumeInsights:
    """Measurable resume quality signals and revision advice."""

    word_count: int
    bullet_count: int
    quantified_bullet_count: int
    action_verb_count: int
    detected_sections: list[str]
    missing_sections: list[str]
    score: int
    recommendations: list[str]


@dataclass
class RoleProfile:
    """High-level information inferred from a job description."""

    role_family: str
    seniority: str
    detected_title: str
    priority_skills: list[str]
    emphasis_areas: list[str]


@dataclass
class PreparationTask:
    """One concrete task in a short interview preparation plan."""

    day: int
    title: str
    description: str
    minutes: int
    category: str


@dataclass
class MockInterviewAnswer:
    """One submitted answer in a timed mock interview."""

    question_index: int
    question: InterviewQuestion
    answer: str
    feedback: AnswerFeedback
    time_taken_seconds: int
    timed_out: bool = False


@dataclass
class MockInterviewSummary:
    """Aggregate performance for a completed mock interview."""

    overall_score: int
    readiness_label: str
    category_scores: dict[str, int]
    rubric_scores: dict[str, int]
    strengths: list[str]
    weaknesses: list[str]
    completed_questions: int
    total_questions: int
    average_time_seconds: int


@dataclass
class KnowledgeCitation:
    """A source supporting grounded coaching guidance."""

    citation_id: str
    title: str
    source: str
    excerpt: str = ""


@dataclass
class GroundedCoachingResponse:
    """Citation-backed coaching returned by Foundry IQ or local knowledge."""

    answer: str
    citations: list[KnowledgeCitation]
    provider: str
    query: str
    activity_summary: list[str] = field(default_factory=list)
    endpoint_host: str = ""
    knowledge_base: str = ""
    elapsed_ms: int | None = None

    @property
    def citation_count(self) -> int:
        return len(self.citations)
