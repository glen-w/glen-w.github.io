# Filter Count Analysis

## JavaScript Selector Mismatches

### Issue 1: CSS Class Name Mismatch

**JavaScript Selectors** (in `_pages/library.md`):
- `.item-type .tag` - for role tags
- `.item-type .badge` - for entry type badges
- `.all-tags .tag` - for language tags

**Actual HTML Structure** (in `_layouts/bib.liquid`):
- Entry type and roles: `<div class="item-type-and-roles">`
  - Entry type: `<a class="badge badge-light">...</a>`
  - Role tags: `<span class="tag">...</span>`
- Language tags: `<div class="all-tags"><a class="tag">...</a>`

**Problem**: JavaScript uses `.item-type` but HTML uses `.item-type-and-roles`

**Impact**: 
- Role tag matching will FAIL (`.item-type .tag` won't match anything)
- Entry type badge matching will FAIL (`.item-type .badge` won't match anything)
- Language tag matching should work (`.all-tags .tag` matches correctly)

### Issue 2: Language Tag Format Mismatch

**JavaScript Matching**:
```javascript
const tagText = tag.textContent.toLowerCase().trim();
return tagText.includes(filterLower);
```

**Display Format**:
- Language tags are displayed as: "🇫🇷 French", "🇪🇸 Spanish", "🇨🇳 Chinese"
- Filter text in YAML is: "french", "spanish", "chinese"

**Problem**: 
- JavaScript does `.includes()` check, so "🇫🇷 French".includes("french") should work
- But the filter link text is just "french" (lowercase, no emoji)
- The matching might work, but the count might be off if display format differs

### Issue 3: Entry Type Case Sensitivity

**Filter Text Format** (from `_data/dynamic_filters.yml`):
- "Journal article" (capitalized)
- "Conference paper" (capitalized)
- etc.

**Display Format** (from `bib.liquid`):
- Line 253: `{{ item_type }}` - preserves original case from notes
- Line 80: Preserves case (no capitalization)
- Line 98: Uses `.capitalize()` (capitalizes first letter)

**JavaScript Matching**:
```javascript
const badgeText = badge.textContent.toLowerCase().trim();
return badgeText === filterLower;
```

**Problem**: 
- If display shows "Journal Article" but filter is "journal article", the exact match (`===`) will fail
- Falls back to pattern matching, which may or may not work

### Issue 4: Pattern Matching Fallback

The JavaScript has hardcoded patterns for common entry types:
```javascript
const patterns = {
  'journal article': ['journal article', 'article', 'journal'],
  'conference paper': ['conference paper', 'conference', 'inproceedings'],
  // etc.
}
```

**Problem**:
- Patterns are hardcoded and may not match all entry types
- If a new entry type is added, it won't be in the patterns
- Pattern matching uses `.includes()` on full item text, which may cause false positives

### Issue 5: Role Tag Extraction

**Display Logic** (`bib.liquid`):
- Checks `entry.role`, `entry.roles`, or `entry.notes` (legacy)
- Checks `block_role` from structured `[role]` section
- Displays as `<span class="tag">` inside `.item-type-and-roles`

**Filter Generation** (`dynamic_filters.py`):
- Checks `note` field for `[role]` section
- Checks `annote` field for `[role]` section
- Checks `keywords` field for role keywords
- Uses `.lower()`

**Problem**:
- Display may show roles from legacy fields that filters don't check
- Keywords field may contain roles that display doesn't show
- Case normalization may differ

## Test Cases Needed

1. **Entry Type Matching**:
   - Test with "Journal Article" vs "journal article"
   - Test with custom types not in pattern list
   - Verify CSS selector matches

2. **Role Tag Matching**:
   - Test with roles from `[role]` section
   - Test with roles from keywords field
   - Verify CSS selector matches (currently broken!)

3. **Language Tag Matching**:
   - Test with "french" filter vs "🇫🇷 French" display
   - Verify `.includes()` matching works correctly

4. **Filter Count Accuracy**:
   - Manually count items for each filter
   - Compare with JavaScript counts
   - Identify discrepancies

## Recommended Fixes

1. **Fix CSS Selectors**: Change `.item-type` to `.item-type-and-roles` in JavaScript
2. **Standardize Case**: Use consistent case normalization (lowercase for matching)
3. **Server-Side Counts**: Generate filter counts during processing, embed in page
4. **Unify Tag Extraction**: Use same extraction logic for display and filters
5. **Remove Pattern Fallback**: Rely on CSS class matching only, remove text matching

