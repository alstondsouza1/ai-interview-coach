"""Streamlit user interface for the interview coaching workflow."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.ai_client import AIClient
from src.answer_evaluator import evaluate_answer
from src.config import get_settings
from src.models import AnswerFeedback, SkillMatch
from src.question_generator import generate_questions
from src.resume_parser import ResumeParsingError, extract_text_from_pdf
from src.skill_analysis import compare_skills

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_RESUME_PATH = PROJECT_ROOT / "sample_data" / "sample_resume.txt"
SAMPLE_JOB_PATH = PROJECT_ROOT / "sample_data" / "sample_job_description.txt"


def run_app() -> None:
    """Configure and render the complete Streamlit application."""

    st.set_page_config(
        page_title="AI Interview Coach",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _apply_styles()
    _initialize_state()

    settings = get_settings()
    ai_client = AIClient(settings) if settings.ai_enabled else None

    _render_sidebar(settings.ai_enabled, settings.model)
    _render_header()
    uploaded_file, job_description = _render_inputs()

    if st.button("Analyze resume and build interview", type="primary", use_container_width=True):
        _start_interview(uploaded_file, job_description, ai_client)

    if "skill_match" in st.session_state:
        match_tab, practice_tab = st.tabs(["Resume match", "Practice interview"])
        with match_tab:
            _render_skill_match(st.session_state.skill_match)
        with practice_tab:
            _render_practice(job_description, ai_client)


def _initialize_state() -> None:
    """Set widget defaults once per browser session."""

    st.session_state.setdefault("job_description", "")
    st.session_state.setdefault("sample_resume_text", "")
    st.session_state.setdefault("feedback", {})


def _render_sidebar(ai_enabled: bool, model: str) -> None:
    with st.sidebar:
        st.markdown("## Session setup")
        if ai_enabled:
            st.success(f"AI connected: `{model}`")
        else:
            st.info("Local coaching mode")
            st.caption(
                "Add `OPENAI_API_KEY` to `.env` for personalized AI questions and feedback."
            )

        if st.button("Load sample student profile", use_container_width=True):
            st.session_state.sample_resume_text = SAMPLE_RESUME_PATH.read_text(
                encoding="utf-8"
            )
            st.session_state.job_description = SAMPLE_JOB_PATH.read_text(
                encoding="utf-8"
            )
            _clear_results()
            st.rerun()

        st.markdown("---")
        st.markdown("### How it works")
        st.markdown(
            "1. Add your resume and target role.\n"
            "2. Review matching and missing skills.\n"
            "3. Practice six personalized questions.\n"
            "4. Improve answers using scored feedback."
        )
        st.caption(
            "Your resume is processed for this session. When AI mode is enabled, "
            "resume and job text are sent to the configured API provider."
        )


def _render_header() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">INTERNSHIP + ENTRY-LEVEL PREP</div>
            <h1>Turn your resume into a focused interview practice plan.</h1>
            <p>Find skill gaps, practice role-specific questions, and improve every answer.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_inputs():
    st.markdown("### Build your interview")
    resume_column, job_column = st.columns(2, gap="large")
    with resume_column:
        uploaded_file = st.file_uploader(
            "Resume (PDF)",
            type=["pdf"],
            help="Text-based PDFs work best. Maximum size: 5 MB.",
        )
        if st.session_state.sample_resume_text and uploaded_file is None:
            st.success("Sample resume loaded. Upload a PDF to replace it.")
            with st.expander("Preview sample resume"):
                st.text(st.session_state.sample_resume_text[:2500])

    with job_column:
        job_description = st.text_area(
            "Job description",
            key="job_description",
            height=240,
            placeholder="Paste the responsibilities and requirements for your target role...",
        )
        st.caption(f"{len(job_description):,} characters")

    return uploaded_file, job_description


def _start_interview(uploaded_file, job_description: str, ai_client: AIClient | None) -> None:
    if not uploaded_file and not st.session_state.sample_resume_text:
        st.error("Upload a PDF resume or load the sample student profile.")
        return
    if len(job_description.strip()) < 80:
        st.error("Paste a fuller job description so the comparison is meaningful.")
        return

    try:
        with st.spinner("Reading your resume and preparing the interview..."):
            resume_text = (
                extract_text_from_pdf(uploaded_file)
                if uploaded_file
                else st.session_state.sample_resume_text
            )
            skill_match = compare_skills(resume_text, job_description)
            questions, warning = generate_questions(
                resume_text, job_description, skill_match, ai_client
            )
    except ResumeParsingError as exc:
        st.error(str(exc))
        return

    st.session_state.resume_text = resume_text
    st.session_state.skill_match = skill_match
    st.session_state.questions = questions
    st.session_state.feedback = {}
    if warning:
        st.warning(f"AI generation was unavailable, so local questions were used. {warning}")
    st.success("Your interview plan is ready. Open the tabs below to begin.")


def _render_skill_match(match: SkillMatch) -> None:
    st.markdown("### Resume-to-role match")
    score_column, matched_column, gap_column = st.columns(3)
    score_column.metric("Skill match", f"{match.match_percentage:.0f}%")
    matched_column.metric("Matched requirements", len(match.matched_skills))
    gap_column.metric("Skills to review", len(match.missing_skills))
    st.progress(match.match_percentage / 100)

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("#### Strengths to mention")
        _render_skill_chips(match.matched_skills, "match")
        if not match.matched_skills:
            st.info("No explicit catalog skills matched. Add concrete tools to your resume.")
    with right:
        st.markdown("#### Requirements to prepare")
        _render_skill_chips(match.missing_skills, "gap")
        if not match.missing_skills:
            st.success("Every detected job skill also appears in your resume.")

    with st.expander("All skills detected in your resume"):
        st.write(", ".join(match.resume_skills) or "No catalog skills detected.")
    st.caption(
        "This keyword comparison is a preparation aid, not an applicant tracking score."
    )


def _render_practice(job_description: str, ai_client: AIClient | None) -> None:
    questions = st.session_state.questions
    completed = len(st.session_state.feedback)
    st.markdown("### Practice interview")
    st.caption(f"{completed} of {len(questions)} answers reviewed")
    st.progress(completed / len(questions))

    for index, question in enumerate(questions):
        label = f"{index + 1}. {question.category.value}: {question.focus_area}"
        with st.expander(label, expanded=index == completed):
            st.markdown(f"#### {question.question}")
            st.caption(f"Why this is asked: {question.why_asked}")
            with st.form(f"answer_form_{index}"):
                answer = st.text_area(
                    "Your answer",
                    key=f"answer_{index}",
                    height=180,
                    placeholder="Use a specific example and explain your individual actions...",
                )
                submitted = st.form_submit_button(
                    "Get feedback", type="primary", use_container_width=True
                )

            if submitted:
                try:
                    with st.spinner("Reviewing your answer..."):
                        feedback, warning = evaluate_answer(
                            question, answer, job_description, ai_client
                        )
                    st.session_state.feedback[index] = feedback
                    if warning:
                        st.warning(
                            f"AI evaluation was unavailable, so local scoring was used. {warning}"
                        )
                except ValueError as exc:
                    st.error(str(exc))

            if index in st.session_state.feedback:
                _render_feedback(st.session_state.feedback[index])


def _render_feedback(feedback: AnswerFeedback) -> None:
    st.markdown("---")
    score_column, summary_column = st.columns([1, 3])
    score_column.metric("Answer score", f"{feedback.score}/100")
    score_column.progress(feedback.score / 100)
    summary_column.markdown("**Coach's summary**")
    summary_column.write(feedback.summary)

    strengths_column, weaknesses_column = st.columns(2)
    with strengths_column:
        st.markdown("**What worked**")
        for item in feedback.strengths:
            st.markdown(f"- {item}")
    with weaknesses_column:
        st.markdown("**What to strengthen**")
        for item in feedback.weaknesses:
            st.markdown(f"- {item}")

    st.markdown("**Next revision checklist**")
    for item in feedback.recommendations:
        st.markdown(f"- {item}")
    st.info(feedback.improved_answer)


def _render_skill_chips(skills: list[str], chip_type: str) -> None:
    if not skills:
        return
    chips = "".join(
        f'<span class="skill-chip {chip_type}">{skill}</span>' for skill in skills
    )
    st.markdown(f'<div class="chip-list">{chips}</div>', unsafe_allow_html=True)


def _clear_results() -> None:
    for key in ("resume_text", "skill_match", "questions", "feedback"):
        st.session_state.pop(key, None)


def _apply_styles() -> None:
    """Add lightweight styling without changing Streamlit's core behavior."""

    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at 85% 5%, rgba(45, 212, 191, 0.12), transparent 25rem),
                #f7f9fc;
        }
        .block-container { max-width: 1180px; padding-top: 2rem; }
        .hero {
            padding: 2.4rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 24px;
            color: #f8fafc;
            background: linear-gradient(135deg, #0f172a 0%, #164e63 100%);
            box-shadow: 0 20px 45px rgba(15, 23, 42, 0.16);
        }
        .hero h1 {
            max-width: 820px;
            margin: 0.35rem 0 0.65rem;
            color: #ffffff;
            font-size: clamp(2rem, 4vw, 3.4rem);
            line-height: 1.08;
        }
        .hero p { margin: 0; color: #cbd5e1; font-size: 1.08rem; }
        .eyebrow {
            color: #5eead4;
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.14em;
        }
        .chip-list { display: flex; flex-wrap: wrap; gap: 0.55rem; margin: 0.6rem 0 1rem; }
        .skill-chip {
            display: inline-block;
            padding: 0.42rem 0.72rem;
            border-radius: 999px;
            font-size: 0.86rem;
            font-weight: 650;
        }
        .skill-chip.match { color: #115e59; background: #ccfbf1; }
        .skill-chip.gap { color: #9a3412; background: #ffedd5; }
        div[data-testid="stMetric"] {
            padding: 1rem;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.8);
        }
        div[data-testid="stExpander"] {
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.72);
        }
        @media (max-width: 640px) {
            .block-container { padding: 1rem; }
            .hero { padding: 1.5rem; border-radius: 18px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

