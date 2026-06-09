"""Streamlit interface for the timed, fully local mock interview."""

from __future__ import annotations

import time

import streamlit as st

from src.answer_evaluator import evaluate_answer
from src.mock_interview import (
    MOCK_QUESTION_TOTAL,
    generate_mock_questions,
    summarize_mock_interview,
    timer_status,
)
from src.models import MockInterviewAnswer, MockInterviewSummary

DEFAULT_QUESTION_SECONDS = 120


def run_mock_interview_page() -> None:
    """Render the complete one-question-at-a-time interview workflow."""

    st.set_page_config(
        page_title="Mock Interview | Interview Prep Studio",
        page_icon="MI",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _apply_mock_styles()
    _initialize_mock_state()
    _render_sidebar()

    if "skill_match" not in st.session_state:
        _render_missing_workspace()
        return

    if not st.session_state.mock_started:
        _render_landing()
    elif st.session_state.mock_complete:
        _render_results()
    else:
        _render_active_question()


def _initialize_mock_state() -> None:
    defaults = {
        "mock_started": False,
        "mock_complete": False,
        "mock_questions": [],
        "mock_answers": [],
        "mock_index": 0,
        "mock_question_seconds": DEFAULT_QUESTION_SECONDS,
        "mock_question_started_at": 0.0,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## Mock Interview")
        st.caption("A timed, local interview using the resume and role in your workspace.")
        st.caption("Use the page navigation above to return to the main workspace.")

        if st.session_state.mock_started:
            completed = len(st.session_state.mock_answers)
            st.markdown("---")
            st.metric("Questions completed", f"{completed} / {MOCK_QUESTION_TOTAL}")
            st.progress(completed / MOCK_QUESTION_TOTAL)
            st.metric(
                "Time per question",
                f"{st.session_state.mock_question_seconds // 60}:"
                f"{st.session_state.mock_question_seconds % 60:02d}",
            )
            if st.button(
                "End and reset interview",
                use_container_width=True,
                icon=":material/restart_alt:",
            ):
                _reset_mock_interview()
                st.rerun()

        st.markdown("---")
        st.caption(
            "No answers leave this browser session. Scoring uses the same transparent "
            "Structure, Specificity, Ownership, Impact, and Clarity rubric."
        )


def _render_missing_workspace() -> None:
    st.markdown(
        """
        <div class="mock-hero">
            <span>WORKSPACE REQUIRED</span>
            <h1>Prepare the role before starting the interview.</h1>
            <p>The mock interview needs your analyzed resume and job description so it
            can select relevant technical questions and skill gaps.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("Open the main Interview Prep Studio page from the sidebar to begin.")


def _render_landing() -> None:
    role = st.session_state.role_profile
    match = st.session_state.skill_match
    st.markdown(
        f"""
        <div class="mock-hero">
            <span>TIMED MOCK INTERVIEW</span>
            <h1>Practice the full interview, one question at a time.</h1>
            <p>10 questions for <b>{role.detected_title}</b>, selected from your
            resume evidence, required skill gaps, and entry-level interview fundamentals.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_columns = st.columns(4)
    metric_columns[0].metric("Questions", "10")
    metric_columns[1].metric("Technical", "4")
    metric_columns[2].metric("Behavioral", "3")
    metric_columns[3].metric("Situational", "3")

    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        st.markdown("### Interview rules")
        st.markdown(
            """
            1. Questions appear one at a time.
            2. The timer starts as soon as each question appears.
            3. Submit a complete answer before moving forward.
            4. Coaching is hidden until the interview is finished.
            5. The final report compares categories and rubric areas.
            """
        )
        st.info(
            "A timeout is recorded for pacing feedback, but you can still finish and "
            "submit the answer.",
            icon=":material/timer:",
        )
    with right:
        st.markdown("### Session settings")
        duration = st.select_slider(
            "Time per question",
            options=[60, 90, 120, 180],
            value=st.session_state.mock_question_seconds,
            format_func=lambda seconds: f"{seconds // 60}:{seconds % 60:02d}",
        )
        st.session_state.mock_question_seconds = duration
        st.markdown("**Required skills being tested**")
        skills = match.required_skills or match.job_skills
        st.write(", ".join(skills[:8]) or "General software engineering fundamentals")

    if st.button(
        "Start 10-question interview",
        type="primary",
        use_container_width=True,
        icon=":material/play_arrow:",
    ):
        _start_mock_interview()
        st.rerun()


def _render_active_question() -> None:
    index = st.session_state.mock_index
    question = st.session_state.mock_questions[index]
    completed = len(st.session_state.mock_answers)

    st.markdown(
        f"""
        <div class="question-header">
            <div>
                <span>QUESTION {index + 1} OF {MOCK_QUESTION_TOTAL}</span>
                <h1>{question.category.value}: {question.focus_area}</h1>
            </div>
            <div class="question-progress">{completed * 10}% complete</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(completed / MOCK_QUESTION_TOTAL)

    timer_column, question_column = st.columns([0.24, 0.76], gap="large")
    with timer_column:
        _render_countdown()
        st.markdown(
            f"""
            <div class="category-card">
                <span>CATEGORY</span>
                <strong>{question.category.value}</strong>
                <small>{question.focus_area}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with question_column:
        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown(f"## {question.question}")
        st.caption("Answer as if you were speaking directly to the interviewer.")
        with st.form(f"mock_answer_form_{index}"):
            answer = st.text_area(
                "Your answer",
                key=f"mock_answer_{index}",
                height=260,
                placeholder=(
                    "Use a concrete example, explain your decisions, and finish with "
                    "the outcome or lesson learned..."
                ),
            )
            word_count = len(answer.split())
            st.caption(f"{word_count} words | Suggested range: 80-180 words")
            submitted = st.form_submit_button(
                "Submit and continue",
                type="primary",
                use_container_width=True,
                icon=":material/arrow_forward:",
            )
        st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        try:
            _submit_mock_answer(answer)
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))


@st.fragment(run_every=1)
def _render_countdown() -> None:
    """Refresh only the timer instead of rerunning the answer form."""

    _, remaining, _ = timer_status(
        st.session_state.mock_question_started_at,
        st.session_state.mock_question_seconds,
        time.time(),
    )
    minutes, seconds = divmod(remaining, 60)
    timer_class = "timer-card warning" if remaining <= 20 else "timer-card"
    status = "Time expired" if remaining == 0 else "Time remaining"
    st.markdown(
        f"""
        <div class="{timer_class}">
            <span>{status}</span>
            <strong>{minutes:02d}:{seconds:02d}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _submit_mock_answer(answer: str) -> None:
    index = st.session_state.mock_index
    question = st.session_state.mock_questions[index]
    elapsed, _, timed_out = timer_status(
        st.session_state.mock_question_started_at,
        st.session_state.mock_question_seconds,
        time.time(),
    )
    feedback = evaluate_answer(question, answer)
    record = MockInterviewAnswer(
        question_index=index,
        question=question,
        answer=" ".join(answer.split()),
        feedback=feedback,
        time_taken_seconds=elapsed,
        timed_out=timed_out,
    )
    st.session_state.mock_answers.append(record)
    st.session_state.mock_index += 1

    if st.session_state.mock_index >= MOCK_QUESTION_TOTAL:
        st.session_state.mock_complete = True
    else:
        st.session_state.mock_question_started_at = time.time()


def _render_results() -> None:
    summary = summarize_mock_interview(st.session_state.mock_answers)
    st.markdown(
        f"""
        <div class="results-hero">
            <span>INTERVIEW COMPLETE</span>
            <h1>{summary.readiness_label}</h1>
            <p>Your readiness score is based on all 10 locally evaluated answers.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _render_summary_metrics(summary)

    category_column, rubric_column = st.columns(2, gap="large")
    with category_column:
        st.markdown("### Performance by category")
        category_data = {
            "Category": list(summary.category_scores),
            "Score": list(summary.category_scores.values()),
        }
        st.bar_chart(category_data, x="Category", y="Score", horizontal=True)
    with rubric_column:
        st.markdown("### Average rubric performance")
        rubric_data = {
            "Rubric": list(summary.rubric_scores),
            "Score": list(summary.rubric_scores.values()),
        }
        st.bar_chart(rubric_data, x="Rubric", y="Score", horizontal=True)

    strength_column, weakness_column = st.columns(2, gap="large")
    with strength_column:
        st.markdown("### Consistent strengths")
        for item in summary.strengths or ["No repeated strength area was detected yet."]:
            st.success(item, icon=":material/check_circle:")
    with weakness_column:
        st.markdown("### Priority weaknesses")
        for item in summary.weaknesses or ["No repeated weakness area was detected."]:
            st.warning(item, icon=":material/priority_high:")

    st.markdown("### Question-by-question review")
    for item in st.session_state.mock_answers:
        timeout_label = " | Timed out" if item.timed_out else ""
        with st.expander(
            f"{item.question_index + 1}. {item.question.category.value} | "
            f"{item.feedback.score}/100{timeout_label}"
        ):
            st.markdown(f"**{item.question.question}**")
            st.markdown("**Your answer**")
            st.write(item.answer)
            st.markdown("**What worked**")
            for strength in item.feedback.strengths:
                st.markdown(f"- {strength}")
            st.markdown("**What to improve**")
            for weakness in item.feedback.weaknesses:
                st.markdown(f"- {weakness}")
            st.info(item.feedback.improved_answer, icon=":material/edit_note:")

    if st.button(
        "Start another mock interview",
        type="primary",
        use_container_width=True,
        icon=":material/replay:",
    ):
        _reset_mock_interview()
        st.rerun()


def _render_summary_metrics(summary: MockInterviewSummary) -> None:
    columns = st.columns(4)
    columns[0].metric("Readiness score", f"{summary.overall_score}/100")
    columns[1].metric("Questions completed", f"{summary.completed_questions}/10")
    columns[2].metric(
        "Average response time",
        f"{summary.average_time_seconds // 60}:"
        f"{summary.average_time_seconds % 60:02d}",
    )
    timed_out = sum(answer.timed_out for answer in st.session_state.mock_answers)
    columns[3].metric("Timed-out answers", timed_out)
    st.progress(summary.overall_score / 100)


def _start_mock_interview() -> None:
    st.session_state.mock_questions = generate_mock_questions(
        st.session_state.skill_match
    )
    st.session_state.mock_answers = []
    st.session_state.mock_index = 0
    st.session_state.mock_complete = False
    st.session_state.mock_started = True
    st.session_state.mock_question_started_at = time.time()
    _clear_mock_answer_widgets()


def _reset_mock_interview() -> None:
    st.session_state.mock_started = False
    st.session_state.mock_complete = False
    st.session_state.mock_questions = []
    st.session_state.mock_answers = []
    st.session_state.mock_index = 0
    st.session_state.mock_question_started_at = 0.0
    _clear_mock_answer_widgets()


def _clear_mock_answer_widgets() -> None:
    for key in list(st.session_state):
        if key.startswith("mock_answer_"):
            del st.session_state[key]


def _apply_mock_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
        :root {
            --ink: #17211b; --paper: #f5f2e9; --card: #fffdf7;
            --green: #205c45; --lime: #c9f26b; --orange: #e8783e;
            --line: #dcd8ca; --muted: #667069;
        }
        .stApp { color: var(--ink); background: var(--paper); }
        html, body, [class*="css"] { font-family: "DM Sans", sans-serif; }
        h1, h2, h3 { font-family: "Manrope", sans-serif !important; color: var(--ink); }
        .block-container { max-width: 1180px; padding: 2.3rem 2rem 5rem; }
        section[data-testid="stSidebar"] { background: #173f31; }
        section[data-testid="stSidebar"] * { color: #f8f4e9; }
        .mock-hero, .results-hero {
            margin-bottom: 1.8rem; padding: 2.8rem; border-radius: 26px;
            color: #fff; background:
                radial-gradient(circle at 90% 10%, rgba(201,242,107,.22), transparent 18rem),
                #173f31;
        }
        .mock-hero span, .results-hero span, .question-header span, .category-card span {
            color: var(--orange); font-size: .7rem; font-weight: 800; letter-spacing: .14em;
        }
        .mock-hero h1, .results-hero h1 { margin: .45rem 0; color: #fff; font-size: 2.8rem; }
        .mock-hero p, .results-hero p { max-width: 780px; color: #d3dfd8; }
        .question-header {
            display: flex; justify-content: space-between; align-items: end; margin-bottom: 1rem;
        }
        .question-header h1 { margin: .25rem 0; }
        .question-progress { color: var(--green); font-weight: 700; }
        .timer-card, .category-card, .question-card {
            padding: 1.25rem; border: 1px solid var(--line); border-radius: 18px;
            background: var(--card);
        }
        .timer-card { display: grid; place-items: center; margin-bottom: 1rem; background: var(--green); }
        .timer-card span { color: #d5e2db; font-size: .75rem; }
        .timer-card strong { color: var(--lime); font: 800 2.8rem "Manrope"; }
        .timer-card.warning { background: #8d3d24; }
        .timer-card.warning strong { color: #fff0c7; }
        .category-card strong, .category-card small { display: block; }
        .category-card strong { margin: .4rem 0; }
        .category-card small { color: var(--muted); }
        .question-card { padding: 1.8rem; }
        .question-card h2 { line-height: 1.35; }
        button[kind="primary"] {
            min-height: 3.1rem; border-radius: 12px !important;
            background: var(--green) !important; border-color: var(--green) !important;
            font-weight: 700 !important;
        }
        div[data-testid="stMetric"], div[data-testid="stExpander"] {
            border: 1px solid var(--line); border-radius: 14px; background: var(--card);
        }
        div[data-testid="stMetric"] { padding: .9rem; }
        div[data-testid="stProgress"] > div > div { background-color: var(--green); }
        textarea, div[data-baseweb="select"] > div { background: #fffdf8 !important; }
        @media (max-width: 760px) {
            .block-container { padding: 1rem 1rem 4rem; }
            .mock-hero, .results-hero { padding: 1.5rem; border-radius: 18px; }
            .mock-hero h1, .results-hero h1 { font-size: 2rem; }
            .question-header { align-items: start; flex-direction: column; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
