# Integrate Selected Publications from Zotero Notes

## Overview

Add support for `[selected]` tag in Zotero Notes field to automatically flag publications for display on homepage and library page. The tag will be extracted during paper processing and converted to `selected = {true}` in BibTeX entries.

## Implementation Steps

### Phase 1: Backup Files

Create timestamped backup directory in `backups/` folder

Backup all files that will be modified:

- `processing/core/tag_extractor.py`
- `processing/core/notes_processor.py`
- `processing/core/bibtex_processor.py`
- `_pages/about.md`
- `_pages/library.md`
- `_includes/selected_papers.liquid` (if exists, otherwise will be created)

### Phase 2: Add [selected] Tag Extraction

**Update `tag_extractor.py`:**
- Add `extract_selected()` method to check for `[selected]` marker in annote field
- Return boolean indicating if entry should be marked as selected
- Follow same pattern as existing `extract_languages()` method

**Update `notes_processor.py`:**
- In `_extract_and_populate_fields()` method, call tag extractor to check for `[selected]`
- If found, add `selected = {true}` to the entry dictionary
- This will be automatically formatted into BibTeX by `_format_entry_to_bibtex()`

### Phase 3: Enable Selected Publications on Homepage

**Update `_pages/about.md`:**
- Change `selected_papers: false` to `selected_papers: true`
- This enables the existing selected publications section in the about layout

### Phase 4: Add Selected Publications to Library Page

**Update `_pages/library.md`:**

1. **Add Selected Publications Toggle Button:**
   - Add toggle button in the filter-actions section (after the map toggle, around line 63)
   - Use similar styling as the map toggle button
   - Button should say "Hide Selected Publications" by default (since it shows by default)
   - Button ID: `selectedToggleBtn`
   - Function: `toggleSelectedPublications()`

2. **Add Selected Publications Container:**
   - Insert after the map container (around line 69)
   - Container ID: `selectedPublicationsContainer`
   - Initially visible (no `display: none` style)
   - Include heading "Selected Publications" or similar
   - Include the `selected_papers.liquid` include within the container
   - Style consistently with existing library page sections

3. **Add JavaScript Toggle Functionality:**
   - Create `toggleSelectedPublications()` function similar to `toggleMap()`
   - Toggle button text between "Hide Selected Publications" and "Show Selected Publications"
   - Toggle container visibility

4. **Add Auto-Hide Logic:**
   - Hide selected publications container when:
     - A filter is selected (any filter tag is clicked)
     - User types in the search box (search input has non-empty value)
     - Filter parameter is present in URL on page load
   - Show selected publications container when:
     - Filters are cleared (via clearFilters() function)
     - Search input is empty
     - No active filters or search terms
   - Add event listeners:
     - Listen to `filterByTag()` calls to hide container
     - Listen to search input `input` events to hide/show based on value
     - Listen to `clearFilters()` calls to show container
     - Check on page load for active filters/search and hide if needed

5. **Add CSS Styling:**
   - Style the selected publications container similar to map container
   - Style the toggle button to match existing filter action buttons
   - Ensure proper spacing and visual consistency

## Technical Details

### Zotero Notes Format

Users will add `[selected]` (case-insensitive) anywhere in the Notes field in Zotero. The tag extractor will look for this marker and extract it.

### BibTeX Output

When `[selected]` is found, the entry will have:
```
selected = {true},
```

### Display Locations

- **Homepage (`/`)**: Uses existing `selected_papers.liquid` include via about layout
- **Library Page (`/library/`)**: New section between map and full bibliography list
  - Shows by default
  - Has show/hide toggle button
  - Auto-hides when filters are active or user searches
  - Auto-shows when filters/search are cleared

### Files to Modify

- `processing/core/tag_extractor.py` - Add selected extraction method
- `processing/core/notes_processor.py` - Add selected field population
- `_pages/about.md` - Enable selected_papers feature
- `_pages/library.md` - Add selected publications section with show/hide toggle and JavaScript logic

## Testing

After implementation:

1. Add `[selected]` to a test entry's Notes field in Zotero
2. Export and run paper processing pipeline
3. Verify `selected = {true}` appears in processed BibTeX
4. Verify publications appear on homepage
5. Verify publications appear on library page by default
6. Verify toggle button works to show/hide selected publications
7. Verify selected publications auto-hide when:
   - Clicking any filter tag
   - Typing in search box
   - URL has filter parameter on load
8. Verify selected publications auto-show when:
   - Clearing filters
   - Clearing search input
   - No active filters or search

