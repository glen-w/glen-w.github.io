# Root Cause Analysis

## Executive Summary

The paper processing/library system has multiple inconsistencies in tag extraction, display, and filtering that cause filter counts to be inaccurate and filters to malfunction. The root causes are:

1. **CSS Selector Mismatch**: JavaScript uses `.item-type` but HTML uses `.item-type-and-roles`
2. **Case Handling Inconsistencies**: Different modules handle case differently (preserve vs capitalize vs lowercase)
3. **Dual-Source System**: Tags stored in both notes/annote AND keywords fields, causing confusion
4. **Incomplete Role Extraction**: Only first role extracted and added to keywords
5. **Type Format Inconsistencies**: Capitalization applied inconsistently across modules

## Detailed Root Causes

### 1. CSS Selector Mismatch (Critical)

**Root Cause**: JavaScript filter matching uses incorrect CSS selectors that don't match the actual HTML structure.

**Evidence**:
- JavaScript (`_pages/library.md`): Uses `.item-type .tag` and `.item-type .badge`
- HTML (`_layouts/bib.liquid`): Uses `.item-type-and-roles` as container class
- Result: Selectors return empty NodeLists, matching fails

**Impact**:
- Filter counts are inaccurate (fallback to unreliable text matching)
- Filters don't work correctly when clicked
- Role tags and entry type badges not matched properly

**Severity**: **CRITICAL** - Filters are fundamentally broken

### 2. Case Handling Inconsistencies

**Root Cause**: Different modules apply different case transformations to the same data.

**Evidence**:
- **Entry Types**:
  - `notes_processor.py`: Preserves original case ("webinar")
  - `dynamic_filters.py`: Uses `.capitalize()` ("Webinar")
  - `bib.liquid` line 80: Preserves case
  - `bib.liquid` line 98: Uses `.capitalize()`
  - Result: Same type appears differently in different places

- **Role Tags**:
  - All modules use `.lower()` - **Consistent**

- **Language Tags**:
  - All modules use `.lower()` - **Consistent**

**Impact**:
- Filter text ("Webinar") may not match display text ("webinar")
- JavaScript exact match (`===`) fails, falls back to pattern matching
- User confusion about correct capitalization

**Severity**: **HIGH** - Causes filter matching failures

### 3. Dual-Source System Confusion

**Root Cause**: Tags are stored in both notes/annote fields AND keywords field, with different modules reading from different sources.

**Evidence**:
- `notes_processor.py`: Reads from notes/annote, writes to keywords
- `dynamic_filters.py`: Reads from notes/annote AND keywords
- `bib.liquid`: Reads only from notes/annote
- JavaScript: Reads from rendered HTML (derived from notes/annote)

**Impact**:
- Keywords field may be incomplete (only first role added)
- Keywords field may contain tags not in notes (if manually edited)
- Unclear which source is authoritative
- Processing may overwrite manually-added keywords

**Severity**: **MEDIUM** - Causes data inconsistency but doesn't break core functionality

### 4. Incomplete Role Extraction

**Root Cause**: `extract_role_from_notes()` only returns the first role found, but entries may have multiple roles.

**Evidence**:
- Sample entry has: `[role]\nmoderator\nspeaker`
- `extract_role_from_notes()` returns: "moderator" only
- Keywords field contains: "moderator" only
- Display correctly shows: "moderator", "speaker"

**Impact**:
- Keywords field incomplete
- Filter generation works correctly (reads from annote directly)
- Display works correctly (reads from annote directly)
- Only affects keywords field consistency

**Severity**: **LOW** - Doesn't break functionality, but causes data inconsistency

### 5. Type Format Inconsistencies

**Root Cause**: Entry types are capitalized inconsistently, and the capitalization logic differs between modules.

**Evidence**:
- `dynamic_filters.py` line 87: Uses `.capitalize()` on extracted type
- `bib.liquid` line 80: Preserves original case
- `bib.liquid` line 98: Uses `.capitalize()` on annote-extracted type
- Result: Same type may appear as "webinar", "Webinar", or "WEBINAR"

**Impact**:
- Filter YAML contains capitalized types ("Webinar")
- Display may show lowercase types ("webinar")
- JavaScript matching fails exact match, uses fallback
- User confusion about correct format

**Severity**: **HIGH** - Causes filter matching failures

## Impact Assessment

### Filter Count Accuracy
- **Current State**: Inaccurate due to CSS selector mismatch
- **Root Cause**: JavaScript selectors don't match HTML structure
- **Impact**: Users see wrong counts, filters appear broken

### Filter Functionality
- **Current State**: Partially broken (relies on fallback text matching)
- **Root Cause**: CSS selector mismatch + case inconsistencies
- **Impact**: Filters may not work correctly, false positives/negatives

### Data Consistency
- **Current State**: Inconsistent between keywords and notes fields
- **Root Cause**: Dual-source system + incomplete extraction
- **Impact**: Confusion about which source is authoritative

### User Experience
- **Current State**: Confusing and unreliable
- **Root Cause**: Multiple issues compound
- **Impact**: Users lose trust in filter system

## Priority Fixes

### Priority 1: Fix CSS Selectors (Critical)
- Update JavaScript selectors to match HTML structure
- Change `.item-type` to `.item-type-and-roles`
- Test filter matching after fix

### Priority 2: Standardize Case Handling (High)
- Decide on case format: preserve original vs always capitalize
- Apply consistently across all modules
- Update filter generation and display to match

### Priority 3: Unify Tag Extraction (High)
- Create single extraction function used by all modules
- Use notes/annote as single source of truth
- Remove keywords field dependency (or document it clearly)

### Priority 4: Fix Role Extraction (Medium)
- Update `extract_role_from_notes()` to return all roles
- Add all roles to keywords field (if keeping keywords)
- Test with entries having multiple roles

### Priority 5: Add Validation (Medium)
- Add validation checks during processing
- Verify tags are preserved through pipeline
- Log warnings for inconsistencies

## Recommendations

1. **Immediate**: Fix CSS selectors in JavaScript (Priority 1)
2. **Short-term**: Standardize case handling (Priority 2)
3. **Medium-term**: Unify tag extraction logic (Priority 3)
4. **Long-term**: Consider removing keywords field dependency (Priority 3)
5. **Ongoing**: Add validation and testing (Priority 5)

## Success Metrics

After fixes:
- Filter counts match actual displayed items (100% accuracy)
- Filters work correctly when clicked (no false positives/negatives)
- Tags displayed consistently across all views
- No data loss through pipeline
- Clear documentation of tag format expectations


