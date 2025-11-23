# Tag Extraction Audit Report

## Overview
This document maps all tag extraction points in the codebase, identifies inconsistencies, and documents the data flow from Zotero export through processing to display.

## Tag Extraction Points

### 1. Processing: `processing/core/notes_processor.py`

**Purpose**: Extracts tags from Zotero notes/annote fields and adds them to keywords field for backward compatibility.

**Methods**:
- `extract_type_from_notes(notes: str)` - Extracts `[type]` section
- `extract_role_from_notes(notes: str)` - Extracts `[role]` section  
- `extract_language_from_notes(notes: str)` - Extracts `[language]` section

**Logic**:
- Splits on `[tag]` marker, takes last occurrence, splits on `[` to get content
- Type: Returns as-is (preserves multiword types)
- Role: Returns `.lower()` (normalized to lowercase)
- Language: Returns `.lower()` (normalized to lowercase)
- **Adds extracted tags to keywords field** (comma-separated)

**Issues**:
- Tags are added to keywords, creating dual-source system
- No validation of tag values
- Case handling: type preserved, role/language lowercased

### 2. Filter Generation: `processing/library/dynamic_filters.py`

**Purpose**: Generates `_data/dynamic_filters.yml` from bibliography entries.

**Logic**:
- **Entry Types**: 
  - Checks `note` field for `[type]` section first
  - Falls back to `annote` field for `[type]` section
  - Falls back to BibTeX ENTRYTYPE with mapping
  - Uses `.capitalize()` on extracted type (inconsistent with notes_processor)
  
- **Role Tags**:
  - Checks `note` field for `[role]` section
  - Checks `annote` field for `[role]` section
  - Also checks `keywords` field for role keywords
  - Uses `.lower()` (consistent)
  
- **Language Tags**:
  - Checks `note` field for `[language]` section
  - Checks `annote` field for `[language]` section
  - Also checks `keywords` field for language indicators (emoji/text)
  - Uses `.lower()` (consistent)
  - Only accepts: 'french', 'spanish', 'chinese'

**Issues**:
- Type extraction uses `.capitalize()` but notes_processor preserves case
- Checks both notes/annote AND keywords (dual-source)
- Language validation is hardcoded

### 3. Display: `_layouts/bib.liquid`

**Purpose**: Renders bibliography items with tags displayed.

**Logic**:
- **Entry Type**:
  - Checks `note` field for `[type]` section first
  - Falls back to `annote` field for `[type]` section
  - Falls back to BibTeX ENTRYTYPE mapping
  - Uses `.replace('@@', '@')` to unescape (for BibTeX compatibility)
  - **Note**: Line 80 doesn't capitalize, line 98 does capitalize (inconsistency!)
  
- **Role Tags**:
  - Checks `entry.role` or `entry.roles` or `entry.notes` (legacy)
  - Checks `block_role` from structured notes `[role]` section
  - Displays as `<span class="tag">` elements
  
- **Language Tags**:
  - Checks `note` field for `[language]` section
  - Checks `annote` field for `[language]` section
  - Uses `.downcase()` and maps to emoji flags
  - Displays as formatted tags (e.g., "🇫🇷 French")

**Issues**:
- Type capitalization inconsistency (line 80 vs 98)
- Role extraction checks legacy fields (`entry.role`, `entry.roles`)
- Language display format differs from filter format

### 4. Filter Matching: `_pages/library.md` (JavaScript)

**Purpose**: Client-side filtering and count calculation.

**Logic**:
- `itemMatchesFilter(item, filterText)` function:
  - Checks `.item-type .tag` elements for role tags
  - Checks `.all-tags .tag` elements for language tags
  - Checks `.item-type .badge` elements for entry types
  - Falls back to pattern matching with hardcoded patterns
  - Falls back to simple text matching

**Issues**:
- Relies on specific CSS classes that may not exist
- Complex fallback logic prone to false matches
- Case-sensitive matching may miss items
- Pattern matching is hardcoded and may not match all types

## Data Flow

```
Zotero Export (Exported Items.bib)
  └─> Contains annote/note fields with [type], [role], [language] tags
      │
      ├─> Processing (main.py → paper_processor.py → bibtex_processor.py)
      │   └─> notes_processor.py extracts tags
      │       └─> Adds tags to keywords field (dual storage)
      │
      ├─> Output: papers.bib
      │   └─> Contains both note/annote fields AND keywords field
      │
      ├─> Dynamic Filters Generation (dynamic_filters.py)
      │   └─> Reads from note/annote AND keywords
      │   └─> Generates _data/dynamic_filters.yml
      │
      ├─> Library Page Generation (generator.py)
      │   └─> Generates _library/*.md pages
      │
      └─> Display (bib.liquid)
          └─> Reads from note/annote fields
          └─> Renders HTML with .badge and .tag classes
              └─> JavaScript (library.md) matches filters
                  └─> Counts items by CSS class matching
```

## Inconsistencies Identified

### 1. Case Handling
- **Type**: 
  - notes_processor: Preserves original case
  - dynamic_filters: Uses `.capitalize()`
  - bib.liquid: Line 80 preserves, line 98 capitalizes
  - **Impact**: Same type may appear differently in filters vs display

- **Role**: 
  - All use `.lower()` - **Consistent**

- **Language**: 
  - All use `.lower()` - **Consistent**

### 2. Source Priority
- **notes_processor**: Only reads from notes/annote, writes to keywords
- **dynamic_filters**: Reads from notes/annote AND keywords
- **bib.liquid**: Only reads from notes/annote
- **JavaScript**: Only reads from rendered HTML (CSS classes)

**Impact**: Keywords field may contain tags that aren't in notes, causing confusion

### 3. Extraction Logic Differences
- **notes_processor**: Simple split on `[tag]`, takes last occurrence
- **dynamic_filters**: Same logic
- **bib.liquid**: Same logic
- **JavaScript**: DOM-based matching with fallback patterns

**Impact**: All extraction logic is consistent, but JavaScript matching differs

### 4. Type Display Format
- **notes_processor**: Preserves original (e.g., "Journal Article")
- **dynamic_filters**: Capitalizes first letter (e.g., "Journal article")
- **bib.liquid**: Mixed (preserves or capitalizes depending on source)
- **JavaScript**: Matches against displayed text

**Impact**: Filter may not match displayed type due to capitalization differences

### 5. Language Format
- **Storage**: Lowercase ("french", "spanish", "chinese")
- **Display**: Formatted with emoji ("🇫🇷 French", "🇪🇸 Spanish")
- **Filter**: Lowercase in YAML, but JavaScript matches against display

**Impact**: Filter matching may fail if JavaScript doesn't handle emoji properly

## Recommendations

1. **Unify Case Handling**: Standardize on one approach (preserve original vs normalize)
2. **Single Source of Truth**: Use notes/annote fields only, remove keywords dependency
3. **Consistent Extraction**: Use same extraction function across all modules
4. **Server-Side Filter Counts**: Generate counts during processing, not client-side
5. **Type Format Standardization**: Decide on capitalization and apply consistently
6. **Language Format**: Store and match consistently (with or without emoji)


