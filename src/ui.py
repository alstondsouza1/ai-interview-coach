"""Streamlit interface for the private, local Interview Prep Studio."""

from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from src.answer_evaluator import RUBRIC_WEIGHTS, evaluate_answer
from src.job_analysis import analyze_job_description
from src.models import AnswerFeedback, ResumeInsights, RoleProfile, SkillMatch
from src.preparation_plan import build_preparation_plan
from src.question_generator import generate_questions
from src.resume_analysis import analyze_resume
from src.resume_parser import (
    ResumeParsingError,
    extract_resume_text,
    validate_resume_text,
)
from src.session_report import build_markdown_report
from src.skill_analysis import compare_skills

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_RESUME_PATH = PROJECT_ROOT / "sample_data" / "sample_resume.txt"
SAMPLE_JOB_PATH = PROJECT_ROOT / "sample_data" / "sample_job_description.txt"


def run_app() -> None:
    """Configure and render the complete application."""

    st.set_page_config(
        page_title="Interview Prep Studio",
        page_icon="IP",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _apply_styles()
    _initialize_state()
    _render_sidebar()
    _render_header()

    uploaded_file, pasted_resume, job_description, question_depth = _render_setup()
    if st.button(
        "Build my preparation workspace",
        type="primary",
        use_container_width=True,
        icon=":material/arrow_forward:",
    ):
        _build_workspace(
            uploaded_file, pasted_resume, job_description, question_depth
        )

    if "skill_match" in st.session_state:
        _render_workspace()
    else:
        _render_empty_state()


def _initialize_state() -> None:
    st.session_state.setdefault("job_description", "")
    st.session_state.setdefault("sample_resume_text", "")
    st.session_state.setdefault("pasted_resume_text", "")
    st.session_state.setdefault("resume_input_method", "Upload PDF or DOCX")
    st.session_state.setdefault("feedback", {})
    st.session_state.setdefault("question_depth", 2)
    st.session_state.setdefault("active_category", "All")


def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-lockup">
                <div class="brand-mark">IP</div>
                <div>
                    <strong>Interview Prep</strong>
                    <span>Student workspace</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="privacy-pill">Local-first and consent-based</div>', unsafe_allow_html=True)
        st.caption(
            "Resume analysis stays local. Optional Foundry IQ coaching sends only "
            "a reviewed question after consent."
        )

        st.markdown("#### Quick start")
        st.caption("Mock Interview is available in the page navigation.")
        if st.button(
            "Load example profile",
            use_container_width=True,
            icon=":material/description:",
        ):
            _load_sample()
            st.rerun()
        if st.button(
            "Reset workspace",
            use_container_width=True,
            icon=":material/restart_alt:",
        ):
            _reset_workspace()
            st.rerun()

        if "questions" in st.session_state:
            st.markdown("---")
            completed = len(st.session_state.feedback)
            total = len(st.session_state.questions)
            plan_complete = sum(
                bool(st.session_state.get(f"plan_done_{index}", False))
                for index in range(len(st.session_state.preparation_plan))
            )
            st.markdown("#### Session progress")
            st.metric("Answers reviewed", f"{completed} / {total}")
            st.progress(completed / total if total else 0)
            st.metric("Plan tasks complete", f"{plan_complete} / 7")

        st.markdown("---")
        st.markdown("#### Preparation flow")
        st.markdown(
            """
            <div class="flow-list">
                <span><b>01</b> Add your target role</span>
                <span><b>02</b> Review your readiness</span>
                <span><b>03</b> Practice out loud</span>
                <span><b>04</b> Follow the study plan</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_header() -> None:
    st.markdown(
        """
        <section class="hero">
            <div class="hero-copy">
                <span class="kicker">INTERVIEW PREPARATION, MADE PRACTICAL</span>
                <h1>Know what to prepare.<br><em>Practice with purpose.</em></h1>
                <p>Turn one resume and one job description into a focused plan you can
                understand, practice, and improve while keeping resume analysis local.</p>
                <div class="hero-points">
                    <span>Role fit</span><span>Resume review</span>
                    <span>Answer coaching</span><span>7-day plan</span>
                </div>
            </div>
            <div class="hero-panel">
                <div class="mini-label">HOW SCORING WORKS</div>
                <div class="score-line"><b>25%</b><span>Answer structure</span></div>
                <div class="score-line"><b>25%</b><span>Specific evidence</span></div>
                <div class="score-line"><b>20%</b><span>Personal ownership</span></div>
                <div class="score-line"><b>20%</b><span>Results and impact</span></div>
                <div class="score-line"><b>10%</b><span>Clear delivery</span></div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_setup():
    st.markdown('<div class="section-label">SET UP YOUR WORKSPACE</div>', unsafe_allow_html=True)
    resume_column, job_column = st.columns([0.9, 1.1], gap="large")

    with resume_column:
        st.markdown("### 1. Add your resume")
        input_method = st.radio(
            "Resume input method",
            ["Upload PDF or DOCX", "Paste resume text"],
            key="resume_input_method",
            horizontal=True,
            label_visibility="collapsed",
        )
        uploaded_file = None
        pasted_resume = ""
        if input_method == "Upload PDF or DOCX":
            uploaded_file = st.file_uploader(
                "Upload a PDF or DOCX",
                type=["pdf", "docx"],
                label_visibility="collapsed",
                help="Use a PDF or DOCX under 5 MB. PDFs are limited to 10 pages.",
            )
            st.caption("PDF or DOCX, maximum 5 MB.")
        else:
            pasted_resume = st.text_area(
                "Paste resume text",
                key="pasted_resume_text",
                height=205,
                label_visibility="collapsed",
                placeholder="Paste the complete text of your resume here...",
            )
            st.caption(f"{len(pasted_resume):,} characters")

        if (
            st.session_state.sample_resume_text
            and uploaded_file is None
            and not pasted_resume.strip()
        ):
            st.markdown(
                '<div class="input-ready"><b>Example resume ready</b>'
                "<span>Add your resume to replace it.</span></div>",
                unsafe_allow_html=True,
            )
            with st.expander("Preview resume text"):
                st.text(st.session_state.sample_resume_text[:2800])

    with job_column:
        st.markdown("### 2. Add the target role")
        job_description = st.text_area(
            "Paste job description",
            key="job_description",
            height=205,
            label_visibility="collapsed",
            placeholder=(
                "Paste the role title, responsibilities, requirements, and preferred skills..."
            ),
        )
        counter_column, depth_column = st.columns([1, 1.4])
        counter_column.caption(f"{len(job_description):,} characters")
        question_depth = depth_column.selectbox(
            "Questions per category",
            options=[2, 3],
            key="question_depth",
            help="Choose 6 or 9 total practice questions.",
        )
    return uploaded_file, pasted_resume, job_description, question_depth


def _build_workspace(
    uploaded_file,
    pasted_resume: str,
    job_description: str,
    question_depth: int,
) -> None:
    if (
        uploaded_file is None
        and not pasted_resume.strip()
        and not st.session_state.sample_resume_text
    ):
        st.error("Upload a resume, paste resume text, or load the example profile.")
        return
    if len(job_description.strip()) < 80:
        st.error("Paste a fuller job description so the role analysis is useful.")
        return

    try:
        with st.spinner("Building your private preparation workspace..."):
            if uploaded_file is not None:
                resume_text = extract_resume_text(uploaded_file, uploaded_file.name)
            elif pasted_resume.strip():
                resume_text = validate_resume_text(pasted_resume)
            else:
                resume_text = validate_resume_text(
                    st.session_state.sample_resume_text, source="example resume"
                )
            skill_match = compare_skills(resume_text, job_description)
            role_profile = analyze_job_description(job_description)
            resume_insights = analyze_resume(resume_text)
            questions = generate_questions(
                resume_text,
                job_description,
                skill_match,
                questions_per_category=question_depth,
            )
            plan = build_preparation_plan(skill_match, role_profile)
    except ResumeParsingError as exc:
        st.error(str(exc))
        return

    st.session_state.resume_text = resume_text
    st.session_state.skill_match = skill_match
    st.session_state.role_profile = role_profile
    st.session_state.resume_insights = resume_insights
    st.session_state.questions = questions
    st.session_state.preparation_plan = plan
    st.session_state.feedback = {}
    _clear_answer_widgets()
    st.success("Workspace ready. Your analysis appears below.")


def _render_workspace() -> None:
    role = st.session_state.role_profile
    st.markdown(
        f"""
        <div class="workspace-heading">
            <div>
                <div class="section-label">YOUR PREPARATION WORKSPACE</div>
                <h2>{html.escape(role.detected_title)}</h2>
            </div>
            <div class="role-tags">
                <span>{html.escape(role.role_family)}</span>
                <span>{html.escape(role.seniority)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    overview_tab, resume_tab, practice_tab, plan_tab = st.tabs(
        ["Overview", "Resume Lab", "Practice Room", "7-Day Plan"]
    )
    with overview_tab:
        _render_overview()
    with resume_tab:
        _render_resume_lab()
    with practice_tab:
        _render_practice_room()
    with plan_tab:
        _render_plan()


def _render_overview() -> None:
    match: SkillMatch = st.session_state.skill_match
    resume: ResumeInsights = st.session_state.resume_insights
    role: RoleProfile = st.session_state.role_profile
    completed = len(st.session_state.feedback)
    total = len(st.session_state.questions)

    cards = [
        (
            "Required match",
            f"{match.required_match_percentage:.0f}%",
            _match_label(match.required_match_percentage),
        ),
        ("Resume readiness", f"{resume.score}/100", _resume_label(resume.score)),
        ("Skills to review", str(len(match.missing_skills)), "Prioritized from the job post"),
        ("Practice progress", f"{completed}/{total}", "Answers reviewed"),
    ]
    columns = st.columns(4)
    for column, (label, value, note) in zip(columns, cards):
        with column:
            st.markdown(
                f"""
                <div class="metric-card">
                    <span>{label}</span>
                    <strong>{value}</strong>
                    <small>{note}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

    left, right = st.columns([1.2, 0.8], gap="large")
    with left:
        st.markdown("### Your role-fit snapshot")
        required_matches = [
            skill for skill in match.matched_skills if skill in match.required_skills
        ]
        required_gaps = [
            skill for skill in match.missing_skills if skill in match.required_skills
        ]
        st.markdown("**Required skills found on your resume**")
        _render_chips(required_matches, "positive")
        st.markdown("**Missing required skills**")
        _render_chips(required_gaps, "attention")
        if match.preferred_skills:
            st.markdown("**Preferred qualifications**")
            _render_chips(match.preferred_skills, "neutral")
        if not match.job_skills:
            st.info("Few catalog skills were detected. Include more of the full job post.")

        if match.matched_evidence:
            st.markdown("### Why these skills matched")
            st.caption(
                "Each match includes the exact resume text that triggered it."
            )
            for skill in match.matched_skills:
                evidence = match.matched_evidence.get(skill, [])
                with st.expander(f"{skill} | {len(evidence)} evidence item(s)"):
                    for snippet in evidence:
                        st.markdown(f"> {snippet}")

    with right:
        st.markdown("### What this role emphasizes")
        emphasis = role.emphasis_areas or [
            "Problem solving",
            "Team collaboration",
            "Learning agility",
        ]
        for index, area in enumerate(emphasis, start=1):
            st.markdown(
                f'<div class="emphasis-row"><b>{index:02d}</b><span>{area}</span></div>',
                unsafe_allow_html=True,
            )

    st.markdown("### Recommended next moves")
    next_moves = _next_moves(match, resume)
    move_columns = st.columns(3)
    for column, (number, title, description) in zip(move_columns, next_moves):
        with column:
            st.markdown(
                f"""
                <div class="action-card">
                    <span>{number}</span>
                    <h4>{title}</h4>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_resume_lab() -> None:
    resume: ResumeInsights = st.session_state.resume_insights
    st.markdown("### Resume readiness review")
    st.caption("Every check below is based on visible structure and wording in your resume.")

    score_column, detail_column = st.columns([0.35, 0.65], gap="large")
    with score_column:
        st.markdown(
            f"""
            <div class="score-card">
                <span>READINESS SCORE</span>
                <strong>{resume.score}</strong>
                <small>out of 100</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with detail_column:
        metrics = st.columns(4)
        metrics[0].metric("Words", resume.word_count)
        metrics[1].metric("Bullets", resume.bullet_count)
        metrics[2].metric("With numbers", resume.quantified_bullet_count)
        metrics[3].metric("Action-led", resume.action_verb_count)
        st.progress(resume.score / 100)
        st.caption(_resume_label(resume.score))

    section_column, recommendation_column = st.columns(2, gap="large")
    with section_column:
        st.markdown("#### Section check")
        for section in ("Education", "Skills", "Projects", "Experience"):
            found = section in resume.detected_sections
            status = "Found" if found else "Missing"
            css_class = "check-good" if found else "check-warn"
            st.markdown(
                f'<div class="check-row {css_class}"><span>{section}</span><b>{status}</b></div>',
                unsafe_allow_html=True,
            )
    with recommendation_column:
        st.markdown("#### Highest-impact edits")
        for index, recommendation in enumerate(resume.recommendations, start=1):
            st.markdown(
                f"""
                <div class="recommendation">
                    <b>{index:02d}</b><span>{recommendation}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with st.expander("Review extracted resume text"):
        st.text(st.session_state.resume_text[:12000])


def _render_practice_room() -> None:
    questions = st.session_state.questions
    feedback = st.session_state.feedback
    completed = len(feedback)

    heading_column, filter_column = st.columns([1.4, 0.6])
    with heading_column:
        st.markdown("### Practice room")
        st.caption(
            f"{completed} of {len(questions)} answers reviewed. Scores use the rubric shown above."
        )
    with filter_column:
        category = st.selectbox(
            "Filter questions",
            ["All", "Technical", "Behavioral", "Situational"],
            key="active_category",
        )
    st.progress(completed / len(questions) if questions else 0)

    visible_questions = [
        (index, question)
        for index, question in enumerate(questions)
        if category == "All" or question.category.value == category
    ]
    for display_number, (index, question) in enumerate(visible_questions, start=1):
        reviewed = index in feedback
        status = "Reviewed" if reviewed else "Not answered"
        with st.expander(
            f"{display_number}. {question.category.value} | {question.focus_area} | {status}",
            expanded=not reviewed and display_number == 1,
        ):
            st.markdown(
                f'<div class="question-type">{question.category.value.upper()}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f"#### {question.question}")
            st.caption(f"Why interviewers ask this: {question.why_asked}")

            with st.form(f"answer_form_{index}"):
                answer = st.text_area(
                    "Your practice answer",
                    key=f"answer_{index}",
                    height=190,
                    placeholder=(
                        "Write one specific example. For behavioral questions, use "
                        "Situation, Task, Action, Result."
                    ),
                )
                word_count = len(answer.split())
                st.caption(f"{word_count} words | Aim for 80-180 words")
                submitted = st.form_submit_button(
                    "Score this answer",
                    type="primary",
                    use_container_width=True,
                    icon=":material/check_circle:",
                )
            if submitted:
                try:
                    st.session_state.feedback[index] = evaluate_answer(question, answer)
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
            if reviewed:
                _render_feedback(feedback[index])


def _render_feedback(feedback: AnswerFeedback) -> None:
    st.markdown('<div class="feedback-divider"></div>', unsafe_allow_html=True)
    score_column, summary_column = st.columns([0.25, 0.75], gap="large")
    with score_column:
        st.markdown(
            f"""
            <div class="answer-score">
                <strong>{feedback.score}</strong>
                <span>ANSWER SCORE</span>
                <small>{feedback.word_count} words</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with summary_column:
        st.markdown("#### Coach notes")
        st.write(feedback.summary)
        st.progress(feedback.score / 100)

    st.markdown("#### Rubric breakdown")
    rubric_columns = st.columns(len(RUBRIC_WEIGHTS))
    for column, (name, weight) in zip(rubric_columns, RUBRIC_WEIGHTS.items()):
        score = feedback.rubric_scores[name]
        with column:
            st.metric(name, f"{score}/100", f"{weight}% weight", delta_color="off")

    strengths_column, gaps_column = st.columns(2, gap="large")
    with strengths_column:
        st.markdown("**What is working**")
        for item in feedback.strengths:
            st.markdown(f"- {item}")
    with gaps_column:
        st.markdown("**What to improve**")
        for item in feedback.weaknesses:
            st.markdown(f"- {item}")

    st.markdown("**Revise in this order**")
    for index, item in enumerate(feedback.recommendations, start=1):
        st.markdown(f"{index}. {item}")
    st.info(feedback.improved_answer, icon=":material/edit_note:")


def _render_plan() -> None:
    plan = st.session_state.preparation_plan
    st.markdown("### Your seven-day preparation plan")
    st.caption("About five hours total. Check off tasks as you complete them in this session.")

    total_minutes = sum(task.minutes for task in plan)
    complete_count = sum(
        bool(st.session_state.get(f"plan_done_{index}", False))
        for index in range(len(plan))
    )
    metric_columns = st.columns(3)
    metric_columns[0].metric("Total time", f"{total_minutes // 60}h {total_minutes % 60}m")
    metric_columns[1].metric("Tasks complete", f"{complete_count} / {len(plan)}")
    metric_columns[2].metric(
        "Plan progress", f"{round(complete_count / len(plan) * 100):.0f}%"
    )
    st.progress(complete_count / len(plan))

    for index, task in enumerate(plan):
        check_column, content_column, time_column = st.columns([0.08, 0.77, 0.15])
        with check_column:
            st.checkbox(
                f"Complete day {task.day}",
                key=f"plan_done_{index}",
                label_visibility="collapsed",
            )
        with content_column:
            st.markdown(
                f"""
                <div class="plan-item">
                    <span>DAY {task.day} / {task.category.upper()}</span>
                    <h4>{task.title}</h4>
                    <p>{task.description}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with time_column:
            st.markdown(
                f'<div class="time-pill">{task.minutes} min</div>',
                unsafe_allow_html=True,
            )

    report = build_markdown_report(
        st.session_state.role_profile,
        st.session_state.skill_match,
        st.session_state.resume_insights,
        st.session_state.questions,
        st.session_state.feedback,
        plan,
    )
    st.download_button(
        "Download preparation report",
        data=report,
        file_name="interview-preparation-report.md",
        mime="text/markdown",
        use_container_width=True,
        icon=":material/download:",
    )


def _render_empty_state() -> None:
    st.markdown(
        """
        <div class="empty-state">
            <span>START HERE</span>
            <h3>Your workspace will appear after analysis.</h3>
            <p>You will get a role-fit dashboard, resume review, tailored question set,
            transparent answer scoring, and a seven-day study plan.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_chips(items: list[str], chip_type: str) -> None:
    if not items:
        st.caption("None detected")
        return
    chips = "".join(
        f'<span class="skill-chip {chip_type}">{html.escape(item)}</span>'
        for item in items
    )
    st.markdown(f'<div class="chip-list">{chips}</div>', unsafe_allow_html=True)


def _next_moves(
    match: SkillMatch, resume: ResumeInsights
) -> list[tuple[str, str, str]]:
    required_gaps = [
        skill for skill in match.missing_skills if skill in match.required_skills
    ]
    gap_candidates = required_gaps or match.missing_skills
    gap = gap_candidates[0] if gap_candidates else "role fundamentals"
    resume_move = resume.recommendations[0]
    return [
        ("01", f"Review {gap}", "Learn enough to explain the basics and one practical use case."),
        ("02", "Strengthen the resume", resume_move),
        ("03", "Practice one answer", "Start with your strongest project and include a measured result."),
    ]


def _match_label(score: float) -> str:
    if score >= 75:
        return "Strong keyword alignment"
    if score >= 50:
        return "Good base with clear gaps"
    return "Focus your preparation"


def _resume_label(score: int) -> str:
    if score >= 80:
        return "Strong structure with room to tailor"
    if score >= 60:
        return "Solid foundation; add stronger evidence"
    return "Prioritize structure and project impact"


def _load_sample() -> None:
    st.session_state.sample_resume_text = SAMPLE_RESUME_PATH.read_text(encoding="utf-8")
    st.session_state.job_description = SAMPLE_JOB_PATH.read_text(encoding="utf-8")
    _clear_results()


def _reset_workspace() -> None:
    _clear_results()
    _clear_answer_widgets()
    st.session_state.sample_resume_text = ""
    st.session_state.pasted_resume_text = ""
    st.session_state.job_description = ""


def _clear_results() -> None:
    for key in (
        "resume_text",
        "skill_match",
        "role_profile",
        "resume_insights",
        "questions",
        "preparation_plan",
        "feedback",
    ):
        st.session_state.pop(key, None)
    st.session_state.feedback = {}


def _clear_answer_widgets() -> None:
    for key in list(st.session_state):
        if key.startswith(("answer_", "plan_done_")):
            del st.session_state[key]


def _apply_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

        :root {
            --ink: #17211b;
            --muted: #667069;
            --paper: #f5f2e9;
            --card: #fffdf7;
            --line: #dcd8ca;
            --green: #205c45;
            --lime: #c9f26b;
            --orange: #e8783e;
            --blue: #dceaf4;
        }
        .stApp {
            color: var(--ink);
            background:
                linear-gradient(rgba(32, 92, 69, 0.035) 1px, transparent 1px),
                linear-gradient(90deg, rgba(32, 92, 69, 0.035) 1px, transparent 1px),
                var(--paper);
            background-size: 32px 32px;
        }
        html, body, [class*="css"] { font-family: "DM Sans", sans-serif; }
        h1, h2, h3, h4 { font-family: "Manrope", sans-serif !important; color: var(--ink); }
        .block-container { max-width: 1240px; padding: 2rem 2.2rem 5rem; }
        section[data-testid="stSidebar"] {
            background: #173f31;
            border-right: 0;
        }
        section[data-testid="stSidebar"] * { color: #f7f4e9; }
        section[data-testid="stSidebar"] [data-testid="stMetric"] {
            background: rgba(255,255,255,0.08);
            border-color: rgba(255,255,255,0.14);
        }
        section[data-testid="stSidebar"] button {
            border-color: rgba(255,255,255,0.28);
            background: rgba(255,255,255,0.08);
        }
        .brand-lockup { display: flex; align-items: center; gap: .8rem; margin: .2rem 0 1rem; }
        .brand-lockup strong { display: block; font: 700 1rem "Manrope"; }
        .brand-lockup span { display: block; color: #b9c9c0 !important; font-size: .78rem; }
        .brand-mark {
            display: grid; place-items: center; width: 42px; height: 42px;
            border-radius: 12px; background: var(--lime); color: #173f31 !important;
            font: 800 .82rem "Manrope";
        }
        .privacy-pill {
            display: inline-block; margin-bottom: .35rem; padding: .35rem .65rem;
            border: 1px solid rgba(201,242,107,.35); border-radius: 999px;
            color: var(--lime) !important; font-size: .72rem; font-weight: 700;
            letter-spacing: .03em;
        }
        .flow-list { display: grid; gap: .75rem; }
        .flow-list span { display: flex; gap: .7rem; align-items: center; color: #d8e2dc !important; }
        .flow-list b { color: var(--lime) !important; font-size: .72rem; }
        .hero {
            display: grid; grid-template-columns: 1.5fr .72fr; gap: 2.5rem;
            margin-bottom: 2.3rem; padding: 3.2rem; border-radius: 28px;
            color: #f9f7ef; background:
                radial-gradient(circle at 85% 15%, rgba(201,242,107,.19), transparent 16rem),
                #173f31;
            box-shadow: 0 28px 70px rgba(23,63,49,.18);
        }
        .hero h1 {
            margin: .55rem 0 1rem; color: #fffdf7; font-size: clamp(2.4rem,5vw,4.5rem);
            line-height: 1.01; letter-spacing: -.055em;
        }
        .hero h1 em { color: var(--lime); font-style: normal; }
        .hero p { max-width: 720px; color: #cedbd4; font-size: 1.05rem; line-height: 1.7; }
        .kicker, .section-label, .mini-label, .question-type {
            color: var(--orange); font-size: .7rem; font-weight: 800; letter-spacing: .16em;
        }
        .hero-points { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: 1.35rem; }
        .hero-points span {
            padding: .45rem .72rem; border: 1px solid rgba(255,255,255,.18);
            border-radius: 999px; color: #edf4ef; font-size: .78rem;
        }
        .hero-panel {
            align-self: center; padding: 1.25rem; border: 1px solid rgba(255,255,255,.15);
            border-radius: 20px; background: rgba(255,255,255,.07);
        }
        .mini-label { color: var(--lime); margin-bottom: .6rem; }
        .score-line {
            display: flex; justify-content: space-between; padding: .72rem 0;
            border-bottom: 1px solid rgba(255,255,255,.1);
        }
        .score-line:last-child { border-bottom: 0; }
        .score-line b { color: #fff; }
        .score-line span { color: #c9d6cf; font-size: .86rem; }
        .section-label { margin: .5rem 0; color: var(--green); }
        .input-ready {
            display: flex; justify-content: space-between; padding: .85rem 1rem;
            border: 1px solid #a9c6b5; border-radius: 12px; background: #e7f2eb;
        }
        .input-ready span { color: var(--muted); font-size: .82rem; }
        .workspace-heading {
            display: flex; justify-content: space-between; align-items: end;
            margin: 3rem 0 1rem; padding-top: 2rem; border-top: 1px solid var(--line);
        }
        .workspace-heading h2 { margin: .15rem 0 0; font-size: 2rem; }
        .role-tags { display: flex; gap: .45rem; }
        .role-tags span, .time-pill {
            padding: .45rem .7rem; border-radius: 999px; background: #e2eadf;
            color: var(--green); font-size: .75rem; font-weight: 700;
        }
        button[kind="primary"] {
            min-height: 3.15rem; border-radius: 12px !important;
            background: var(--green) !important; border-color: var(--green) !important;
            font-weight: 700 !important;
        }
        button[kind="primary"]:hover { background: #164735 !important; }
        div[data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap: .35rem; padding: .35rem; border-radius: 14px; background: #e9e5da;
        }
        div[data-testid="stTabs"] button {
            border-radius: 10px; font-weight: 700;
        }
        div[data-testid="stTabs"] [aria-selected="true"] { background: var(--card); }
        .metric-card, .action-card, .score-card, .empty-state {
            height: 100%; padding: 1.25rem; border: 1px solid var(--line);
            border-radius: 18px; background: rgba(255,253,247,.92);
            box-shadow: 0 8px 24px rgba(50,55,45,.045);
        }
        .metric-card span { display: block; color: var(--muted); font-size: .8rem; }
        .metric-card strong { display: block; margin: .2rem 0; font: 800 2rem "Manrope"; }
        .metric-card small { color: var(--green); }
        .chip-list { display: flex; flex-wrap: wrap; gap: .5rem; margin: .6rem 0 1.35rem; }
        .skill-chip {
            display: inline-block; padding: .4rem .68rem; border-radius: 9px;
            font-size: .8rem; font-weight: 700;
        }
        .skill-chip.positive { color: #174e39; background: #dff1e5; }
        .skill-chip.attention { color: #884122; background: #f8e2d5; }
        .skill-chip.neutral { color: #274b60; background: #dceaf4; }
        .emphasis-row, .check-row, .recommendation {
            display: flex; align-items: center; gap: .85rem; margin-bottom: .55rem;
            padding: .78rem .9rem; border: 1px solid var(--line);
            border-radius: 11px; background: rgba(255,253,247,.75);
        }
        .emphasis-row b, .recommendation b { color: var(--orange); font-size: .72rem; }
        .check-row { justify-content: space-between; }
        .check-row b { font-size: .76rem; }
        .check-good b { color: var(--green); }
        .check-warn b { color: var(--orange); }
        .action-card span { color: var(--orange); font-size: .72rem; font-weight: 800; }
        .action-card h4 { margin: .75rem 0 .35rem; }
        .action-card p, .plan-item p { margin: 0; color: var(--muted); line-height: 1.55; }
        .score-card { display: grid; place-items: center; min-height: 190px; background: var(--green); }
        .score-card span, .score-card small { color: #cfddd5; }
        .score-card strong { color: var(--lime); font: 800 4rem "Manrope"; line-height: 1; }
        div[data-testid="stMetric"] {
            padding: .85rem; border: 1px solid var(--line);
            border-radius: 13px; background: rgba(255,253,247,.8);
        }
        div[data-testid="stExpander"] {
            margin-bottom: .7rem; border: 1px solid var(--line);
            border-radius: 14px; background: rgba(255,253,247,.78);
        }
        .question-type { display: inline-block; margin-bottom: .4rem; color: var(--orange); }
        .feedback-divider { height: 1px; margin: 1.3rem 0; background: var(--line); }
        .answer-score {
            display: grid; place-items: center; padding: 1.2rem; border-radius: 16px;
            background: var(--green);
        }
        .answer-score strong { color: var(--lime); font: 800 3rem "Manrope"; }
        .answer-score span, .answer-score small { color: #d8e5de; font-size: .7rem; }
        .plan-item { padding-bottom: 1.2rem; }
        .plan-item span { color: var(--orange); font-size: .68rem; font-weight: 800; letter-spacing: .1em; }
        .plan-item h4 { margin: .25rem 0; }
        .time-pill { display: inline-block; margin-top: .2rem; white-space: nowrap; }
        .empty-state { margin: 2rem 0; padding: 2.2rem; text-align: center; border-style: dashed; }
        .empty-state span { color: var(--orange); font-size: .7rem; font-weight: 800; letter-spacing: .14em; }
        .empty-state h3 { margin: .45rem 0; }
        .empty-state p { max-width: 660px; margin: auto; color: var(--muted); }
        div[data-testid="stProgress"] > div > div { background-color: var(--green); }
        textarea, div[data-baseweb="select"] > div { background: #fffdf8 !important; }
        @media (max-width: 900px) {
            .hero { grid-template-columns: 1fr; padding: 2rem; }
            .hero-panel { display: none; }
            .workspace-heading { align-items: start; flex-direction: column; gap: .8rem; }
        }
        @media (max-width: 640px) {
            .block-container { padding: 1rem 1rem 4rem; }
            .hero { padding: 1.5rem; border-radius: 20px; }
            .hero h1 { font-size: 2.45rem; }
            .hero-points { display: none; }
            .role-tags { flex-wrap: wrap; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
