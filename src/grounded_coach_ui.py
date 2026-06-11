"""Streamlit interface for local and Foundry IQ grounded coaching."""

from __future__ import annotations

import html

import streamlit as st

from src.foundry_iq import (
    FoundryIQClient,
    FoundryIQError,
    settings_from_mapping,
)
from src.local_knowledge import retrieve_local_guidance
from src.models import GroundedCoachingResponse


def run_grounded_coach_page() -> None:
    """Render the consent-gated grounded coaching experience."""

    st.set_page_config(
        page_title="Grounded Coach | Interview Prep Studio",
        page_icon="GC",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _apply_styles()
    settings = _load_foundry_settings()
    _render_sidebar(settings is not None)
    _render_header(settings is not None)

    if "skill_match" not in st.session_state:
        st.info(
            "Build the main preparation workspace first to receive role-specific prompts."
        )

    query = _render_query_builder()
    use_foundry = False
    consent = False
    if settings is not None:
        st.markdown("### Microsoft Foundry IQ")
        use_foundry = st.toggle(
            "Use Microsoft Foundry IQ for this question",
            value=False,
            help="When enabled, the question and selected context are sent to Azure AI Search.",
        )
        if use_foundry:
            consent = st.checkbox(
                "I understand that this question will be sent to my configured Azure resource."
            )
            st.caption(
                "The full resume is never sent. Only the text visible in the question box is used."
            )

    if st.button(
        "Get cited coaching",
        type="primary",
        use_container_width=True,
        icon=":material/menu_book:",
    ):
        if len(query.strip()) < 10:
            st.error("Enter a more specific coaching question.")
        elif use_foundry and not consent:
            st.error("Confirm consent before sending the question to Foundry IQ.")
        else:
            with st.spinner("Retrieving grounded guidance..."):
                response = _retrieve(query, settings if use_foundry else None)
            st.session_state.grounded_response = response

    if "grounded_response" in st.session_state:
        _render_response(st.session_state.grounded_response)


def _load_foundry_settings():
    try:
        values = st.secrets.get("foundry_iq")
    except (FileNotFoundError, KeyError):
        values = None
    return settings_from_mapping(values)


def _render_sidebar(foundry_ready: bool) -> None:
    with st.sidebar:
        st.markdown("## Grounded Coach")
        if foundry_ready:
            st.success("Foundry IQ configured")
        else:
            st.info("Local cited knowledge mode")
        st.caption(
            "Guidance is grounded in a knowledge source and displayed with citations."
        )
        st.markdown("---")
        st.markdown("**Privacy boundary**")
        st.caption(
            "Resume content is processed locally. Foundry receives only the coaching "
            "question that the user reviews and explicitly approves."
        )


def _render_header(foundry_ready: bool) -> None:
    status = "FOUNDRY IQ READY" if foundry_ready else "LOCAL KNOWLEDGE READY"
    st.markdown(
        f"""
        <div class="coach-hero">
            <span>{status}</span>
            <h1>Ask for guidance you can trace back to a source.</h1>
            <p>Turn skill gaps and interview questions into grounded preparation advice,
            with a visible citation trail and an explicit privacy boundary.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_query_builder() -> str:
    default_query = ""
    if "skill_match" in st.session_state:
        match = st.session_state.skill_match
        required_gaps = [
            skill for skill in match.missing_skills if skill in match.required_skills
        ]
        gap = (required_gaps or match.missing_skills or ["technical interviews"])[0]
        role = st.session_state.role_profile.detected_title
        default_query = (
            f"How should a student prepare to discuss {gap} in an interview for "
            f"{role}? Give practical steps and explain what a strong answer should include."
        )
    return st.text_area(
        "Coaching question",
        value=default_query,
        height=150,
        placeholder=(
            "Example: How should I structure a strong teamwork answer for a software "
            "engineering internship?"
        ),
    )


def _retrieve(query: str, settings) -> GroundedCoachingResponse:
    if settings is None:
        return retrieve_local_guidance(query)
    try:
        return FoundryIQClient(settings).retrieve(query)
    except FoundryIQError as exc:
        st.warning(
            f"Foundry IQ was unavailable, so local cited guidance was used. {exc}"
        )
        return retrieve_local_guidance(query)


def _render_response(response: GroundedCoachingResponse) -> None:
    st.markdown("---")
    provider_column, citation_column = st.columns(2)
    provider_column.metric("Knowledge provider", response.provider)
    citation_column.metric("Citations", len(response.citations))
    st.markdown("### Grounded guidance")
    st.markdown(response.answer)

    st.markdown("### Sources")
    if not response.citations:
        st.warning("The provider returned no citation metadata.")
    for citation in response.citations:
        with st.expander(
            f"[{citation.citation_id}] {html.escape(citation.title)}"
        ):
            if citation.source.startswith("http"):
                st.markdown(f"[Open source]({citation.source})")
            else:
                st.code(citation.source)
            if citation.excerpt:
                st.write(citation.excerpt)

    if response.activity_summary:
        with st.expander("Retrieval activity"):
            for item in response.activity_summary:
                st.markdown(f"- {item}")


def _apply_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
        .stApp { background: #f5f2e9; color: #17211b; }
        html, body, [class*="css"] { font-family: "DM Sans", sans-serif; }
        h1, h2, h3 { font-family: "Manrope", sans-serif !important; }
        .block-container { max-width: 1080px; padding: 2.4rem 2rem 5rem; }
        section[data-testid="stSidebar"] { background: #173f31; }
        section[data-testid="stSidebar"] * { color: #f8f4e9; }
        .coach-hero {
            padding: 2.8rem; margin-bottom: 1.5rem; border-radius: 26px;
            background: #173f31; color: #fff;
        }
        .coach-hero span { color: #c9f26b; font-size: .72rem; font-weight: 800; letter-spacing: .14em; }
        .coach-hero h1 { margin: .5rem 0; color: #fff; font-size: 2.7rem; }
        .coach-hero p { max-width: 760px; color: #d2dfd8; line-height: 1.65; }
        button[kind="primary"] {
            min-height: 3.1rem; border-radius: 12px !important;
            background: #205c45 !important; border-color: #205c45 !important;
            font-weight: 700 !important;
        }
        div[data-testid="stMetric"], div[data-testid="stExpander"] {
            border: 1px solid #dcd8ca; border-radius: 14px; background: #fffdf7;
        }
        div[data-testid="stMetric"] { padding: .9rem; }
        textarea { background: #fffdf8 !important; }
        @media (max-width: 700px) {
            .block-container { padding: 1rem 1rem 4rem; }
            .coach-hero { padding: 1.5rem; }
            .coach-hero h1 { font-size: 2rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
