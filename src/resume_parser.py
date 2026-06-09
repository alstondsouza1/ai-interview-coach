"""Utilities for validating and extracting text from PDF resumes."""

from __future__ import annotations

from io import BytesIO
from typing import BinaryIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
MAX_PAGES = 10


class ResumeParsingError(ValueError):
    """Raised when an uploaded resume cannot be safely parsed."""


def extract_text_from_pdf(file: BinaryIO | bytes) -> str:
    """Extract readable text from a PDF resume.

    Args:
        file: Uploaded PDF as bytes or a binary file-like object.

    Returns:
        Cleaned text from every page in the PDF.

    Raises:
        ResumeParsingError: If the file is invalid, too large, or has no text.
    """

    raw_bytes = file if isinstance(file, bytes) else file.read()
    if not raw_bytes:
        raise ResumeParsingError("The uploaded PDF is empty.")
    if len(raw_bytes) > MAX_FILE_SIZE_BYTES:
        raise ResumeParsingError("The resume must be smaller than 5 MB.")

    try:
        reader = PdfReader(BytesIO(raw_bytes))
    except (PdfReadError, ValueError, TypeError) as exc:
        raise ResumeParsingError("The uploaded file is not a valid PDF.") from exc

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as exc:
            raise ResumeParsingError("Password-protected PDFs are not supported.") from exc

    if len(reader.pages) > MAX_PAGES:
        raise ResumeParsingError("Please upload a resume with 10 pages or fewer.")

    page_text = [page.extract_text() or "" for page in reader.pages]
    text = _clean_text("\n".join(page_text))
    if not text:
        raise ResumeParsingError(
            "No readable text was found. Try exporting the resume as a text-based PDF."
        )
    return text


def _clean_text(text: str) -> str:
    """Remove repeated whitespace while preserving useful line breaks."""

    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()

