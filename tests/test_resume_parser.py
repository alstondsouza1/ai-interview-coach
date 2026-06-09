"""Tests for PDF resume parsing helpers."""

from io import BytesIO

import pytest

from src.resume_parser import ResumeParsingError, extract_text_from_pdf


def test_empty_pdf_is_rejected() -> None:
    with pytest.raises(ResumeParsingError, match="empty"):
        extract_text_from_pdf(BytesIO(b""))


def test_invalid_pdf_is_rejected() -> None:
    with pytest.raises(ResumeParsingError, match="valid PDF"):
        extract_text_from_pdf(BytesIO(b"not a pdf"))

