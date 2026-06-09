"""Evaluate interview answers with a transparent local rubric."""

from __future__ import annotations

import re

from src.models import AnswerFeedback, InterviewQuestion, QuestionCategory

RUBRIC_WEIGHTS = {
    "Structure": 25,
    "Specificity": 25,
    "Ownership": 20,
    "Impact": 20,
    "Clarity": 10,
}


def evaluate_answer(
    question: InterviewQuestion, answer: str, job_description: str = ""
) -> AnswerFeedback:
    """Score an answer using observable writing signals.

    The score is a coaching aid, not a judgment of technical correctness.
    """

    del job_description
    clean_answer = " ".join(answer.split())
    if len(clean_answer) < 20:
        raise ValueError("Please write at least a few complete sentences.")

    words = clean_answer.split()
    lower_answer = clean_answer.casefold()
    signals = _answer_signals(clean_answer, lower_answer, words)
    rubric_scores = {
        "Structure": _structure_score(signals),
        "Specificity": _specificity_score(signals),
        "Ownership": _ownership_score(signals),
        "Impact": _impact_score(signals),
        "Clarity": _clarity_score(clean_answer, words),
    }
    score = sum(
        round(rubric_scores[name] * weight / 100)
        for name, weight in RUBRIC_WEIGHTS.items()
    )
    strengths, weaknesses, recommendations = _build_coaching(rubric_scores)

    return AnswerFeedback(
        score=max(0, min(100, score)),
        rubric_scores=rubric_scores,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
        improved_answer=_revision_framework(question),
        summary=_score_summary(score),
        word_count=len(words),
    )


def _answer_signals(answer: str, lower_answer: str, words: list[str]) -> dict[str, bool | int]:
    return {
        "word_count": len(words),
        "has_context": any(
            phrase in lower_answer
            for phrase in ("during", "when i", "in my", "our project", "the situation")
        ),
        "has_task": any(
            phrase in lower_answer
            for phrase in ("my task", "my goal", "responsible for", "needed to", "had to")
        ),
        "has_action": bool(
            re.search(
                r"\bi (built|created|implemented|tested|debugged|designed|decided|"
                r"organized|asked|reviewed|changed|led|wrote|fixed)\b",
                lower_answer,
            )
        ),
        "has_result": bool(
            re.search(
                r"\b(result|outcome|improved|reduced|increased|saved|completed|"
                r"learned|successful|feedback)\b",
                lower_answer,
            )
        ),
        "has_number": bool(re.search(r"\b\d+(?:\.\d+)?%?\b", answer)),
        "has_example": any(
            phrase in lower_answer
            for phrase in ("for example", "specifically", "such as", "in my project")
        ),
        "first_person_actions": len(re.findall(r"\bi\b", lower_answer)),
    }


def _structure_score(signals: dict[str, bool | int]) -> int:
    score = 20
    score += 20 if signals["has_context"] else 0
    score += 15 if signals["has_task"] else 0
    score += 25 if signals["has_action"] else 0
    score += 20 if signals["has_result"] else 0
    return score


def _specificity_score(signals: dict[str, bool | int]) -> int:
    score = 30
    score += 25 if signals["has_example"] else 0
    score += 25 if signals["has_number"] else 0
    score += 20 if int(signals["word_count"]) >= 70 else 0
    return score


def _ownership_score(signals: dict[str, bool | int]) -> int:
    score = 25
    score += 40 if signals["has_action"] else 0
    score += min(35, int(signals["first_person_actions"]) * 7)
    return score


def _impact_score(signals: dict[str, bool | int]) -> int:
    score = 25
    score += 45 if signals["has_result"] else 0
    score += 30 if signals["has_number"] else 0
    return score


def _clarity_score(answer: str, words: list[str]) -> int:
    sentences = [part for part in re.split(r"[.!?]+", answer) if part.strip()]
    if not sentences:
        return 20
    average_length = len(words) / len(sentences)
    score = 65
    if 8 <= average_length <= 24:
        score += 25
    if 55 <= len(words) <= 220:
        score += 10
    return min(100, score)


def _build_coaching(
    rubric_scores: dict[str, int],
) -> tuple[list[str], list[str], list[str]]:
    strengths = [
        f"{name} is working well ({score}/100)."
        for name, score in rubric_scores.items()
        if score >= 75
    ]
    weaknesses = [
        f"{name} needs more evidence ({score}/100)."
        for name, score in rubric_scores.items()
        if score < 60
    ]
    recommendations_by_area = {
        "Structure": "Use Situation, Task, Action, Result in that order.",
        "Specificity": "Name the project, challenge, tools, and one concrete detail.",
        "Ownership": "Use clear 'I' statements for the decisions and work you completed.",
        "Impact": "Finish with a result, measurement, feedback, or lesson learned.",
        "Clarity": "Use shorter sentences and remove background that does not support the answer.",
    }
    recommendations = [
        recommendations_by_area[name]
        for name, score in sorted(rubric_scores.items(), key=lambda item: item[1])[:3]
        if score < 85
    ]
    return (
        strengths or ["You gave the coach enough text to identify a revision path."],
        weaknesses or ["No major rubric gap was detected; focus on polishing delivery."],
        recommendations or ["Practice saying the answer aloud in under two minutes."],
    )


def _revision_framework(question: InterviewQuestion) -> str:
    if question.category == QuestionCategory.TECHNICAL:
        return (
            "Revision plan: state the problem, explain your technical choice, walk through "
            "your implementation or debugging steps, discuss one tradeoff, and end with the result."
        )
    return (
        "Revision plan: give one sentence of context, state your responsibility, describe "
        "two actions you personally took, and finish with the result and lesson learned."
    )


def _score_summary(score: int) -> str:
    if score >= 80:
        return "Strong draft. Tighten the wording and practice delivering it naturally."
    if score >= 60:
        return "Good foundation. Add evidence in the lowest-scoring rubric areas."
    return "Early draft. Rebuild it around one specific example and a clear result."
