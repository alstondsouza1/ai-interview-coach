"""Evaluate practice answers and return actionable coaching feedback."""

from __future__ import annotations

import json
import re

from src.ai_client import AIClient, AIServiceError
from src.models import AnswerFeedback, InterviewQuestion


def evaluate_answer(
    question: InterviewQuestion,
    answer: str,
    job_description: str,
    ai_client: AIClient | None = None,
) -> tuple[AnswerFeedback, str | None]:
    """Score an answer with AI or a deterministic coaching fallback."""

    clean_answer = answer.strip()
    if len(clean_answer) < 20:
        raise ValueError("Please write at least a few complete sentences.")

    if ai_client is not None:
        try:
            data = ai_client.complete_json(
                _evaluation_system_prompt(),
                _evaluation_user_prompt(question, clean_answer, job_description),
            )
            return _parse_feedback(data), None
        except (AIServiceError, KeyError, TypeError, ValueError) as exc:
            return _fallback_feedback(question, clean_answer), str(exc)

    return _fallback_feedback(question, clean_answer), None


def _evaluation_system_prompt() -> str:
    return """
You are a supportive but honest interview coach for students and entry-level
software engineering candidates. Evaluate only the answer provided. Return
valid JSON with: score (integer 0-100), strengths (array), weaknesses (array),
recommendations (array), improved_answer (string), and summary (string).
Reward specific examples, clear structure, technical accuracy, ownership, and
measurable results. Do not claim that an answer is technically correct when
there is not enough context. Keep feedback concise and actionable.
""".strip()


def _evaluation_user_prompt(
    question: InterviewQuestion, answer: str, job_description: str
) -> str:
    context = {
        "category": question.category.value,
        "question": question.question,
        "focus_area": question.focus_area,
        "candidate_answer": answer[:6000],
        "job_description": job_description[:4000],
    }
    return "Evaluate this interview answer:\n" + json.dumps(context)


def _parse_feedback(data: dict) -> AnswerFeedback:
    score = max(0, min(100, int(data["score"])))
    feedback = AnswerFeedback(
        score=score,
        strengths=_string_list(data["strengths"]),
        weaknesses=_string_list(data["weaknesses"]),
        recommendations=_string_list(data["recommendations"]),
        improved_answer=str(data["improved_answer"]).strip(),
        summary=str(data["summary"]).strip(),
    )
    if not feedback.summary or not feedback.recommendations:
        raise ValueError("The AI feedback was incomplete.")
    return feedback


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        raise TypeError("Expected a list in the AI response.")
    return [str(item).strip() for item in value if str(item).strip()]


def _fallback_feedback(
    question: InterviewQuestion, answer: str
) -> AnswerFeedback:
    """Give basic coaching when no AI provider is configured."""

    words = answer.split()
    lower_answer = answer.casefold()
    has_example = any(
        phrase in lower_answer
        for phrase in ("for example", "in my project", "when i", "during")
    )
    has_result = bool(
        re.search(r"\b(result|outcome|improved|reduced|increased|learned)\b", lower_answer)
        or re.search(r"\b\d+(?:\.\d+)?%?\b", answer)
    )
    has_action = any(
        phrase in lower_answer
        for phrase in ("i built", "i created", "i implemented", "i decided", "i tested")
    )

    score = 35
    score += min(25, len(words) // 4)
    score += 12 if has_example else 0
    score += 14 if has_action else 0
    score += 14 if has_result else 0
    score = min(score, 92)

    strengths = []
    if len(words) >= 60:
        strengths.append("The answer includes enough detail to discuss your approach.")
    if has_example:
        strengths.append("You used a concrete example instead of staying fully general.")
    if has_action:
        strengths.append("Your individual contribution is visible.")
    if has_result:
        strengths.append("You included an outcome or lesson.")
    if not strengths:
        strengths.append("You made a direct attempt to answer the question.")

    weaknesses = []
    recommendations = []
    if len(words) < 60:
        weaknesses.append("The answer is brief and may leave the interviewer with questions.")
        recommendations.append("Add context, your actions, and the final result.")
    if not has_example:
        weaknesses.append("The answer does not include a specific example.")
        recommendations.append("Choose one project, class, or team experience as evidence.")
    if not has_action:
        weaknesses.append("Your personal actions are not clearly separated from the team's work.")
        recommendations.append("Use 'I' statements to explain two or three actions you took.")
    if not has_result:
        weaknesses.append("The result or lesson learned is unclear.")
        recommendations.append("End with a measurable result, feedback, or what you learned.")

    improved = (
        f"Use this structure for your {question.category.value.lower()} answer: "
        "briefly describe the situation, explain your responsibility, give two specific "
        "actions you took, and finish with the result and what you learned."
    )
    return AnswerFeedback(
        score=score,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
        improved_answer=improved,
        summary="This local score focuses on detail, ownership, examples, and results.",
    )

