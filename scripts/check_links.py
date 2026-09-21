#!/usr/bin/env python3
"""Check links in the codebase (and optionally a built `_site`).

Adapted from Folk Directory's `scripts/check_listing_www.py` (HEAD/GET classify
pattern) for this Jekyll site.

Default (source) mode scans markdown/HTML/YAML for links and verifies:
  - `file://` targets → error (common paste leftovers)
  - site-absolute `/assets/...` and relative file paths → must exist on disk
  - other site paths (`/blog/...`, `/projects/...`) → warning unless `--site` is set
  - `http(s)://` → skipped unless `--external`

Site mode (`--site _site`) mirrors CI's offline lychee pass: walk built HTML and
resolve local `href`/`src` against the site tree.

Usage:
  python3 scripts/check_links.py
  python3 scripts/check_links.py --site _site
  python3 scripts/check_links.py --external --limit 50
  python3 scripts/check_links.py --out /tmp/link-report.csv
"""

from __future__ import annotations

import argparse
import csv
import re
import socket
import sys
import time
from collections import Counter
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
LYCHEEIGNORE = ROOT / ".lycheeignore"
HEADERS = {
    "User-Agent": "glen-w.github.io/1.0 (local link check; https://glenwright.earth)"
}
TIMEOUT = 12

# Site content only — skip upstream al-folio template docs at repo root
# (CUSTOMIZE.md / FAQ.md / INSTALL.md link to optional paths that may not exist).
SOURCE_GLOBS = (
    "_pages/**/*.md",
    "_posts/**/*.md",
    "_projects/**/*.md",
    "_services/**/*.md",
    "_creative/**/*.md",
    "_books/**/*.md",
    "_news/**/*.md",
    "_includes/**/*.{html,liquid,md}",
    "_layouts/**/*.{html,liquid}",
    "_data/**/*.{yml,yaml}",
    "docs/dev/**/*.md",
)

BARE_HOST_RE = re.compile(
    r"^(?:www\.)?[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+(?:/.*)?$"
)

SKIP_DIR_PARTS = {
    ".git",
    "node_modules",
    "_site",
    ".jekyll-cache",
    ".bundle",
    "vendor",
    "lighthouse_results",
    "sandbox",
    "backups",
}

MD_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
MD_AUTOLINK_RE = re.compile(r"<(https?://[^>\s]+)>")
HREF_SRC_RE = re.compile(
    r"""(?:href|src)\s*=\s*(?P<q>['"])(?P<url>.*?)(?P=q)""",
    re.IGNORECASE,
)
BARE_URL_IN_FM_RE = re.compile(
    r"""(?m)^(?:\s*(?:url|href|link|website|repo|github|doi|pdf|slides|code)\s*:\s*)['"]?(https?://[^\s'"]+)"""
)


@dataclass
class Finding:
    source: str
    url: str
    status: str
    detail: str


class _HrefSrcCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k.lower(): v for k, v in attrs if v is not None}
        for key in ("href", "src", "poster", "data-src"):
            if key in attr_map:
                self.urls.append(attr_map[key])


def load_excludes() -> list[re.Pattern[str]]:
    patterns: list[re.Pattern[str]] = []
    if not LYCHEEIGNORE.is_file():
        return patterns
    for line in LYCHEEIGNORE.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            patterns.append(re.compile(line))
        except re.error:
            patterns.append(re.compile(re.escape(line)))
    return patterns


def is_excluded(url: str, excludes: list[re.Pattern[str]]) -> bool:
    return any(p.search(url) for p in excludes)


def iter_source_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in SOURCE_GLOBS:
        for path in ROOT.glob(pattern):
            if not path.is_file():
                continue
            if any(part in SKIP_DIR_PARTS for part in path.parts):
                continue
            files.add(path)
    return sorted(files)


def extract_urls_from_text(text: str) -> list[str]:
    found: list[str] = []
    found.extend(MD_LINK_RE.findall(text))
    found.extend(MD_AUTOLINK_RE.findall(text))
    found.extend(m.group("url") for m in HREF_SRC_RE.finditer(text))
    found.extend(BARE_URL_IN_FM_RE.findall(text))
    # de-dupe, keep order
    seen: set[str] = set()
    out: list[str] = []
    for url in found:
        url = url.strip()
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(url)
    return out


def extract_urls_from_html(text: str) -> list[str]:
    parser = _HrefSrcCollector()
    try:
        parser.feed(text)
    except Exception:
        return extract_urls_from_text(text)
    seen: set[str] = set()
    out: list[str] = []
    for url in parser.urls:
        url = (url or "").strip()
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(url)
    return out


def normalize_external(raw: str) -> str:
    raw = (raw or "").strip().strip("'\"")
    if not raw:
        return ""
    if raw.startswith("//"):
        return f"https:{raw}"
    if raw.startswith(("http://", "https://")):
        return raw
    return f"https://{raw}"


