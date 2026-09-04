"""Build compact library catalog JSON from parsed BibTeX entries."""

from __future__ import annotations

import html
import json
import os
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

import yaml

from processing.core.tag_extractor import TagExtractor
from processing.library.bib_parser import BibParser
from processing.library.content_generator import ContentGenerator

MAX_AUTHOR_LIMIT = 3
SELF_LAST = "Wright"
SELF_FIRST_PREFIXES = ("Glen", "G.")
THUMB_WIDTH = 480
PREVIEW_PREFIX = "/assets/img/publication_preview/"
PDF_PREFIX = "/assets/pdf/"
PHOTO_PREFIX = "/assets/img/publications/"


class CatalogParityError(Exception):
    """Raised when generated catalog counts drift from expected sources."""


class CatalogGenerator:
    """Generate list + details JSON (and a noscript selected YAML) from bib entries."""

    @staticmethod
    def jekyll_page_slug(filename_stem: str) -> str:
        """Match Jekyll collection permalink ``/library/:name/`` from a markdown basename."""
        return filename_stem.replace("_", "-")

    def __init__(self, project_root: str, library_dir: Optional[str] = None):
        self.project_root = project_root
        self.library_dir = library_dir or os.path.join(project_root, "_library")
        self.bib_parser = BibParser()
        self.content_generator = ContentGenerator()
        self.tag_extractor = TagExtractor()
        self._library_index: Optional[Dict[str, Dict[str, Any]]] = None

    def generate(
        self,
        entries: List[Dict[str, Any]],
        *,
        check_parity: bool = True,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Return (catalog, details) dicts and write artifacts to disk."""
        items: List[Dict[str, Any]] = []
        details: Dict[str, Any] = {}
        for entry in entries:
            item, detail = self.build_item(entry)
            if item is None:
                continue
            items.append(item)
            if detail:
                details[item["id"]] = detail

        items.sort(key=self._sort_key)
        catalog = {"v": 1, "items": items}

        if check_parity:
            self.assert_parity(catalog, entries)

        self._write_artifacts(catalog, details)
        return catalog, details

    def build_item(
        self, entry: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
        entry_id = str(entry.get("ID") or "").strip()
        if not entry_id:
            return None, {}

        title = self.bib_parser.clean_title(entry.get("title", "Untitled"))
        year = self._year_int(entry)
        month = self._month_int(entry)
        entry_type = self.tag_extractor.extract_type(entry) or "Other"
        roles = self.tag_extractor.extract_roles(entry)
        langs = self.tag_extractor.extract_languages(entry)
        authors = self.bib_parser.format_authors(entry)
        authors_short = self.format_authors_short(authors)
        venue = self._venue(entry)
        links = self.bib_parser.extract_links(entry)
        selected = self._is_selected(entry)

        thumb = self._thumb_url(entry)
        pdf = self._asset_url(links.get("pdf"), PDF_PREFIX)
        url = self._http_url(links.get("url"))
        doi = self._doi_url(links.get("doi") or entry.get("doi"))
        video = self._http_url(links.get("video")) or self._first_http(
            self._annote_lines(entry, "[video]")
        )
        slides = self._asset_url(links.get("slides"), PDF_PREFIX)
        agenda = self._asset_url(links.get("agenda"), PDF_PREFIX)

        abstract = self._abstract(entry)
        photos = self._image_list(entry, "photos")
        figures = self._image_list(entry, "figures")
        speakers = self._annote_lines(entry, "[speakers]")
        quotes = self._annote_lines(entry, "[quotes]")
        audio = self._annote_lines(entry, "[audio]")
        extra_links = self._annote_lines(entry, "[links]") or self._annote_lines(
            entry, "[link]"
        )
        award = self._strip(entry.get("award") or entry.get("award_name"))

        flags: List[str] = []
        if abstract:
            flags.append("abs")
        if photos:
            flags.append("photos")
        if figures:
            flags.append("figures")
        if video:
            flags.append("video")
        if speakers:
            flags.append("speakers")
        if quotes:
            flags.append("quotes")
        if audio:
            flags.append("audio")
        if award:
            flags.append("award")

        item: Dict[str, Any] = {
            "id": entry_id,
            "title": title,
            "year": year,
            "type": entry_type,
        }
        if month:
            item["month"] = month
        if roles:
            item["roles"] = roles
        if langs:
            item["langs"] = langs
        if authors_short:
            item["authors"] = authors_short["text"]
            item["authorsHtml"] = authors_short["html"]
        if venue:
            item["venue"] = venue
        if thumb:
            item["thumb"] = thumb
        if pdf:
            item["pdf"] = pdf
        if url:
            item["url"] = url
        if doi:
            item["doi"] = doi
        if video:
            item["video"] = video
        if slides:
            item["slides"] = slides
        if agenda:
            item["agenda"] = agenda
        if extra_links:
            item["links"] = extra_links
        if selected:
            item["selected"] = True
        if flags:
            item["flags"] = flags

        info = self._info_url(entry_id)
        if info:
            item["info"] = info

        detail: Dict[str, Any] = {}
        if abstract:
            detail["abstract"] = abstract
        if photos:
            detail["photos"] = photos
        if figures:
            detail["figures"] = figures
        if speakers:
            detail["speakers"] = speakers
        if quotes:
            detail["quotes"] = quotes
        if audio:
            detail["audio"] = audio
        if award:
            detail["award"] = award
        if len(authors) > MAX_AUTHOR_LIMIT:
            detail["authors"] = self.format_authors_short(authors, limit=len(authors))[
                "html"
            ]

        return item, detail

    @staticmethod
    def format_authors_short(
        authors: List[Dict[str, str]], limit: int = MAX_AUTHOR_LIMIT
    ) -> Optional[Dict[str, str]]:
        """Up to `limit` names; then 'et al.' Solo authors are omitted (matches bib.liquid)."""
        names = []
        for author in authors:
            first = (author.get("first") or "").strip()
            last = (author.get("last") or "").strip()
            full = f"{first} {last}".strip() or (author.get("full") or "").strip()
            if full:
                names.append({"first": first, "last": last, "full": full})
        if len(names) <= 1:
            return None

        shown = names[:limit]
        truncated = len(names) > limit

        def is_self(person: Dict[str, str]) -> bool:
            last = re.sub(r"[*∗†‡§¶‖&^]", "", person["last"])
            if last != SELF_LAST:
                return False
            first = person["first"]
            return any(
                first == prefix or first.startswith(prefix + " ")
                for prefix in SELF_FIRST_PREFIXES
            )

        def html_name(person: Dict[str, str]) -> str:
            escaped = html.escape(person["full"])
            if is_self(person):
                return f"<em>{escaped}</em>"
            return escaped

        labels = [p["full"] for p in shown]
        html_parts = [html_name(p) for p in shown]

        if truncated:
            text = ", ".join(labels) + " et al."
            markup = ", ".join(html_parts) + " et al."
        elif len(labels) == 2:
            text = f"{labels[0]} and {labels[1]}"
            markup = f"{html_parts[0]} and {html_parts[1]}"
        else:
            text = ", ".join(labels[:-1]) + ", and " + labels[-1]
            markup = ", ".join(html_parts[:-1]) + ", and " + html_parts[-1]
        return {"text": text, "html": markup}

    def assert_parity(
        self, catalog: Dict[str, Any], entries: List[Dict[str, Any]]
    ) -> None:
        items = catalog.get("items") or []
        errors: List[str] = []

        expected_ids = [str(e.get("ID") or "").strip() for e in entries if e.get("ID")]
        got_ids = [item["id"] for item in items]
        if len(got_ids) != len(expected_ids):
            errors.append(
                f"catalog item count {len(got_ids)} != bib entry count {len(expected_ids)}"
            )
        missing = sorted(set(expected_ids) - set(got_ids))
        extra = sorted(set(got_ids) - set(expected_ids))
        if missing:
            errors.append(f"catalog missing ids: {missing[:8]}")
        if extra:
            errors.append(f"catalog extra ids: {extra[:8]}")

        type_counts = Counter(item.get("type") for item in items if item.get("type"))
        role_counts: Counter = Counter()
        lang_counts: Counter = Counter()
        for item in items:
            for role in item.get("roles") or []:
                role_counts[role] += 1
            for lang in item.get("langs") or []:
                lang_counts[lang] += 1

        expected_types: Counter = Counter()
        expected_roles: Counter = Counter()
        expected_langs: Counter = Counter()
        for entry in entries:
            entry_type = self.tag_extractor.extract_type(entry)
            if entry_type:
                expected_types[entry_type] += 1
            for role in self.tag_extractor.extract_roles(entry):
                expected_roles[role] += 1
            for lang in self.tag_extractor.extract_languages(entry):
                expected_langs[lang] += 1

        if type_counts != expected_types:
            errors.append(f"type counts drifted: {dict(type_counts)} vs {dict(expected_types)}")
        if role_counts != expected_roles:
            errors.append(f"role counts drifted: {dict(role_counts)} vs {dict(expected_roles)}")
        if lang_counts != expected_langs:
            errors.append(f"lang counts drifted: {dict(lang_counts)} vs {dict(expected_langs)}")

        filters_path = os.path.join(self.project_root, "_data", "dynamic_filters.yml")
        if os.path.isfile(filters_path):
            with open(filters_path, encoding="utf-8") as handle:
                filters = yaml.safe_load(handle) or {}
            filter_types = filters.get("entry_type_counts") or {}
            if filter_types and dict(type_counts) != dict(filter_types):
                errors.append(
                    "entry_type_counts in dynamic_filters.yml do not match catalog "
                    f"({dict(type_counts)} vs {dict(filter_types)})"
                )
            filter_roles = filters.get("role_tag_counts") or {}
            if filter_roles and dict(role_counts) != dict(filter_roles):
                errors.append(
                    "role_tag_counts in dynamic_filters.yml do not match catalog "
                    f"({dict(role_counts)} vs {dict(filter_roles)})"
                )
            filter_langs = filters.get("language_tag_counts") or {}
            if filter_langs and dict(lang_counts) != dict(filter_langs):
                errors.append(
                    "language_tag_counts in dynamic_filters.yml do not match catalog "
                    f"({dict(lang_counts)} vs {dict(filter_langs)})"
                )

        library_index = self._get_library_index()
        if library_index:
            pdf_mismatches = []
            for item in items:
                page = library_index.get(item["id"])
                if not page:
                    continue
                catalog_pdf = os.path.basename(item.get("pdf") or "")
                page_pdf = os.path.basename(str(page.get("pdf") or ""))
                if catalog_pdf and page_pdf and catalog_pdf != page_pdf:
                    pdf_mismatches.append(f"{item['id']} catalog={catalog_pdf} library={page_pdf}")
            if pdf_mismatches:
                print(
                    "  ⚠️  Library page PDF differs from bib (catalog uses bib): "
                    + "; ".join(pdf_mismatches[:8])
                )

        if errors:
            raise CatalogParityError("; ".join(errors))

    def _write_artifacts(self, catalog: Dict[str, Any], details: Dict[str, Any]) -> None:
        json_dir = os.path.join(self.project_root, "assets", "json")
        os.makedirs(json_dir, exist_ok=True)
        catalog_path = os.path.join(json_dir, "library.json")
        details_path = os.path.join(json_dir, "library-details.json")
        with open(catalog_path, "w", encoding="utf-8") as handle:
            json.dump(catalog, handle, ensure_ascii=False, indent=2, sort_keys=False)
            handle.write("\n")
        with open(details_path, "w", encoding="utf-8") as handle:
            json.dump(details, handle, ensure_ascii=False, indent=2, sort_keys=False)
            handle.write("\n")

        selected = []
        for item in catalog["items"]:
            if not item.get("selected"):
                continue
            row = {
                "id": item["id"],
                "title": item["title"],
                "year": item["year"],
            }
            if item.get("pdf"):
                row["pdf"] = item["pdf"]
            if item.get("url"):
                row["url"] = item["url"]
            elif item.get("doi"):
                row["url"] = item["doi"]
            elif item.get("info"):
                row["url"] = item["info"]
            selected.append(row)

        data_dir = os.path.join(self.project_root, "_data")
        os.makedirs(data_dir, exist_ok=True)
        selected_path = os.path.join(data_dir, "library_selected.yml")
        with open(selected_path, "w", encoding="utf-8") as handle:
            yaml.dump(selected, handle, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(
            f"Wrote library catalog: {len(catalog['items'])} items, "
            f"{len(details)} details, {len(selected)} selected"
        )
        print(f"  {catalog_path}")
        print(f"  {details_path}")
        print(f"  {selected_path}")

    def _get_library_index(self) -> Dict[str, Dict[str, Any]]:
        if self._library_index is not None:
            return self._library_index
        index: Dict[str, Dict[str, Any]] = {}
        if not os.path.isdir(self.library_dir):
            self._library_index = index
            return index
        for name in os.listdir(self.library_dir):
            if not name.endswith(".md"):
                continue
            path = os.path.join(self.library_dir, name)
            try:
                with open(path, encoding="utf-8") as handle:
                    text = handle.read()
            except OSError:
                continue
            if not text.startswith("---"):
                continue
            parts = text.split("---", 2)
            if len(parts) < 3:
                continue
            try:
                data = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                continue
            key = self._strip(data.get("bibtex_key"))
            if not key:
                continue
            permalink = self._strip(data.get("permalink"))
            if permalink:
                info = permalink if permalink.endswith("/") else f"{permalink}/"
                slug = info.removeprefix("/library/").rstrip("/")
            else:
                slug = self.jekyll_page_slug(name[:-3])
                info = f"/library/{slug}/"
            index[key] = {
                "slug": slug,
                "info": info,
                "preview": data.get("preview"),
                "pdf": data.get("pdf"),
                "title": data.get("title"),
            }
        self._library_index = index
        return index

    def _info_url(self, entry_id: str) -> Optional[str]:
        page = self._get_library_index().get(entry_id)
        if page:
            return page["info"]
        return None

    def _is_selected(self, entry: Dict[str, Any]) -> bool:
        if self.tag_extractor.extract_selected(entry):
            return True
        value = entry.get("selected")
        if isinstance(value, bool):
            return value
        return str(value or "").strip().lower() in {"true", "1", "yes"}

    def _abstract(self, entry: Dict[str, Any]) -> str:
        abstract = self.bib_parser.get_abstract(entry)
        if abstract:
            return abstract
        lines = self._annote_lines(entry, "[abstract]")
        return "\n".join(lines) if lines else ""

    def _venue(self, entry: Dict[str, Any]) -> Optional[str]:
        for key in ("journal", "booktitle", "institution", "publisher", "school", "howpublished"):
            value = self._strip(entry.get(key))
            if value:
                return value
        return self._strip(self.bib_parser.format_venue(entry))

    def _thumb_url(self, entry: Dict[str, Any]) -> Optional[str]:
        preview = self._strip(entry.get("preview"))
        if not preview:
            return None
        if "://" in preview:
            return preview
        basename = os.path.basename(preview)
        stem, _ext = os.path.splitext(basename)
        if not stem:
            return None
        return f"{PREVIEW_PREFIX}{stem}-{THUMB_WIDTH}.webp"

    def _image_list(self, entry: Dict[str, Any], field: str) -> List[Dict[str, str]]:
        raw = self._strip(entry.get(field))
        if not raw:
            return []
        images = []
        for part in raw.split(","):
            name = os.path.basename(part.strip())
            if not name or "thumbnail" in name.lower():
                continue
            images.append({"src": f"{PHOTO_PREFIX}{name}", "alt": field[:-1].title()})
        return images

    def _annote_lines(self, entry: Dict[str, Any], marker: str) -> List[str]:
        return self.content_generator._extract_annote_lines(entry, marker)

    def _year_int(self, entry: Dict[str, Any]) -> int:
        try:
            return int(str(self.bib_parser.extract_year(entry))[:4])
        except (TypeError, ValueError):
            return 0

    def _month_int(self, entry: Dict[str, Any]) -> Optional[int]:
        raw = self.bib_parser.extract_month(entry)
        if not raw:
            return None
        month_names = {
            "jan": 1,
            "january": 1,
            "feb": 2,
            "february": 2,
            "mar": 3,
            "march": 3,
            "apr": 4,
            "april": 4,
            "may": 5,
            "jun": 6,
            "june": 6,
            "jul": 7,
            "july": 7,
            "aug": 8,
            "august": 8,
            "sep": 9,
            "sept": 9,
            "september": 9,
            "oct": 10,
            "october": 10,
            "nov": 11,
            "november": 11,
            "dec": 12,
            "december": 12,
        }
        text = re.sub(r"[^a-z0-9]", "", str(raw).lower())
        if text in month_names:
            return month_names[text]
        try:
            value = int(text)
            if 1 <= value <= 12:
                return value
        except ValueError:
            return None
        return None

    @staticmethod
    def _sort_key(item: Dict[str, Any]) -> Tuple:
        return (-int(item.get("year") or 0), -int(item.get("month") or 0), item.get("title") or "")

    @staticmethod
    def _strip(value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _http_url(value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        text = str(value).strip()
        if text.startswith("http://") or text.startswith("https://") or text.startswith("/"):
            return text
        return None

    @staticmethod
    def _first_http(lines: List[str]) -> Optional[str]:
        for line in lines:
            if "http://" in line or "https://" in line or line.startswith("www."):
                return line.strip()
        return None

    @staticmethod
    def _asset_url(value: Optional[str], prefix: str) -> Optional[str]:
        if not value:
            return None
        text = str(value).strip()
        if not text or text in {"null", "undefined", "false"}:
            return None
        if "://" in text or text.startswith("/"):
            return text
        return prefix + os.path.basename(text)

    @staticmethod
    def _doi_url(value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        text = str(value).strip()
        if not text:
            return None
        if text.startswith("http"):
            return text
        return f"https://doi.org/{text}"
