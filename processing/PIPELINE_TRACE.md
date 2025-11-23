# Pipeline Trace Analysis

## Sample Entry: HighSeasTreaty2023

### Source: `_bibliography/Exported Items.bib`

```bibtex
@misc{HighSeasTreaty2023,
	type = {webinar},
	title = {High {Seas} {Treaty}: preliminary analysis and implementation challenges},
	annote = {[role]
moderator
speaker
[speakers]
Arne Langlet (University of Vienna)
...
[type]
webinar
[video]
https://www.youtube.com/watch?v=BmQHtQYfhQg
},
	...
}
```

**Tags in source**:
- Type: "webinar" (from `[type]` section)
- Roles: "moderator", "speaker" (from `[role]` section)
- Language: None

### Step 1: Processing (`processing/main.py` → `paper_processor.py` → `bibtex_processor.py`)

**Processing Flow**:
1. `bibtex_processor.py` calls `process_notes_from_zotero()`
2. This calls `notes_processor.process_notes_for_entry()`
3. `notes_processor` extracts tags and adds to keywords field

**What happens**:
- `extract_type_from_notes()`: Returns "webinar" (preserved case)
- `extract_role_from_notes()`: Returns "moderator" (lowercased, but multiple roles!)
- `extract_language_from_notes()`: Returns None

**Issue**: `extract_role_from_notes()` only returns the FIRST role found, but there are TWO roles ("moderator" and "speaker")!

**Keywords field update**:
- Original keywords: (none or existing)
- After processing: `keywords = {webinar, moderator}` (only first role added!)

### Step 2: Output (`_bibliography/papers.bib`)

**Expected output**:
```bibtex
@misc{HighSeasTreaty2023,
	type = {webinar},
	annote = {[role]
moderator
speaker
[type]
webinar
...
},
	keywords = {webinar, moderator},  // Added by processing
	...
}
```

**Tags preserved**:
- ✅ Type: "webinar" in annote `[type]` section
- ⚠️ Roles: "moderator", "speaker" in annote `[role]` section (but only "moderator" in keywords)
- ✅ Language: None

### Step 3: Dynamic Filters Generation (`processing/library/dynamic_filters.py`)

**Filter Generation Logic**:
1. Checks `note` field for `[type]` - not found
2. Checks `annote` field for `[type]` - finds "webinar"
3. Uses `.capitalize()` → "Webinar" (but original is lowercase!)
4. Adds to `entry_types` set

**Role Tags**:
1. Checks `note` field for `[role]` - not found
2. Checks `annote` field for `[role]` - finds "moderator\nspeaker"
3. Splits by lines, processes each:
   - "moderator" → adds to `role_tags` set (lowercase)
   - "speaker" → adds to `role_tags` set (lowercase)
4. Also checks `keywords` field - finds "moderator" (already added)

**Language Tags**:
- Checks both fields, finds nothing
- Checks keywords, finds nothing

**Output**: `_data/dynamic_filters.yml`
```yaml
entry_types:
  - Webinar  # Capitalized!
role_tags:
  - moderator
  - speaker
language_tags:
  - (none)
```

**Issues**:
- Type is capitalized to "Webinar" but original was "webinar"
- Both roles are correctly extracted (unlike keywords field)

### Step 4: Display (`_layouts/bib.liquid`)

**Type Extraction**:
1. Checks `note` field - not found
2. Checks `annote` field for `[type]` - finds "webinar"
3. Line 98: Uses `.capitalize()` → "Webinar"
4. Displays as: `<a class="badge badge-light">Webinar</a>`

**Role Extraction**:
1. Checks `entry.role`, `entry.roles`, `entry.notes` - not found (legacy)
2. Checks `block_role` from structured notes:
   - Extracts `[role]` section from combined notes
   - Splits by lines: "moderator", "speaker"
   - Displays as: `<span class="tag">moderator</span><span class="tag">speaker</span>`

**Language Extraction**:
- Checks both fields, finds nothing
- No language tags displayed

**HTML Output**:
```html
<div class="item-type-and-roles">
  <a class="badge badge-light">Webinar</a>
  <span class="tag">moderator</span>
  <span class="tag">speaker</span>
</div>
```

### Step 5: Filter Matching (`_pages/library.md` JavaScript)

**Filter Count Calculation**:
- Filter: "Webinar" (from YAML)
- JavaScript looks for `.item-type .badge` with text "webinar" (lowercased)
- **Problem**: CSS selector `.item-type` doesn't match `.item-type-and-roles`!
- Falls back to pattern matching, finds "webinar" in item text
- Count may be inaccurate

**Role Filter Matching**:
- Filter: "moderator" (from YAML)
- JavaScript looks for `.item-type .tag` with text "moderator"
- **Problem**: CSS selector `.item-type` doesn't match `.item-type-and-roles`!
- Falls back to text matching, may find false positives

**Language Filter Matching**:
- No language tags, so no matching needed

## Issues Identified

### 1. Multiple Roles Not Added to Keywords
- **Problem**: `extract_role_from_notes()` only returns first role
- **Impact**: Keywords field missing "speaker" role
- **Fix Needed**: Extract all roles, not just first

### 2. Type Capitalization Inconsistency
- **Problem**: `dynamic_filters.py` capitalizes types, but original may be lowercase
- **Impact**: Filter shows "Webinar" but source was "webinar"
- **Fix Needed**: Preserve original case or standardize

### 3. CSS Selector Mismatch
- **Problem**: JavaScript uses `.item-type` but HTML uses `.item-type-and-roles`
- **Impact**: Filter matching fails, falls back to unreliable text matching
- **Fix Needed**: Update JavaScript selectors

### 4. Keywords Field Redundancy
- **Problem**: Tags stored in both notes/annote AND keywords
- **Impact**: Dual-source system causes confusion, keywords may be incomplete
- **Fix Needed**: Use notes/annote as single source of truth

## Data Loss Points

1. **Role Extraction**: Only first role added to keywords (but all roles preserved in annote)
2. **Type Case**: Original case may be lost during capitalization
3. **Filter Matching**: CSS selector mismatch causes filter counts to be inaccurate

## Recommendations

1. Fix `extract_role_from_notes()` to return all roles, not just first
2. Standardize type case handling (preserve original or always capitalize)
3. Fix JavaScript CSS selectors to match actual HTML structure
4. Consider removing keywords field dependency, use notes/annote only
5. Add validation to ensure tags are preserved through pipeline