def classify_external(url: str) -> tuple[str, str]:
    """Return (status, detail). Same idea as Folk Directory's check_listing_www."""
    if requests is None:
        return "skipped", "requests not installed"
    try:
        host = urlparse(url).hostname or ""
        if host:
            socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        return "dns", str(exc)
    except OSError as exc:
        return "dns", str(exc)

    last_err = ""
    for method in ("head", "get"):
        try:
            fn = requests.head if method == "head" else requests.get
            res = fn(
                url,
                headers=HEADERS,
                timeout=TIMEOUT,
                allow_redirects=True,
                stream=method == "get",
            )
            if method == "get":
                res.close()
            code = res.status_code
            if code >= 500:
                return "http_5xx", str(code)
            if code == 404:
                return "http_404", str(code)
            if code == 429:
                return "rate_limited", str(code)
            if code >= 400:
                return "http_4xx", str(code)
            return "ok", str(code)
        except requests.exceptions.SSLError as exc:
            return "tls", str(exc)[:200]
        except requests.exceptions.Timeout as exc:
            last_err = f"timeout:{exc}"
            continue
        except requests.exceptions.RequestException as exc:
            last_err = str(exc)[:200]
            continue
    if "timeout" in last_err:
        return "timeout", last_err
    return "fail", last_err or "unknown"


def strip_url_noise(url: str) -> str:
    url = url.strip()
    if url.startswith("<") and ">" in url:
        url = url[1 : url.index(">")].strip()
    return url


def looks_like_bare_host(url: str) -> bool:
    """www.example.com/path without a scheme — treat as external, not a relative path."""
    if url.startswith(("/", "#", ".", "mailto:", "tel:", "file:")):
        return False
    if "://" in url or url.startswith("//"):
        return False
    return bool(BARE_HOST_RE.match(url.split("#", 1)[0].split("?", 1)[0]))


