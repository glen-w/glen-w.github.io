# Attachments Pipeline & Unhideable Sections Assessment

## Current Status

### 1. Attachments Pipeline - **PARTIALLY WORKING**

#### What Works:
- **Thumbnail attachments**: Processed correctly, creates `preview` field
- **PDF attachments**: Processed correctly, creates `pdf` field
- **Image attachments**: Processed correctly, creates `photos` or `figures` fields
- **Agenda PDFs**: Extracted but **only used for thumbnail generation priority**, NOT created as `agenda` field

#### What Doesn't Work:
- **Agenda PDFs**: Not converted to `agenda` field in BibTeX
- **Slides PDFs**: Only created if keywords detected (presenter, speaker, prezi, miro), NOT based on attachment name
- **Handout PDFs**: Not processed at all
- **Poster PDFs**: Not processed from attachments (only if manually added as `poster` field)
- **Other attachment types**: Not processed

#### Current Processing Logic:
1. **PDF Processing** (`paper_processor.py`):
   - Extracts all PDFs from `file` field
   - Processes them into `assets/pdf/` directory
   - Creates `pdf` field OR `slides` field based on keyword detection
   - Does NOT check attachment name/description for type

2. **Agenda Extraction** (`bibtex_processor.py`):
   - `extract_agenda_pdfs()` extracts agenda PDFs
   - Used ONLY for thumbnail generation priority
   - NOT converted to `agenda` field

3. **Slides Detection**:
   - Based on keywords in entry: "presenter", "speaker", "prezi", "miro"
   - NOT based on attachment name containing "slides"

#### Missing Functionality:
- No code to create `agenda` field from agenda attachments
- No code to create `slides` field from slides attachments (by name)
- No code to create `handout` field from handout attachments
- No code to create `poster` field from poster attachments

### 2. Unhideable Sections - **MOSTLY WORKING WITH ISSUES**

#### What Works:
- **Abstract section**: Uses `.hidden` class, JavaScript toggles `.open` class
- **Quotes section**: Uses `.hidden` class, JavaScript toggles `.open` class
- **Video section**: Uses `.hidden` class, JavaScript toggles `.open` class
- **Audio section**: Uses `.hidden` class, JavaScript toggles `.open` class
- **Figures/Photos sections**: Uses `.hidden` class, JavaScript toggles `.open` class
- **Documents section**: Uses `.hidden` class, JavaScript toggles `.open` class

#### Issues Found:

1. **Speakers Section - CLASS CONFLICT**:
   - HTML uses: `class="collapse speakers"` (Bootstrap collapse)
   - JavaScript uses: `.speakers.hidden` selector
   - **Problem**: Speakers div doesn't have `.hidden` class, so JavaScript won't find it!
   - **Impact**: Speakers section toggle may not work correctly

2. **Section Visibility**:
   - All sections use `.hidden` class (display:none by default)
   - JavaScript adds `.open` class to show (display:block)
   - **This is correct** - sections are hidden by default, shown when clicked

3. **Section Extraction**:
   - Abstract: Extracted from `[abstract]` block OR `abstract` field ✅
   - Speakers: Extracted from `[speakers]` block ✅
   - Quotes: Extracted from `[quotes]` block ✅
   - Video: Extracted from `[video]` block OR `video` field ✅
   - Audio: Extracted from `[audio]` block ✅

## Issues Identified

### Critical Issues:

1. **Speakers Section Class Mismatch**:
   - Location: `_layouts/bib.liquid` line 931
   - Current: `<div id="spk-{{ entry.key }}" class="collapse speakers">`
   - JavaScript expects: `.speakers.hidden`
   - **Fix needed**: Add `hidden` class to speakers div

2. **Agenda Attachments Not Processed**:
   - Agenda PDFs extracted but not converted to `agenda` field
   - No button/link created for agenda PDFs
   - **Fix needed**: Create `agenda` field from agenda attachments

3. **Slides Detection Incomplete**:
   - Only detects slides by keywords, not by attachment name
   - If attachment named "slides.pdf" but no keywords, won't create `slides` field
   - **Fix needed**: Check attachment name/description for "slides"

### Medium Priority Issues:

4. **Handout/Poster Attachments**:
   - Not processed at all
   - Would need to add processing logic

5. **Section Robustness**:
   - All sections depend on JavaScript for toggling
   - If JavaScript fails, sections remain hidden
   - Could add CSS-only fallback or ensure JavaScript always loads

## Recommendations

### Immediate Fixes:

1. **Fix Speakers Section**:
   - Change `class="collapse speakers"` to `class="collapse speakers hidden"`
   - OR update JavaScript to use `.speakers` selector instead of `.speakers.hidden`

2. **Add Agenda Field Processing**:
   - After extracting agenda PDFs, create `agenda` field
   - Add agenda button rendering in `bib.liquid`

3. **Improve Slides Detection**:
   - Check attachment name/description for "slides" in addition to keywords
   - Create `slides` field if attachment name contains "slides"

### Future Enhancements:

4. **Add Handout/Poster Processing**:
   - Extract handout PDFs from attachments
   - Extract poster PDFs from attachments
   - Create respective fields

5. **Add Attachment Type Detection**:
   - Create mapping: attachment name → BibTeX field
   - Support: agenda → `agenda`, slides → `slides`, handout → `handout`, poster → `poster`

6. **Improve Section Robustness**:
   - Add CSS fallback for sections
   - Ensure JavaScript always loads
   - Add error handling for missing sections

## Testing Needed

1. **Test Speakers Section**:
   - Verify speakers button works
   - Verify speakers section displays when clicked
   - Check if JavaScript selector matches HTML class

2. **Test Agenda Attachments**:
   - Add entry with agenda PDF attachment
   - Verify `agenda` field is created
   - Verify agenda button appears in bibliography

3. **Test Slides Detection**:
   - Add entry with "slides.pdf" attachment (no keywords)
   - Verify `slides` field is created
   - Verify slides button appears

4. **Test All Sections**:
   - Verify all unhideable sections work
   - Test with entries that have multiple sections
   - Verify sections close when another is opened


