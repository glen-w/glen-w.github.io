#!/usr/bin/env python3
"""Assess whether the catalogue of failures is safe to publish.

Reads the local cards under assets/failures/ and the Jekyll pages under
_failures/ and _pages/failures.md. Those paths are gitignored; this script
lives in the repo so the gate can be run before anything is made public.

Blockers are privacy leaks and machinery that should not be on a public page.
Warnings are formatting leftovers that do not by themselves expose someone.

Exit status is 0 when there are no blockers. --strict also fails on warnings.

Usage:
  python3 scripts/check_failures_readiness.py
  python3 scripts/check_failures_readiness.py --strict
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "assets" / "failures"
PAGES = ROOT / "_failures"
INDEX = ROOT / "_pages" / "failures.md"

# Glen's own addresses stay visible. Any other address is a blocker.
KEEP_EMAILS = {
    "glen.w.wright@gmail.com",
    "glen.wright@iddri.org",
    "glen.wright@sciencespo.fr",
}

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(
    r"\b(?:\+61[\s\-]?|0[2-478][\s\-]?)(?:\d[\s\-]?){8}\d\b"
    r"|\b\+\d{1,3}[\s\-]\d{2,4}[\s\-]\d{3,4}[\s\-]\d{3,4}\b"
)
CONTROL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\u2028\u2029\u0085]")
HTML_RE = re.compile(
    r"</?(?:div|p|br|span|a|html|body|table|ul|ol|li|font|img|b|strong|em|i)\b(?:\s[^<>]{0,200})?>",
    re.I,
)
SOURCE_RE = re.compile(
    r"(?m)^(?:# Job advertisement|# Related emails|# Redacted application materials|## Source:|_Source:)"
)
ADDRESS_RE = re.compile(
    r"\[REDACTED ADDRESS\]|Castle Hill|Empire Circuit|Lenton Boulevard|Avenue du Maine|"
    r"\b2154\b|\bNG7 2FQ\b",
    re.I,
)
SHARPIE_EMAIL_RE = re.compile(r"█+\s*<\[REDACTED EMAIL\]>")
PLACEHOLDER_RE = re.compile(r"\[REDACTED (?:EMAIL|PHONE|ADDRESS|PASSPORT|DOB)\]")
PATH_RE = re.compile(r"/Users/|Admin/job applications|job applications\.sbd")
PAGE_FURNITURE_RE = re.compile(r"(?m)^\s*\d+\s+of\s+\d+\s*$")
GLEN_LINE_RE = re.compile(r"(?m)^\s*Glen (?:William )?Wright\s*$")
WRAP_RE_LINE = re.compile(r"[A-Za-z,]$")
APP_TITLE_RE = re.compile(r"^# Application for .+ \(.+\)\s*$")
DATE_CORRUPT_RE = re.compile(r"(?:\[REDACTED PHONE\]|█{4,})T\d{2}:")


class Finding:
    def __init__(self, severity: str, path: Path, detail: str) -> None:
        self.severity = severity
        self.path = path
        self.detail = detail

    def __str__(self) -> str:
        rel = self.path.relative_to(ROOT) if self.path.is_absolute() else self.path
        return f"{self.severity}: {rel}: {self.detail}"


def card_files() -> list[Path]:
    if not CARDS.is_dir():
        return []
    return sorted(
        p
        for p in CARDS.glob("*/*.md")
        if p.name in {"application.md", "job-ad.md", "emails.md"}
    )


def add_line_hits(findings: list[Finding], path: Path, text: str, pattern: re.Pattern[str], severity: str, label: str, limit: int = 5) -> None:
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if pattern.search(line):
            hits.append(i)
            if len(hits) >= limit:
                break
    if hits:
        more = "" if len(hits) < limit else "+"
        findings.append(Finding(severity, path, f"{label} on line(s) {', '.join(map(str, hits))}{more}"))


def check_file(path: Path, findings: list[Finding]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    if CONTROL_RE.search(text):
        findings.append(Finding("blocker", path, "control character (form feed or similar)"))
    if HTML_RE.search(text):
        findings.append(Finding("blocker", path, "HTML tag left in the card"))
    if SOURCE_RE.search(text):
        findings.append(Finding("blocker", path, "source or pipeline header"))
    if PATH_RE.search(text):
        findings.append(Finding("blocker", path, "local path or mailbox name"))
    if SHARPIE_EMAIL_RE.search(text):
        findings.append(Finding("blocker", path, "redacted name still followed by <[REDACTED EMAIL]>"))
    if PLACEHOLDER_RE.search(text):
        findings.append(Finding("blocker", path, "bracket redaction label; use a blackout bar"))
    if any(PHONE_RE.search(line) and "REDACTED PHONE" not in line for line in text.splitlines()):
        findings.append(Finding("blocker", path, "phone number that is not redacted"))
    add_line_hits(findings, path, text, ADDRESS_RE, "blocker", "address leftover")
    emails = sorted({m.group(0).lower() for m in EMAIL_RE.finditer(text)} - KEEP_EMAILS)
    if emails:
        findings.append(Finding("blocker", path, f"unredacted email ({len(emails)} distinct)"))
    if path.name == "emails.md" and "No matching messages" in text:
        findings.append(Finding("blocker", path, "empty email file should not exist"))
    if DATE_CORRUPT_RE.search(text):
        findings.append(Finding("warning", path, "date field was partly redacted as a phone number"))
    if PAGE_FURNITURE_RE.search(text):
        findings.append(Finding("warning", path, "PDF page number left in the text"))
    if path.name == "application.md":
        if GLEN_LINE_RE.search(text):
            findings.append(Finding("warning", path, "standalone Glen Wright line"))
        first = next((ln for ln in text.splitlines() if ln.strip()), "")
        if not APP_TITLE_RE.match(first):
            findings.append(Finding("blocker", path, f"title is not 'Application for Role (Org)': {first[:80]}"))
        wraps = 0
        lines = text.splitlines()
        for i, line in enumerate(lines[:-1]):
            nxt = lines[i + 1].strip()
            if len(line.rstrip()) >= 70 and WRAP_RE_LINE.search(line.rstrip()) and nxt[:1].islower():
                wraps += 1
        if wraps:
            findings.append(Finding("warning", path, f"{wraps} mid-paragraph line break(s)"))


def check_pages(findings: list[Finding]) -> None:
    if not PAGES.is_dir():
        return
    for page in sorted(PAGES.glob("*.md")):
        text = page.read_text(encoding="utf-8", errors="replace")
        slug = page.stem
        for kind, filename in (
            ("Application", "application.md"),
            ("Related emails", "emails.md"),
            ("Job advertisement", "job-ad.md"),
        ):
            if f"](/assets/failures/{slug}/{filename})" in text and not (CARDS / slug / filename).exists():
                findings.append(Finding("blocker", page, f"links to missing {filename}"))
            if kind == "Job advertisement" and (CARDS / slug / filename).exists():
                body = (CARDS / slug / filename).read_text(encoding="utf-8", errors="replace")[:200]
                if "No job ad" in body and f"](/assets/failures/{slug}/{filename})" in text:
                    findings.append(Finding("warning", page, "links to a placeholder job ad"))


def check_publication(findings: list[Finding]) -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8", errors="replace")
    ignored = {line.strip() for line in gitignore.splitlines()}
    if "assets/failures/" in ignored or "_failures/" in ignored or "_pages/failures.md" in ignored:
        findings.append(
            Finding(
                "warning",
                ROOT / ".gitignore",
                "cards are gitignored, so this repo will not publish them",
            )
        )
    if INDEX.exists() and re.search(r"not published|local working", INDEX.read_text(encoding="utf-8"), re.I):
        findings.append(Finding("warning", INDEX, "index still describes the catalogue as unpublished"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="fail on warnings as well as blockers")
    args = parser.parse_args()

    findings: list[Finding] = []
    files = card_files()
    if not files:
        print("No catalogue cards found under assets/failures/.")
        return 1
    for path in files:
        check_file(path, findings)
    check_pages(findings)
    check_publication(findings)

    blockers = [f for f in findings if f.severity == "blocker"]
    warnings = [f for f in findings if f.severity == "warning"]
    for item in blockers + warnings:
        print(item)
    print(
        f"\n{len(files)} cards checked. {len(blockers)} blocker(s), {len(warnings)} warning(s)."
    )
    if blockers or (args.strict and warnings):
        print("Not ready to publish.")
        return 1
    print("No publication blockers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
