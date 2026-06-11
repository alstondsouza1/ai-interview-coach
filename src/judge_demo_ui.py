"""One-click fictional demo and judge walkthrough."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.job_analysis import analyze_job_description
from src.preparation_plan import build_preparation_plan
from src.question_generator import generate_questions
from src.resume_analysis import analyze_resume
from src.skill_analysis import compare_skills

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_judge_demo_page() -> None:
    """Prepare fictional data and explain the three-minute product story."""

    st.set_page_config(
        page_title="Judge Demo | Interview Prep Studio",
        page_icon="JD",
        layout="wide",
    )
    _apply_styles()
    st.markdown(
        """
        <div class="demo-hero">
            <span>HACKATHON JUDGE MODE</span>
            <h1>See the complete product story in three minutes.</h1>
            <p>This guided flow uses fictional student data and prepares every page
            needed to demonstrate explainability, local privacy, mock interviews,
            progress analytics, and Foundry IQ grounding.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Prepare fictional demo workspace",
        type="primary",
        use_container_width=True,
        icon=":material/rocket_launch:",
    ):
        _prepare_demo_workspace()
        st.success("Demo workspace prepared. Use the page navigation to continue.")

    _render_demo_script()
    _render_judge_checklist()
    _render_architecture()


def _prepare_demo_workspace() -> None:
    resume_text = (
        PROJECT_ROOT / "sample_data" / "sample_resume.txt"
    ).read_text(encoding="utf-8")
    job_description = (
        PROJECT_ROOT / "sample_data" / "sample_job_description.txt"
    ).read_text(encoding="utf-8")
    match = compare_skills(resume_text, job_description)
    role = analyze_job_description(job_description)

    st.session_state.sample_resume_text = resume_text
    st.session_state.job_description = job_description
    st.session_state.resume_text = resume_text
    st.session_state.skill_match = match
    st.session_state.role_profile = role
    st.session_state.resume_insights = analyze_resume(resume_text)
    st.session_state.questions = generate_questions(
        resume_text, job_description, match, questions_per_category=2
    )
    st.session_state.preparation_plan = build_preparation_plan(match, role)
    st.session_state.feedback = {}
    st.session_state.demo_mode = True


def _render_demo_script() -> None:
    st.markdown("## Three-minute script")
    steps = [
        (
            "0:00-0:30",
            "Problem",
            "Students receive generic advice and unexplained match scores. "
            "Interview Prep Studio makes every finding traceable.",
        ),
        (
            "0:30-1:05",
            "Evidence-backed role fit",
            "Open the main workspace. Show required versus preferred skills, "
            "then expand a match to reveal the exact resume evidence.",
        ),
        (
            "1:05-1:40",
            "Realistic practice",
            "Open Mock Interview. Show 10 balanced questions, adjustable timing, "
            "local rubric scoring, and the completed category charts.",
        ),
        (
            "1:40-2:15",
            "Grounded intelligence",
            "Open Grounded Coach. Ask how to prepare for a missing skill and show "
            "the citation trail from Foundry IQ or the local knowledge fallback.",
        ),
        (
            "2:15-2:45",
            "Measurable improvement",
            "Open Progress. Show that only aggregate scores are saved and compare "
            "performance across attempts.",
        ),
        (
            "2:45-3:00",
            "Close",
            "Emphasize the privacy boundary: deterministic resume analysis stays "
            "local, and cloud grounding requires explicit consent.",
        ),
    ]
    for timing, title, description in steps:
        st.markdown(
            f"""
            <div class="demo-step">
                <b>{timing}</b>
                <div><strong>{title}</strong><p>{description}</p></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_judge_checklist() -> None:
    st.markdown("## Submission checklist")
    checks = {
        "Creative application": "Evidence-backed interview preparation with an interactive timed workflow.",
        "Microsoft IQ": "Foundry IQ retrieve integration with citations and consent.",
        "GitHub Copilot": "Development journal must contain real prompts and screenshots.",
        "Privacy": "Resume and answers stay local; history stores aggregate metrics only.",
        "Technical quality": "Unit tests cover parsing, retrieval, scoring, timing, and persistence.",
        "Demo reliability": "Fictional sample data works without cloud credentials.",
    }
    columns = st.columns(2)
    for index, (title, detail) in enumerate(checks.items()):
        with columns[index % 2]:
            st.markdown(f"**{title}**")
            st.caption(detail)


def _render_architecture() -> None:
    st.markdown("## Product architecture")
    st.code(
        """
Resume + Job Description
        |
        +--> Local parsing and evidence matching
        |        |
        |        +--> Practice questions + transparent scoring
        |        +--> Timed mock interview + SQLite aggregates
        |
        +--> Explicit user consent
                 |
                 +--> Microsoft Foundry IQ knowledge retrieval
                          |
                          +--> Grounded guidance + citations
""".strip()
    )


def _apply_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #f5f2e9; color: #17211b; }
        .block-container { max-width: 1080px; padding: 2.4rem 2rem 5rem; }
        .demo-hero {
            padding: 2.8rem; border-radius: 26px; margin-bottom: 1.5rem;
            background: #173f31; color: #fff;
        }
        .demo-hero span { color: #c9f26b; font-size: .72rem; font-weight: 800; letter-spacing: .14em; }
        .demo-hero h1 { color: #fff; margin: .5rem 0; font-size: 2.7rem; }
        .demo-hero p { color: #d2dfd8; max-width: 780px; }
        .demo-step {
            display: grid; grid-template-columns: 100px 1fr; gap: 1rem;
            padding: 1rem; margin-bottom: .65rem; border: 1px solid #dcd8ca;
            border-radius: 14px; background: #fffdf7;
        }
        .demo-step b { color: #e8783e; }
        .demo-step p { margin: .25rem 0 0; color: #667069; }
        button[kind="primary"] {
            min-height: 3.1rem; background: #205c45 !important;
            border-color: #205c45 !important; border-radius: 12px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
