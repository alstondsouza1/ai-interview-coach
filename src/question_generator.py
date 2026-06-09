"""Build role-aware practice interviews from a curated question bank."""

from __future__ import annotations

from src.models import InterviewQuestion, QuestionCategory, SkillMatch

QUESTION_BANK: dict[QuestionCategory, list[dict[str, object]]] = {
    QuestionCategory.TECHNICAL: [
        {
            "skills": {"Python", "Java", "JavaScript", "TypeScript", "C++", "C#"},
            "question": "Walk me through a project where you used {skill}. Why did you choose it?",
            "focus": "{skill}",
            "why": "Connects a resume skill to your technical decisions and actual contribution.",
        },
        {
            "skills": {"Testing"},
            "question": "How would you test a new feature before asking a teammate to review it?",
            "focus": "Testing",
            "why": "Checks whether quality is part of your normal development process.",
        },
        {
            "skills": {"SQL", "PostgreSQL", "MongoDB"},
            "question": "A database-backed page has become slow. How would you investigate it?",
            "focus": "Data and debugging",
            "why": "Tests structured problem solving without requiring advanced system design.",
        },
        {
            "skills": {"React", "Vue.js", "HTML", "CSS", "JavaScript"},
            "question": "How would you design a responsive interface that is also accessible?",
            "focus": "Frontend quality",
            "why": "Explores usability, accessibility, and implementation tradeoffs.",
        },
        {
            "skills": {"REST APIs", "Flask", "Django", "Node.js"},
            "question": "Design a small API for a campus event app. Which endpoints would you create?",
            "focus": "API design",
            "why": "Evaluates resource modeling, HTTP basics, and clear technical communication.",
        },
        {
            "skills": {"Git"},
            "question": "Describe your Git workflow when working on a feature with other developers.",
            "focus": "Git collaboration",
            "why": "Checks practical teamwork habits used in real engineering teams.",
        },
        {
            "skills": {"Docker", "AWS", "Google Cloud", "Kubernetes"},
            "question": "What problem does {skill} solve, and when would you use it in a student project?",
            "focus": "{skill}",
            "why": "Tests your understanding of a role requirement that may be newer to you.",
        },
        {
            "skills": {"Data Structures"},
            "question": "How would you choose a data structure for fast lookup and frequent updates?",
            "focus": "Data structures",
            "why": "Checks whether you can explain a fundamental tradeoff clearly.",
        },
        {
            "skills": {"Object-Oriented Programming"},
            "question": "Explain encapsulation using an example from a project or everyday system.",
            "focus": "Object-oriented design",
            "why": "Tests fundamentals and your ability to explain technical ideas simply.",
        },
    ],
    QuestionCategory.BEHAVIORAL: [
        {
            "skills": {"Teamwork"},
            "question": "Tell me about a team project where people had different opinions.",
            "focus": "Collaboration",
            "why": "Shows how you listen, communicate, and move a group toward a decision.",
        },
        {
            "skills": {"Communication"},
            "question": "Tell me about a time you explained a technical idea to a non-technical person.",
            "focus": "Communication",
            "why": "Entry-level engineers need to adapt explanations to different audiences.",
        },
        {
            "skills": set(),
            "question": "Describe a mistake you made in a project and what you changed afterward.",
            "focus": "Ownership",
            "why": "Interviewers look for honesty, reflection, and evidence of improvement.",
        },
        {
            "skills": set(),
            "question": "Tell me about a time you had to learn something quickly.",
            "focus": "Learning agility",
            "why": "Internships require learning unfamiliar tools with limited guidance.",
        },
        {
            "skills": set(),
            "question": "Which project are you most proud of, and what was your personal contribution?",
            "focus": "Project impact",
            "why": "Helps separate your work from the team's work and reveal what motivates you.",
        },
    ],
    QuestionCategory.SITUATIONAL: [
        {
            "skills": set(),
            "question": "A task is taking longer than expected and the deadline is tomorrow. What do you do?",
            "focus": "Prioritization",
            "why": "Checks planning, early communication, and ownership under pressure.",
        },
        {
            "skills": set(),
            "question": "You receive a vague ticket with no clear acceptance criteria. How do you begin?",
            "focus": "Clarifying requirements",
            "why": "Good engineers reduce ambiguity before writing unnecessary code.",
        },
        {
            "skills": set(),
            "question": "Your code works locally but fails in the shared environment. What are your next steps?",
            "focus": "Debugging process",
            "why": "Evaluates calm, methodical troubleshooting and communication.",
        },
        {
            "skills": set(),
            "question": "A teammate is blocked and asks for help while you have urgent work. How do you respond?",
            "focus": "Team judgment",
            "why": "Explores how you balance delivery, empathy, and team outcomes.",
        },
        {
            "skills": set(),
            "question": "You disagree with feedback on your pull request. What would you do?",
            "focus": "Code review",
            "why": "Checks whether you can discuss technical disagreement constructively.",
        },
    ],
}


def generate_questions(
    resume_text: str,
    job_description: str,
    skill_match: SkillMatch,
    questions_per_category: int = 2,
) -> list[InterviewQuestion]:
    """Select balanced questions based on detected resume and job skills."""

    del resume_text, job_description  # Inputs are represented by the analyzed skill match.
    relevant_skills = set(skill_match.job_skills) | set(skill_match.resume_skills)
    questions: list[InterviewQuestion] = []

    for category in QuestionCategory:
        ranked = sorted(
            QUESTION_BANK[category],
            key=lambda item: _question_priority(
                item["skills"], relevant_skills, set(skill_match.missing_skills)
            ),
            reverse=True,
        )
        for item in ranked[:questions_per_category]:
            template_skill = _best_template_skill(
                item["skills"], skill_match.missing_skills, skill_match.matched_skills
            )
            questions.append(
                InterviewQuestion(
                    category=category,
                    question=str(item["question"]).format(skill=template_skill),
                    focus_area=str(item["focus"]).format(skill=template_skill),
                    why_asked=str(item["why"]),
                )
            )
    return questions


def _question_priority(
    question_skills: object, relevant_skills: set[str], missing_skills: set[str]
) -> tuple[int, int]:
    skills = set(question_skills)
    return (len(skills & missing_skills), len(skills & relevant_skills))


def _best_template_skill(
    question_skills: object, missing_skills: list[str], matched_skills: list[str]
) -> str:
    skills = set(question_skills)
    for candidate in [*missing_skills, *matched_skills]:
        if candidate in skills:
            return candidate
    return sorted(skills)[0] if skills else "a new technology"
