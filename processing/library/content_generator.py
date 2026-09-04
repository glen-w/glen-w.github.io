"""
Content Generator

Generates markdown content and front matter for library pages.
"""

import hashlib
import html
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import yaml

from processing.config import Configuration
from processing.core.tag_extractor import TagExtractor
from processing.core.text_processor import TextProcessor
from processing.library.bib_parser import BibParser


class ContentGenerator:
    """Generates markdown content for library pages."""

    EVENT_TYPES = frozenset({
        'conference', 'workshop', 'webinar', 'seminar', 'panel',
        'lecture', 'presentation', 'event',
    })

    EVENT_ALIASES = {
        'conference paper': 'conference',
        'guest lecture': 'lecture',
        'side event': 'event',
        'launch': 'event',
        'launch event': 'event',
        'roundtable': 'event',
        'brown bag': 'event',
        'moderated': 'panel',
        'organized': 'event',
        'organised': 'event',
        'attendance': 'event',
    }

    # Most-specific wins when duplicate URLs appear
    KIND_SPECIFICITY = {
        'agenda': 70,
        'slides': 60,
        'poster': 50,
        'pdf': 40,
        'video': 30,
        'zip': 20,
        'landing': 10,
    }

    KIND_ORDER = ('pdf', 'agenda', 'slides', 'poster', 'zip', 'video', 'landing')

    FORMAT_BY_EXT = {
        '.pdf': 'PDF',
        '.ppt': 'PPT',
        '.pptx': 'PPTX',
        '.doc': 'DOC',
        '.docx': 'DOCX',
        '.xls': 'XLS',
        '.xlsx': 'XLSX',
        '.zip': 'ZIP',
        '.rar': 'RAR',
    }

    STANDFIRST_MAX_CHARS = 280

    def __init__(self):
        """Initialize the content generator."""
        self.bib_parser = BibParser()
        self.config = Configuration()
        self.text_processor = TextProcessor(self.config)
        self.tag_extractor = TagExtractor()
        self.warnings: List[str] = []

    def generate_front_matter(self, entry: Dict[str, Any]) -> str:
        """Generate YAML front matter for the page."""
        self.warnings = []

        title = self.bib_parser.clean_title(entry.get('title', 'Untitled'))
        year = self.bib_parser.extract_year(entry)
        month = self.bib_parser.extract_month(entry)
        date_str = self._build_date_str(year, month)

        keywords = self.bib_parser.extract_keywords(entry)
        tags = [kw for kw in keywords if not kw.startswith('ignore')]
        categories = self._determine_categories(entry, keywords)

        authors = self.bib_parser.format_authors(entry)
        author_names = self._dedupe_list([
            self._strip_str(f"{author['first']} {author['last']}")
            for author in authors
            if self._strip_str(f"{author['first']} {author['last']}")
        ])

        links = self.bib_parser.extract_links(entry)
        entry_type = self._strip_str(self.bib_parser.get_entry_type_display(entry)) or 'Other'
        is_event = self._compute_is_event(entry_type)

        abstract = self._strip_str(self.bib_parser.get_abstract(entry))
        standfirst = self._build_standfirst(entry, abstract)
        description = self._build_description(entry, abstract, title, standfirst)

        venue = self._strip_str(self.bib_parser.format_venue(entry))
        location = self._strip_str(entry.get('address') or entry.get('location'))
        institution = self._strip_str(entry.get('institution'))
        publisher = self._strip_str(entry.get('publisher'))

        roles = self.tag_extractor.extract_roles(entry)
        role = roles[0] if roles else None
        speakers = self._extract_annote_lines(entry, '[speakers]')
        quotes = self._extract_annote_lines(entry, '[quotes]')

        processed_images = self._find_processed_images(entry)
        preview = self._resolve_preview(entry, processed_images)

        resources = self._build_resources(
            entry=entry,
            links=links,
            title=title,
            entry_type=entry_type,
            is_event=is_event,
            institution=institution or venue,
        )

        front_matter: Dict[str, Any] = {
            'layout': 'library-item',
            'title': title,
            'date': date_str,
            'entry_type': entry_type,
            'year': year,
            'bibtex_key': self._strip_str(entry.get('ID', '')),
            'is_event': is_event,
        }

        self._set_if(front_matter, 'description', description)
        self._set_if(front_matter, 'standfirst', standfirst)
        self._set_if(front_matter, 'abstract', abstract)
        self._set_list(front_matter, 'tags', tags)
        self._set_list(front_matter, 'categories', categories)
        self._set_list(front_matter, 'authors', author_names)
        self._set_if(front_matter, 'venue', venue)
        self._set_if(front_matter, 'location', location)
        self._set_if(front_matter, 'institution', institution)
        self._set_if(front_matter, 'publisher', publisher)
        self._set_if(front_matter, 'role', role)
        self._set_list(front_matter, 'speakers', speakers)
        self._set_list(front_matter, 'quotes', quotes)
        self._set_if(front_matter, 'preview', preview)

        if processed_images:
            gallery = [img for img in processed_images if img and 'thumbnail' not in img.lower()]
            self._set_list(front_matter, 'gallery', self._dedupe_list(gallery))

        # Legacy top-level fields for index / compatibility
        for key in ('pdf', 'agenda', 'slides', 'poster', 'video', 'url', 'doi'):
            value = self._strip_str(links.get(key))
            if value:
                front_matter[key] = value

        zip_name = self._strip_str(entry.get('zip_archive'))
        if zip_name:
            front_matter['zip_archive'] = zip_name
            zip_count = self._strip_str(entry.get('zip_file_count'))
            zip_size = self._strip_str(entry.get('zip_file_size_mb'))
            if zip_count:
                front_matter['zip_file_count'] = zip_count
            if zip_size:
                front_matter['zip_file_size_mb'] = zip_size

        for key in ('pages', 'volume', 'number'):
            self._set_if(front_matter, key, self._strip_str(entry.get(key)))

        if resources:
            front_matter['resources'] = resources

        for warning in self.warnings:
            key = self._strip_str(entry.get('ID', '')) or title
            print(f"  ⚠️  [{key}] {warning}")

        yaml_str = yaml.dump(
            front_matter,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
        return f"---\n{yaml_str}---"

    # ------------------------------------------------------------------
    # Resources
    # ------------------------------------------------------------------

    def _build_resources(
        self,
        entry: Dict[str, Any],
        links: Dict[str, str],
        title: str,
        entry_type: str,
        is_event: bool,
        institution: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Build normalized resources list with verification and deduplication."""
        candidates: List[Dict[str, Any]] = []

        pdf = self._strip_str(links.get('pdf'))
        if pdf:
            resource = self._local_file_resource(
                kind='pdf',
                filename=pdf,
                directory=self.config.PDF_DIR,
                url_prefix='/assets/pdf/',
                title=title,
                label=self._pdf_action_label(entry_type),
                primary=True,
            )
            if resource:
                candidates.append(resource)

        agenda = self._strip_str(links.get('agenda'))
        if agenda:
            resource = self._local_file_resource(
                kind='agenda',
                filename=agenda,
                directory=self.config.PDF_DIR,
                url_prefix='/assets/pdf/',
                title='Conference agenda',
                label='View conference programme',
            )
            if resource:
                candidates.append(resource)

        slides = self._strip_str(links.get('slides'))
        if slides:
            resource = self._local_file_resource(
                kind='slides',
                filename=slides,
                directory=self.config.PDF_DIR,
                url_prefix='/assets/pdf/',
                title='Presentation slides',
                label='View presentation',
            )
            if resource:
                candidates.append(resource)

        poster = self._strip_str(links.get('poster'))
        if poster:
            resource = self._local_file_resource(
                kind='poster',
                filename=poster,
                directory=self.config.PDF_DIR,
                url_prefix='/assets/pdf/',
                title='Poster',
                label='View poster',
            )
            if resource:
                candidates.append(resource)

        zip_name = self._strip_str(entry.get('zip_archive'))
        if zip_name:
            meta_bits = []
            count = self._strip_str(entry.get('zip_file_count'))
            size = self._strip_str(entry.get('zip_file_size_mb'))
            if count:
                meta_bits.append(f"{count} files")
            if size:
                meta_bits.append(f"{size} MB")
            subtitle = ' · '.join(meta_bits) if meta_bits else None
            resource = self._local_file_resource(
                kind='zip',
                filename=zip_name,
                directory=self.config.ZIP_DIR,
                url_prefix='/assets/zips/',
                title='Download all files',
                label='Download all files',
                subtitle=subtitle,
            )
            if resource:
                candidates.append(resource)

        video = self._strip_str(links.get('video') or links.get('youtube'))
        if video:
            candidates.append({
                'kind': 'video',
                'title': 'Event recording',
                'label': 'Watch recording',
                'url': video,
                'format': 'Video',
                'local': False,
                'external': True,
            })

        landing = self._strip_str(links.get('url'))
        if landing:
            candidates.append({
                'kind': 'landing',
                'title': self._landing_title(institution, is_event),
                'label': self._landing_label(institution, is_event),
                'url': landing,
                'format': 'Web',
                'local': False,
                'external': True,
            })

        return self._dedupe_resources(candidates)

    def _local_file_resource(
        self,
        kind: str,
        filename: str,
        directory: str,
        url_prefix: str,
        title: str,
        label: str,
        primary: bool = False,
        subtitle: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Verify local file exists; warn and omit if missing."""
        basename = os.path.basename(filename.strip())
        path = os.path.join(directory, basename)
        if not os.path.isfile(path):
            self.warnings.append(
                f"Missing local {kind} file '{basename}' — omitting from resources"
            )
            return None

        resource: Dict[str, Any] = {
            'kind': kind,
            'title': title,
            'label': label,
            'url': f"{url_prefix}{basename}",
            'format': self._format_from_filename(basename),
            'local': True,
            'external': False,
        }
        if primary:
            resource['primary'] = True
        if subtitle:
            resource['subtitle'] = subtitle
        return resource

    def _dedupe_resources(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Keep one resource per normalized URL; most specific kind wins."""
        by_url: Dict[str, Dict[str, Any]] = {}
        for resource in candidates:
            url_key = self._normalize_url_key(resource.get('url', ''))
            if not url_key:
                continue
            existing = by_url.get(url_key)
            if not existing:
                by_url[url_key] = resource
                continue
            if self.KIND_SPECIFICITY.get(resource['kind'], 0) > self.KIND_SPECIFICITY.get(
                existing['kind'], 0
            ):
                # Preserve primary flag if the loser had it
                if existing.get('primary') and not resource.get('primary'):
                    resource = dict(resource)
                    resource['primary'] = True
                by_url[url_key] = resource

        ordered = list(by_url.values())
        ordered.sort(key=lambda r: self.KIND_ORDER.index(r['kind'])
                      if r['kind'] in self.KIND_ORDER else 99)

        # Ensure at most one primary; prefer explicit pdf primary
        primary_seen = False
        for resource in ordered:
            if resource.get('primary'):
                if primary_seen:
                    resource.pop('primary', None)
                else:
                    primary_seen = True
        if not primary_seen:
            for resource in ordered:
                if resource.get('local') and resource.get('kind') == 'pdf':
                    resource['primary'] = True
                    break

        return ordered

    def _pdf_action_label(self, entry_type: str) -> str:
        if entry_type.strip().lower() == 'report':
            return 'View report PDF'
        return 'View primary document'

    def _landing_title(self, institution: Optional[str], is_event: bool) -> str:
        return self._landing_label(institution, is_event)

    def _landing_label(self, institution: Optional[str], is_event: bool) -> str:
        if institution:
            return f"Visit {institution} publication page"
        if is_event:
            return 'Visit event website'
        return 'Visit publication page'

    def _format_from_filename(self, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        return self.FORMAT_BY_EXT.get(ext, ext.lstrip('.').upper() or 'File')

    @staticmethod
    def _normalize_url_key(url: str) -> str:
        return url.strip().rstrip('/').lower()

    # ------------------------------------------------------------------
    # Standfirst / description / event
    # ------------------------------------------------------------------

    def _build_standfirst(self, entry: Dict[str, Any], abstract: Optional[str]) -> Optional[str]:
        """Emit standfirst from description/summary, else first abstract paragraph."""
        for field in ('description', 'summary'):
            raw = self._strip_str(entry.get(field))
            if raw and raw.lower() not in {'untitled', ''}:
                cleaned = self._plain_text(raw)
                if cleaned and len(cleaned) >= 40:
                    return self._cap_standfirst(cleaned)

        if abstract:
            first_para = self._first_paragraph(abstract)
            if first_para:
                return self._cap_standfirst(first_para)
        return None

    def _build_description(
        self,
        entry: Dict[str, Any],
        abstract: Optional[str],
        title: str,
        standfirst: Optional[str],
    ) -> Optional[str]:
        if standfirst:
            return standfirst
        if abstract:
            return self._cap_standfirst(self._plain_text(abstract))
        return self._strip_str(title)

    def _compute_is_event(self, entry_type: str) -> bool:
        return self._normalize_event_key(entry_type) is not None

    def _normalize_event_key(self, entry_type: str) -> Optional[str]:
        raw = re.sub(r'[^a-z0-9\s]', ' ', (entry_type or '').lower())
        raw = re.sub(r'\s+', ' ', raw).strip()
        if not raw:
            return None
        if raw in self.EVENT_ALIASES:
            return self.EVENT_ALIASES[raw]
        if raw in self.EVENT_TYPES:
            return raw
        tokens = raw.split()
        for et in self.EVENT_TYPES:
            if et in tokens or raw.startswith(et + ' ') or raw.endswith(' ' + et):
                return et
        return None

    def _first_paragraph(self, text: str) -> Optional[str]:
        plain = self._plain_text(text)
        if not plain:
            return None
        parts = re.split(r'\n\s*\n', plain)
        for part in parts:
            candidate = self._strip_str(part)
            if candidate and len(candidate) >= 20:
                return candidate
        return plain if len(plain) >= 20 else None

    def _cap_standfirst(self, text: str) -> str:
        text = self._strip_str(text) or ''
        if len(text) <= self.STANDFIRST_MAX_CHARS:
            return text

        # Prefer ending on a sentence boundary within the limit
        window = text[: self.STANDFIRST_MAX_CHARS + 1]
        sentence_end = max(window.rfind('. '), window.rfind('! '), window.rfind('? '))
        if sentence_end >= 80:
            return text[: sentence_end + 1].strip()

        cut = text[: self.STANDFIRST_MAX_CHARS]
        if ' ' in cut:
            cut = cut.rsplit(' ', 1)[0]
        return cut.rstrip('.,;:') + '…'

    def _plain_text(self, text: str) -> str:
        if not text:
            return ''
        text = html.unescape(text)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'[*_`#\[\]{}]', '', text)
        text = re.sub(r'\\[%&]', lambda m: m.group(0)[-1], text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    # ------------------------------------------------------------------
    # Annote helpers / preview / normalisation utilities
    # ------------------------------------------------------------------

    def _extract_annote_lines(self, entry: Dict[str, Any], marker: str) -> List[str]:
        annote = entry.get('annote', '')
        if not annote or marker not in annote:
            return []
        section = annote.split(marker)[-1].split('[')[0]
        lines = []
        seen = set()
        for line in section.split('\n'):
            clean = self._strip_str(line.replace('@@', '@'))
            if clean and clean.lower() not in seen:
                lines.append(clean)
                seen.add(clean.lower())
        return lines

    def _resolve_preview(
        self, entry: Dict[str, Any], processed_images: List[str]
    ) -> Optional[str]:
        """Prefer existing BibTeX preview file, then generated thumbnail, then gallery."""
        bib_preview = self._strip_str(entry.get('preview'))
        if bib_preview:
            basename = os.path.basename(bib_preview)
            stem, ext = os.path.splitext(basename)
            candidates = []
            if ext:
                candidates.append(basename)
            else:
                candidates.extend([f"{stem}.jpeg", f"{stem}.jpg", f"{stem}.png"])
            for name in candidates:
                path = os.path.join(self.config.PREVIEW_DIR, name)
                if os.path.isfile(path):
                    return os.path.splitext(name)[0]

        thumbnail = self._check_for_existing_thumbnail(entry)
        if thumbnail:
            return thumbnail

        if processed_images:
            return processed_images[0]
        return None

    @staticmethod
    def resolve_hero_preview_src(preview: Optional[str]) -> Optional[str]:
        """Build the site-root image URL used by the library item hero.

        Front matter often stores the preview basename *without* an extension
        (historical convention). The hero template must append ``.jpeg`` in that
        case; otherwise the browser requests a path with no file and renders the
        alt text as visible placeholder copy.

        This helper mirrors ``_includes/library/hero.liquid`` so pytest can lock
        the contract without running Jekyll.
        """
        if preview is None:
            return None
        text = str(preview).strip()
        if not text:
            return None
        if '://' in text:
            return text

        basename = os.path.basename(text)
        if '.' not in basename:
            basename = f'{basename}.jpeg'
        return f'/assets/img/publication_preview/{basename}'

    @staticmethod
    def preview_src_resolves_on_disk(preview: Optional[str], preview_dir: str) -> bool:
        """Return True if ``resolve_hero_preview_src`` points at an existing file."""
        src = ContentGenerator.resolve_hero_preview_src(preview)
        if not src or '://' in src:
            return bool(src and '://' in src)
        filename = os.path.basename(src)
        return os.path.isfile(os.path.join(preview_dir, filename))

    def _build_date_str(self, year: str, month: str) -> str:
        try:
            month_names = {
                'jan': 1, 'january': 1,
                'feb': 2, 'february': 2,
                'mar': 3, 'march': 3,
                'apr': 4, 'april': 4,
                'may': 5,
                'jun': 6, 'june': 6,
                'jul': 7, 'july': 7,
                'aug': 8, 'august': 8,
                'sep': 9, 'sept': 9, 'september': 9,
                'oct': 10, 'october': 10,
                'nov': 11, 'november': 11,
                'dec': 12, 'december': 12,
            }
            month_l = re.sub(r'[^a-z0-9]', '', str(month).lower())
            if month_l in month_names:
                month_num = month_names[month_l]
            else:
                month_num = int(month)
            date_obj = datetime(int(year), month_num, 1)
            return date_obj.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            return f"{year}-01-01"

    @staticmethod
    def _strip_str(value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, (list, tuple)):
            return None
        text = str(value).strip()
        return text if text else None

    @staticmethod
    def _set_if(target: Dict[str, Any], key: str, value: Optional[str]) -> None:
        if value:
            target[key] = value

    @staticmethod
    def _set_list(target: Dict[str, Any], key: str, values: List[Any]) -> None:
        cleaned = [v for v in values if v is not None and str(v).strip() != '']
        if cleaned:
            target[key] = cleaned

    @staticmethod
    def _dedupe_list(values: List[str]) -> List[str]:
        seen = set()
        result = []
        for value in values:
            key = value.lower()
            if key not in seen:
                seen.add(key)
                result.append(value)
        return result

    def _determine_categories(self, entry: Dict[str, Any], keywords: List[str]) -> List[str]:
        """Determine categories based on entry type and keywords."""
        categories = []

        entry_type = entry.get('type', '').lower()
        if entry_type == 'article':
            categories.append('publications')
        elif entry_type in ['inproceedings', 'incollection']:
            categories.append('conferences')
        elif entry_type in ['phdthesis', 'mastersthesis', 'thesis']:
            categories.append('theses')
        elif entry_type == 'techreport':
            categories.append('reports')
        elif entry_type == 'misc':
            if any(kw in keywords for kw in ['blog', 'webinar', 'workshop']):
                categories.append('events')
            else:
                categories.append('other')
        else:
            categories.append('other')

        topic_keywords = {
            'ocean': 'ocean-governance',
            'energy': 'energy-policy',
            'renewable': 'renewable-energy',
            'climate': 'climate-change',
            'marine': 'marine-policy',
            'biodiversity': 'biodiversity',
            'sustainability': 'sustainability',
            'policy': 'policy',
            'governance': 'governance',
        }

        for keyword in keywords:
            for topic, category in topic_keywords.items():
                if topic in keyword.lower():
                    if category not in categories:
                        categories.append(category)
                    break

        return categories if categories else ['other']

    def _check_for_existing_thumbnail(self, entry: Dict[str, Any]) -> Optional[str]:
        """Check if a thumbnail exists for this entry's PDF."""
        citation_key = entry.get('ID', '')
        if not citation_key:
            return None

        try:
            thumbnail_filename = self.text_processor.generate_filename(
                citation_key,
                entry,
                'jpeg',
                check_directory=self.config.PREVIEW_DIR,
            )

            if thumbnail_filename:
                thumbnail_path = os.path.join(self.config.PREVIEW_DIR, thumbnail_filename)
                if os.path.exists(thumbnail_path):
                    return thumbnail_filename.replace('.jpeg', '').replace('.jpg', '')
        except Exception:
            pass

        return None

    def _find_processed_images(self, entry: Dict[str, Any]) -> List[str]:
        """Find processed image filenames for this entry."""
        if not os.path.exists(self.config.IMAGES_DIR):
            return []

        author_filename = self.text_processor.extract_author_names_for_filename(
            entry.get('author', '')
        )
        title = entry.get('title', '')
        condensed_title = self.text_processor.remove_filler_words(title)
        clean_filename = self.text_processor.slugify_title(
            condensed_title, max_length=190, separator='_'
        )
        year = entry.get('year', '')

        if author_filename and year:
            base_filename = f"{author_filename}_{year}_{clean_filename}"
        elif author_filename:
            base_filename = f"{author_filename}_{clean_filename}"
        else:
            base_filename = clean_filename

        base_filename = self.text_processor.clean_filename(base_filename).lower()

        candidates = []
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

        try:
            for filename in os.listdir(self.config.IMAGES_DIR):
                filename_lower = filename.lower()
                if filename_lower.startswith(base_filename) and (
                    '_photo_' in filename_lower or '_figure_' in filename_lower
                ):
                    for ext in image_extensions:
                        if filename_lower.endswith(ext):
                            candidates.append((
                                filename[:-len(ext)],
                                os.path.join(self.config.IMAGES_DIR, filename),
                            ))
                            break

            candidates.sort(key=lambda item: item[0])
        except Exception:
            return []

        return self._dedupe_images_by_content(candidates)

    @staticmethod
    def _dedupe_images_by_content(candidates: List[Tuple[str, str]]) -> List[str]:
        """Keep the first stem for each unique file hash (and each unique stem)."""
        unique = []
        seen_stems = set()
        seen_hashes = set()
        for stem, path in candidates:
            stem_key = stem.lower()
            if stem_key in seen_stems:
                continue
            seen_stems.add(stem_key)
            try:
                with open(path, 'rb') as handle:
                    digest = hashlib.md5(handle.read()).hexdigest()
            except OSError:
                unique.append(stem)
                continue
            if digest in seen_hashes:
                continue
            seen_hashes.add(digest)
            unique.append(stem)
        return unique

    def generate_content(self, entry: Dict[str, Any]) -> str:
        """Generate the main content for the library page.

        Keep body light: hero/materials/event panels are driven by front matter.
        Only emit Notes when present; skip redundant Publication Details / Links.
        """
        content_parts = []

        if entry.get('note'):
            note = entry['note']
            note_lines = note.split('\n')
            clean_lines = []
            for line in note_lines:
                line = line.strip()
                if line and not line.startswith('http'):
                    clean_lines.append(line)

            if clean_lines:
                content_parts.append("## Notes\n")
                content_parts.append('\n'.join(clean_lines))
                content_parts.append("")

        return '\n'.join(content_parts)
