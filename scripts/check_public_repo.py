"""Fail when common credential patterns appear in tracked project files."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".docx", ".db"}
PATTERNS = {
    "Azure AI Search key": re.compile(r"\b[0-9A-Za-z]{52}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "Private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "Generic secret assignment": re.compile(
        r"(?i)\b(?:api[_-]?key|password|secret|token)\s*[:=]\s*['\"][^'\"]{12,}['\"]"
    ),
}
ALLOWED_PLACEHOLDERS = (
    "YOUR-",
    "YOUR_",
    "secret-value",
    "example.search.windows.net",
)


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [ROOT / line for line in result.stdout.splitlines() if line]


def scan_file(path: Path) -> list[str]:
    if path.suffix.casefold() in EXCLUDED_SUFFIXES:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    findings = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if any(placeholder in line for placeholder in ALLOWED_PLACEHOLDERS):
            continue
        for name, pattern in PATTERNS.items():
            if pattern.search(line):
                findings.append(f"{path.relative_to(ROOT)}:{line_number}: {name}")
    return findings


def main() -> int:
    findings = [
        finding
        for path in tracked_files()
        for finding in scan_file(path)
    ]
    if findings:
        print("Potential secrets found:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("No common credential patterns found in tracked files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