def rel_to_root(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def local_candidates(url: str, source: Path, site_root: Path | None) -> list[Path]:
    """Map a local/site URL to candidate filesystem paths."""
    path_only = url.split("#", 1)[0].split("?", 1)[0]
    path = unquote(path_only)
    if not path:
        return []

    candidates: list[Path] = []

    if site_root is not None:
        if path.startswith("/"):
            resolved = (site_root / path.lstrip("/")).resolve()
        else:
            resolved = (source.parent / path).resolve()
        candidates.append(resolved)
        candidates.append(Path(str(resolved) + ".html"))
        if resolved.suffix == "":
            candidates.append(resolved / "index.html")
        # CI remap: '_site(/?.*)/assets/(.*) _site/assets/$2'
        resolved_s = str(resolved)
        if "/assets/" in resolved_s:
            asset_tail = resolved_s.split("/assets/", 1)[-1]
            candidates.append((site_root / "assets" / asset_tail).resolve())
        return candidates

    if path.startswith("/"):
        rel = path.lstrip("/")
        candidates.append(ROOT / rel)
        candidates.append(ROOT / rel / "index.html")
        stem = Path(rel).name
        parent = Path(rel).parent.as_posix()
        for collection, folder in (
            ("projects", "_projects"),
            ("services", "_services"),
            ("news", "_news"),
            ("books", "_books"),
        ):
            if parent == collection or rel.startswith(f"{collection}/"):
                candidates.append(ROOT / folder / f"{stem}.md")
                candidates.append(ROOT / folder / stem / "index.md")
        return candidates

    base = source.parent
    candidates.append((base / path).resolve())
    if "assets/" in path:
        cleaned = path
        while cleaned.startswith("../"):
            cleaned = cleaned[3:]
        if cleaned.startswith("assets/"):
            candidates.append(ROOT / cleaned)
    return candidates


def check_local(url: str, source: Path, site_root: Path | None) -> tuple[str, str]:
    raw = strip_url_noise(url)
    if raw.startswith("<"):
        raw = raw[1:].strip()

    if raw.startswith("//"):
        return "external", "use --external to probe"

    if looks_like_bare_host(raw):
        return "external", "use --external to probe"

    parsed = urlparse(raw)

    if parsed.scheme == "file" or raw.startswith("file:"):
        return "file_uri", "file:// links are not portable"

    if parsed.scheme in {"mailto", "tel", "javascript", "data"}:
        return "skipped", parsed.scheme

    if not parsed.scheme and raw.startswith("#"):
        return "skipped", "fragment"

    if parsed.scheme in {"http", "https"}:
        return "external", "use --external to probe"

    if "{{" in raw or "{%" in raw:
        return "skipped", "liquid"

    candidates = local_candidates(raw, source, site_root)
    if not candidates:
        return "skipped", "empty path"

    for cand in candidates:
        try:
            if cand.is_file():
                return "ok", rel_to_root(cand)
            if cand.is_dir():
                if (cand / "index.html").is_file():
                    return "ok", rel_to_root(cand / "index.html")
                return "ok", rel_to_root(cand)
        except OSError:
            continue

    if site_root is None and raw.startswith("/") and not raw.startswith("/assets/"):
        return "needs_build", "site path; re-run with --site _site after build"

    return "missing", f"not found ({rel_to_root(candidates[0]) if candidates else raw})"

def check_one(
    url: str,
    source: Path,
    *,
    site_root: Path | None,
    external: bool,
    excludes: list[re.Pattern[str]],
    sleep: float,
) -> Finding | None:
    url = url.strip()
    if not url or is_excluded(url, excludes):
        return None

    status, detail = check_local(url, source, site_root)
    if status == "external":
        if not external:
            return None
        normalized = normalize_external(url)
        if not normalized:
            return Finding(str(source.relative_to(ROOT)), url, "invalid", "unusable url")
        status, detail = classify_external(normalized)
        time.sleep(max(0.0, sleep))
        return Finding(str(source.relative_to(ROOT)), normalized, status, detail)

    if status == "skipped":
        return None

    return Finding(str(source.relative_to(ROOT)), url, status, detail)


def scan_source(args: argparse.Namespace, excludes: list[re.Pattern[str]]) -> list[Finding]:
    findings: list[Finding] = []
    checked = 0
    for path in iter_source_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for url in extract_urls_from_text(text):
            finding = check_one(
                url,
                path,
                site_root=None,
                external=args.external,
                excludes=excludes,
                sleep=args.sleep,
            )
            if finding is None:
                continue
            findings.append(finding)
            if finding.status not in {"ok", "needs_build"}:
                checked += 1
            if args.limit and checked >= args.limit:
                return findings
    return findings


def scan_site(site_root: Path, args: argparse.Namespace, excludes: list[re.Pattern[str]]) -> list[Finding]:
    findings: list[Finding] = []
    checked = 0
    for path in sorted(site_root.rglob("*.html")):
        if any(part in SKIP_DIR_PARTS for part in path.parts if part != "_site"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for url in extract_urls_from_html(text):
            finding = check_one(
                url,
                path,
                site_root=site_root,
                external=args.external,
                excludes=excludes,
                sleep=args.sleep,
            )
            if finding is None:
                continue
            findings.append(finding)
            if finding.status not in {"ok"}:
                checked += 1
            if args.limit and checked >= args.limit:
                return findings
    return findings


ERROR_STATUSES = {
    "missing",
    "file_uri",
    "dns",
    "http_404",
    "http_4xx",
    "http_5xx",
    "tls",
    "timeout",
    "fail",
    "invalid",
    "rate_limited",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--site",
        type=Path,
        default=None,
        help="Built site root (e.g. _site). Offline local check, closest to CI lychee.",
    )
    ap.add_argument(
        "--external",
        action="store_true",
        help="Also HEAD/GET http(s) links (network; slower).",
    )
    ap.add_argument("--limit", type=int, default=0, help="Stop after N non-ok findings")
    ap.add_argument("--sleep", type=float, default=0.15, help="Pause between external requests")
    ap.add_argument("--out", type=Path, default=None, help="Optional CSV report path")
    args = ap.parse_args()

    excludes = load_excludes()
    site_root = args.site.resolve() if args.site else None
    if site_root is not None and not site_root.is_dir():
        print(f"error: --site {site_root} is not a directory", file=sys.stderr)
        return 2

    if site_root is not None:
        findings = scan_site(site_root, args, excludes)
        mode = f"site:{site_root.relative_to(ROOT) if site_root.is_relative_to(ROOT) else site_root}"
    else:
        findings = scan_source(args, excludes)
        mode = "source"

    counts = Counter(f.status for f in findings)
    errors = [f for f in findings if f.status in ERROR_STATUSES]
    warnings = [f for f in findings if f.status == "needs_build"]

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=["source", "url", "status", "detail"])
            writer.writeheader()
            writer.writerows(
                {"source": f.source, "url": f.url, "status": f.status, "detail": f.detail}
                for f in findings
            )

    print(f"Link check ({mode}): {len(findings)} findings")
    for key in sorted(counts):
        print(f"  {key}: {counts[key]}")

    if warnings and not site_root:
        print(
            f"\n{len(warnings)} site permalink(s) need a build to verify "
            "(run: bundle exec jekyll build && python3 scripts/check_links.py --site _site)"
        )

    if errors:
        print(f"\n{len(errors)} error(s):")
        for f in errors[:40]:
            print(f"  [{f.status}] {f.source}: {f.url} — {f.detail}")
        if len(errors) > 40:
            print(f"  … {len(errors) - 40} more")
        if args.out:
            print(f"\nReport: {args.out}")
        return 1

    if args.out:
        print(f"Report: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
