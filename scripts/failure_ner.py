"""Person-name scan for the catalogue of failures.

Same approach as TranscriptX NER: spaCy PERSON spans
(transcriptx.core.analysis.ner.extract_named_entities). TranscriptX defaults
to en_core_web_md. This gate uses en_core_web_lg because the medium model
misses short referee lines such as "Kristina Gjerde".
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "assets" / "failures"
PAGES = ROOT / "_failures"
DEFAULT_MODEL = "en_core_web_lg"
CARD_NAMES = ("application.md", "job-ad.md")

KEEP_NAMES = {
    "glen",
    "glen wright",
    "glen w wright",
    "glen w. wright",
    "glen william",
    "glen william wright",
    "g wright",
    "g. wright",
    "wright",
    "william",
}

STOP_TOKENS = {
    "sir",
    "madam",
    "sincerely",
    "faithfully",
    "regards",
    "dear",
    "applicant",
    "candidate",
    "referee",
    "professor",
    "dr",
    "mr",
    "mrs",
    "ms",
    "miss",
    "cf",
    "curriculum",
    "vitae",
    "resume",
    "cv",
    "annex",
    "appendix",
    "page",
    "figure",
    "table",
    "committee",
    "panel",
    "board",
    "secretariat",
    "commission",
    "university",
    "institute",
    "department",
    "ministry",
    "office",
    "team",
    "programme",
    "program",
    "section",
    "division",
    "unit",
}

# A token from this set means the span is a place, statute, or form label.
NOT_A_PERSON = STOP_TOKENS | {
    "po",
    "law",
    "energy",
    "observer",
    "page",
    "house",
    "coordinator",
    "degree",
    "rue",
    "street",
    "road",
    "avenue",
    "lane",
    "australia",
    "sciences",
    "geoscience",
    "radio",
    "scientific",
    "education",
    "level",
    "bachelor",
    "maori",
    "komiti",
    "firth",
    "waatea",
    "ecomafia",
    "rapporto",
    "snow",
    "ivory",
    "takutai",
    "moana",
    "haye",
    "lenton",
    "nottingham",
    "never",
    "employed",
    "current",
}

ROLE_TOKENS = {
    "commissioner",
    "executive",
    "secretary",
    "lecturer",
    "director",
    "senior",
    "advisor",
    "adviser",
    "chair",
    "manager",
    "professor",
    "doctor",
    "dr",
}

TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ'’\-]*")
PERSON_SHAPE = re.compile(
    r"^[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ'’\-]+(?:\s+[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ'’\-]+){1,2}$"
)
FRONT_MATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.S)
LINK_TARGET_RE = re.compile(r"\]\([^)]+\)")
LINE_NAME_RE = re.compile(
    r"^(?:[-•*]\s+|\d+\.\s+)?([A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ'’\-]+(?:\s+[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ'’\-]+){1,2})\s*$"
)
COO_RE = re.compile(
    r"\bc/o\s+([A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ'’\-]+(?:\s+[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ'’\-]+){1,2})"
)
FULL_NAME_RE = re.compile(r"^full name:\s*$", re.I)
SINGLE_NAME_RE = re.compile(r"^[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ'’\-]{2,}$")


@dataclass(frozen=True)
class PersonHit:
    path: Path
    start: int
    end: int
    surface: str
    line: int


def sharpie(text: str) -> str:
    """Block bar roughly as wide as the hidden words. Same scale as _redact.sharpie."""
    n = len(re.sub(r"\s+", " ", (text or "").strip()))
    blocks = max(4, min(14, (n + 1) // 2))
    return "█" * blocks


def card_paths() -> list[Path]:
    paths: list[Path] = []
    if CARDS.is_dir():
        paths.extend(
            p
            for p in sorted(CARDS.glob("*/*"))
            if p.name in CARD_NAMES and p.is_file()
        )
    if PAGES.is_dir():
        paths.extend(sorted(PAGES.glob("*.md")))
    return paths


def normalise(name: str) -> str:
    text = re.sub(r"\s+", " ", name).strip().strip("\"'`")
    text = text.replace(".", "")
    return re.sub(r"\s+", " ", text).casefold()


def _mask(match: re.Match[str]) -> str:
    return "".join("\n" if char == "\n" else " " for char in match.group(0))


def prepare(text: str) -> str:
    """Blank front matter and link targets without moving offsets."""
    text = FRONT_MATTER_RE.sub(_mask, text, count=1)
    return LINK_TARGET_RE.sub(_mask, text)


def keep_person(surface: str) -> bool:
    text = " ".join(surface.split())
    if not text or "█" in text or "_" in text or "/" in text:
        return False
    key = normalise(text)
    if not key or key in KEEP_NAMES or key.startswith("glen wright") or key.startswith("glen william"):
        return False
    if not PERSON_SHAPE.match(text):
        return False
    tokens = TOKEN_RE.findall(text)
    if any(token.casefold() in NOT_A_PERSON for token in tokens):
        return False
    return True


def person_surface(raw: str) -> str | None:
    tokens = " ".join(raw.split()).split()
    while len(tokens) > 2 and tokens[-1].casefold().rstrip(".") in ROLE_TOKENS:
        tokens.pop()
    text = " ".join(tokens)
    if keep_person(text):
        return text
    return None


def line_no(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _load_nlp(model_name: str):
    import spacy

    return spacy.load(model_name, disable=["parser", "lemmatizer", "textcat"])


def iter_person_hits(model_name: str = DEFAULT_MODEL) -> list[PersonHit]:
    paths = card_paths()
    if not paths:
        return []
    nlp = _load_nlp(model_name)
    originals = [path.read_text(encoding="utf-8", errors="replace") for path in paths]
    masked = [prepare(text) for text in originals]
    hits: list[PersonHit] = []
    seen: set[tuple[str, int, int]] = set()

    def add(path: Path, start: int, end: int, surface: str, text: str) -> None:
        key = (str(path), start, end)
        if key in seen or start < 0 or end > len(text) or start >= end:
            return
        if "█" in text[start:end]:
            return
        seen.add(key)
        hits.append(PersonHit(path, start, end, surface, line_no(text, start)))

    for path, original, text, doc in zip(paths, originals, masked, nlp.pipe(masked, batch_size=8)):
        for ent in doc.ents:
            if ent.label_ != "PERSON":
                continue
            surface = person_surface(ent.text)
            if not surface:
                continue
            if surface in ent.text:
                offset = ent.text.find(surface)
                add(path, ent.start_char + offset, ent.start_char + offset + len(surface), surface, original)
            else:
                add(path, ent.start_char, ent.end_char, surface, original)
        for match in LINE_NAME_RE.finditer(original):
            surface = person_surface(match.group(1))
            if not surface:
                continue
            add(path, match.start(1), match.end(1), surface, original)
        for match in COO_RE.finditer(original):
            surface = person_surface(match.group(1))
            if not surface:
                continue
            add(path, match.start(1), match.end(1), surface, original)
        for start, end, surface in _full_name_fields(original):
            add(path, start, end, surface, original)
    return hits


def _full_name_fields(text: str) -> list[tuple[int, int, str]]:
    """Names written on their own lines under a 'Full name:' label."""
    spans: list[tuple[int, int, str]] = []
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        if FULL_NAME_RE.match(lines[i].strip()):
            j = i + 1
            while j < len(lines):
                stripped = lines[j].strip()
                if not stripped:
                    j += 1
                    continue
                if (
                    SINGLE_NAME_RE.match(stripped)
                    and stripped.casefold() not in KEEP_NAMES
                    and stripped.casefold() not in NOT_A_PERSON
                ):
                    spans.append((stripped, j))
                    j += 1
                    continue
                break
            i = j
            continue
        i += 1
    # Resolve line indexes to character offsets.
    resolved: list[tuple[int, int, str]] = []
    line_starts = [0]
    for line in lines[:-1]:
        line_starts.append(line_starts[-1] + len(line))
    for surface, index in spans:
        local = lines[index].find(surface)
        start = line_starts[index] + local
        resolved.append((start, start + len(surface), surface))
    return resolved


def censor_hits(hits: list[PersonHit]) -> int:
    """Replace each hit in place with an ASCII block bar. Returns files changed."""
    by_path: dict[Path, list[PersonHit]] = {}
    for hit in hits:
        by_path.setdefault(hit.path, []).append(hit)
    changed = 0
    for path, group in by_path.items():
        text = path.read_text(encoding="utf-8", errors="replace")
        chosen: list[PersonHit] = []
        for hit in sorted(group, key=lambda item: (item.start, -(item.end - item.start))):
            if hit.start < 0 or hit.end > len(text):
                continue
            if chosen and hit.start < chosen[-1].end:
                continue
            chosen.append(hit)
        pieces: list[str] = []
        cursor = 0
        for hit in chosen:
            pieces.append(text[cursor : hit.start])
            pieces.append(sharpie(hit.surface))
            cursor = hit.end
        pieces.append(text[cursor:])
        new = "".join(pieces)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1
    return changed
