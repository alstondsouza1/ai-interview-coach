"""Streamlit dashboard for aggregate local interview history."""

from __future__ import annotations

from statistics import mean

import streamlit as st

from src.history_store import delete_all_history, list_mock_sessions


def run_progress_page() -> None:
    """Render saved score trends and privacy controls."""

    st.set_page_config(
        page_title="Progress | Interview Prep Studio",
        page_icon="PG",
        layout="wide",
    )
    _apply_styles()
    st.markdown(
        """
        <div class="progress-hero">
            <span>LOCAL PROGRESS ANALYTICS</span>
            <h1>See whether your interview practice is improving.</h1>
            <p>Only aggregate scores and timing are stored. Resume text and answers
            are never written to the history database.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sessions = list_mock_sessions()
    if not sessions:
        st.info("Complete a Mock Interview to create your first progress record.")
        return

    _render_metrics(sessions)
    _render_trends(sessions)
    _render_recent_sessions(sessions)
    _render_privacy_controls()


def _render_metrics(sessions: list[dict]) -> None:
    newest = sessions[0]
    oldest = sessions[-1]
    score_change = newest["overall_score"] - oldest["overall_score"]
    columns = st.columns(4)
    columns[0].metric("Completed interviews", len(sessions))
    columns[1].metric("Latest score", f"{newest['overall_score']}/100")
    columns[2].metric("Average score", f"{round(mean(s['overall_score'] for s in sessions))}/100")
    columns[3].metric("Change since first", score_change)


def _render_trends(sessions: list[dict]) -> None:
    chronological = list(reversed(sessions))
    st.markdown("### Readiness score trend")
    st.line_chart(
        {
            "Attempt": list(range(1, len(chronological) + 1)),
            "Score": [session["overall_score"] for session in chronological],
        },
        x="Attempt",
        y="Score",
    )

    latest = sessions[0]
    category_column, rubric_column = st.columns(2, gap="large")
    with category_column:
        st.markdown("### Latest category scores")
        st.bar_chart(
            {
                "Category": list(latest["category_scores"]),
                "Score": list(latest["category_scores"].values()),
            },
            x="Category",
            y="Score",
            horizontal=True,
        )
    with rubric_column:
        st.markdown("### Latest rubric scores")
        st.bar_chart(
            {
                "Rubric": list(latest["rubric_scores"]),
                "Score": list(latest["rubric_scores"].values()),
            },
            x="Rubric",
            y="Score",
            horizontal=True,
        )


def _render_recent_sessions(sessions: list[dict]) -> None:
    st.markdown("### Recent interviews")
    for session in sessions[:10]:
        with st.expander(
            f"{session['created_at'][:10]} | {session['role_title']} | "
            f"{session['overall_score']}/100"
        ):
            st.write(f"Readiness: **{session['readiness_label']}**")
            st.write(
                f"Average response time: **{session['average_time_seconds']} seconds**"
            )
            if session["strengths"]:
                st.write("Strengths: " + " ".join(session["strengths"]))
            if session["weaknesses"]:
                st.write("Focus: " + " ".join(session["weaknesses"]))


def _render_privacy_controls() -> None:
    st.markdown("---")
    with st.expander("Privacy and local data controls"):
        st.write(
            "Stored fields: role title, date, aggregate score, category scores, "
            "rubric scores, readiness label, and timing. No resume or answer text."
        )
        confirm = st.checkbox("I understand this deletes all saved progress.")
        if st.button("Delete all local history", disabled=not confirm):
            delete_all_history()
            st.success("Local interview history deleted.")
            st.rerun()


def _apply_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #f5f2e9; color: #17211b; }
        .block-container { max-width: 1120px; padding: 2.4rem 2rem 5rem; }
        .progress-hero {
            padding: 2.6rem; margin-bottom: 1.5rem; border-radius: 26px;
            background: #173f31; color: #fff;
        }
        .progress-hero span { color: #c9f26b; font-size: .72rem; font-weight: 800; letter-spacing: .14em; }
        .progress-hero h1 { margin: .5rem 0; color: #fff; font-size: 2.6rem; }
        .progress-hero p { max-width: 760px; color: #d2dfd8; }
        div[data-testid="stMetric"], div[data-testid="stExpander"] {
            border: 1px solid #dcd8ca; border-radius: 14px; background: #fffdf7;
        }
        div[data-testid="stMetric"] { padding: .9rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )
