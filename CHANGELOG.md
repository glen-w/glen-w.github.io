# Changelog

All notable changes to this website project will be documented in this file.

## [Unreleased]

### Changed
- **Navigation**: Renamed "writing" section to "library"
  - File renamed from `_pages/writing.md` to `_pages/library.md`
  - Permalink changed from `/writing/` to `/library/`
  - Title updated from "writing" to "library"
  - ROADMAP.md updated to reflect new URL

### Removed
- **Navigation**: Removed "speaking" page
  - Deleted `_pages/speaking.md` file
  - No other references found in codebase

### Modified
- **Styling**: Removed dropdown arrow from submenu navigation
  - Added CSS rule in `_sass/_base.scss` to hide dropdown arrow
  - Rule: `.navbar .dropdown-toggle::after { display: none !important; }`
  - Only affects navbar dropdowns, preserves dropdown functionality
  - Change documented in `_sass/_base.scss` around line 280

## [Previous Changes]

*Note: This changelog was started on the current date. Previous changes are not documented.*
