"""Export interview preparation results as a readable Markdown report."""

from __future__ import annotations

from src.models import (
    AnswerFeedback,
    InterviewQuestion,
    PreparationTask,
    ResumeInsights,
    RoleProfile,
    SkillMatch,
)


def build_markdown_report(
    role: RoleProfile,
    match: SkillMatch,
    resume: ResumeInsights,
    questions: list[InterviewQuestion],
    feedback: dict[int, AnswerFeedback],
    plan: list[PreparationTask],
) -> str:
    """Create a portable report from the current browser session."""

    lines = [
        "# Interview Preparation Report",
        "",
        f"**Target role:** {role.detected_title}",
        f"**Role family:** {role.role_family}",
        f"**Skill match:** {match.match_percentage:.0f}%",
        f"**Required skill match:** {match.required_match_percentage:.0f}%",
        f"**Resume readiness:** {resume.score}/100",
        "",
        "## Skill Review",
        "",
        "**Required:** " + (", ".join(match.required_skills) or "None detected"),
        "",
        "**Preferred:** " + (", ".join(match.preferred_skills) or "None detected"),
        "",
        "**Matched:** " + (", ".join(match.matched_skills) or "None detected"),
        "",
        "**Prepare next:** " + (", ".join(match.missing_skills) or "No gaps detected"),
        "",
        "## Match Evidence",
        "",
    ]
    for skill in match.matched_skills:
        lines.append(f"### {skill}")
        evidence = match.matched_evidence.get(skill, [])
        lines.extend(f"- {snippet}" for snippet in evidence)
        if not evidence:
            lines.append("- No evidence excerpt available.")
        lines.append("")

    lines.extend(
        [
            "## Resume Recommendations",
            "",
            *[f"- {item}" for item in resume.recommendations],
            "",
            "## Practice Questions",
            "",
        ]
    )
    for index, question in enumerate(questions):
        lines.append(f"### {index + 1}. {question.category.value}: {question.focus_area}")
        lines.append("")
        lines.append(question.question)
        if index in feedback:
            item = feedback[index]
            lines.extend(
                [
                    "",
                    f"**Practice score:** {item.score}/100",
                    f"**Next step:** {item.recommendations[0]}",
                ]
            )
        lines.append("")

    lines.extend(["## Seven-Day Plan", ""])
    for task in plan:
        lines.append(
            f"- **Day {task.day}: {task.title}** ({task.minutes} min) - {task.description}"
        )
    return "\n".join(lines).strip() + "\n"
