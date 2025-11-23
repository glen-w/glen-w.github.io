# Zotero Integration Guide

## Overview

The paper processing system integrates with Zotero by extracting structured tags from the **Notes** field in Zotero entries. Tags are specified using a simple bracket notation format that is preserved during BibTeX export.

## Tag Format

Tags are specified in the Zotero **Notes** field using the following format:

```
[type]
Entry Type Name

[role]
role1
role2

[language]
language1
```

### Entry Types (`[type]`)

Specifies the type/category of the entry. Can be any value, but common types include:

- Journal Article
- Conference Paper
- Book Chapter
- Book
- Webinar
- Workshop
- Roundtable
- Panel
- Blog
- Newspaper
- Report
- Briefing Note
- Guest Lecture

**Format**: Single line after `[type]` marker

**Example**:
```
[type]
Webinar
```

**Case Handling**: The system normalizes entry types to Title Case (e.g., "webinar" → "Webinar"). You can use any case in Zotero, but the displayed format will be standardized.

### Role Tags (`[role]`)

Specifies the author's role(s) in the work. Multiple roles can be specified, one per line.

**Valid Roles**:
- attendee
- co-author
- contributor
- coordinator
- delegate
- editor
- facilitator
- featured
- interview
- lead author
- moderator
- organiser (or organizer)
- panelist (or panellist)
- participant
- presenter
- quoted
- speaker

**Format**: One role per line after `[role]` marker

**Example**:
```
[role]
moderator
speaker
```

**Case Handling**: All roles are normalized to lowercase. You can use any case in Zotero.

### Language Tags (`[language]`)

Specifies the language(s) of the work. Currently supports:

- french
- spanish
- chinese

**Format**: One language per line after `[language]` marker

**Example**:
```
[language]
french
```

**Case Handling**: All languages are normalized to lowercase. You can use any case in Zotero.

## Complete Example

Here's a complete example of a Zotero Notes field with all tag types:

```
This is supplementary information about the entry.

[type]
Webinar

[role]
moderator
speaker

[language]
french

[speakers]
Speaker Name 1
Speaker Name 2

[video]
https://www.youtube.com/watch?v=example

[abstract]
This is the abstract text...
```

## Processing Flow

1. **Zotero Export**: Export bibliography from Zotero as BibTeX
   - The Notes field becomes the `annote` field in BibTeX
   - Tags are preserved exactly as entered

2. **Processing**: Run `processing/main.py`
   - Tags are extracted from `annote`/`note` fields
   - Tags are also added to `keywords` field for backward compatibility
   - All roles and languages are extracted (not just first)

3. **Filter Generation**: Dynamic filters are generated
   - Entry types, roles, and languages are collected
   - `_data/dynamic_filters.yml` is generated

4. **Display**: Tags are displayed in bibliography items
   - Entry types shown as badges
   - Roles shown as tags
   - Languages shown with emoji flags

## Best Practices

### 1. Use Consistent Naming

- Use standard entry type names when possible (see list above)
- Use lowercase for roles and languages (they'll be normalized anyway)
- Use Title Case for entry types (they'll be normalized anyway)

### 2. Multiple Values

- **Roles**: List multiple roles, one per line
- **Languages**: List multiple languages, one per line
- **Entry Type**: Only one entry type per entry (use the first if multiple)

### 3. Tag Placement

- Place tags at the end of the Notes field, after other content
- Use blank lines between sections for readability
- Keep tag sections together

### 4. Validation

The system validates:
- Entry types: Any value accepted
- Roles: Only recognized roles are used (others ignored)
- Languages: Only french, spanish, chinese are recognized

## Troubleshooting

### Tags Not Appearing

1. **Check Format**: Ensure tags use exact format `[type]`, `[role]`, `[language]`
2. **Check Field**: Tags must be in the Notes field (not other fields)
3. **Check Processing**: Re-run processing script after adding tags
4. **Check Export**: Ensure Notes field is included in Zotero export

### Incorrect Tag Display

1. **Case Issues**: Tags are normalized, so case differences shouldn't matter
2. **Multiple Roles**: All roles should be extracted (check keywords field)
3. **Filter Counts**: Filter counts should match displayed items (if not, see FILTER_COUNT_ANALYSIS.md)

### Processing Errors

1. **Invalid Format**: Check for typos in tag markers (`[type]` not `[Type]`)
2. **Special Characters**: @ symbols are automatically escaped
3. **Empty Sections**: Empty tag sections are ignored

## Migration from Old System

If you have existing entries with tags in the `keywords` field:

1. **Keep Both**: The system reads from both notes/annote AND keywords
2. **Gradual Migration**: Move tags to Notes field as you edit entries
3. **No Data Loss**: Old keywords are still recognized

## Technical Details

### Tag Extraction

Tags are extracted using the unified `TagExtractor` class:
- Location: `processing/core/tag_extractor.py`
- Used by: `notes_processor.py`, `dynamic_filters.py`
- Format: Preserves Zotero format exactly

### Case Normalization

- **Entry Types**: Title Case (first letter of each word capitalized)
- **Roles**: Lowercase
- **Languages**: Lowercase

### Storage

Tags are stored in two places:
1. **Notes/Annote Fields**: Primary source (preserves Zotero format)
2. **Keywords Field**: Secondary source (for backward compatibility)

The system prioritizes notes/annote fields over keywords field.

## Examples

### Journal Article
```
[type]
Journal Article
```

### Conference Paper with Role
```
[type]
Conference Paper

[role]
presenter
```

### Multilingual Work
```
[type]
Report

[language]
french
spanish
```

### Webinar with Multiple Roles
```
[type]
Webinar

[role]
moderator
speaker

[speakers]
Speaker 1
Speaker 2

[video]
https://www.youtube.com/watch?v=example
```


