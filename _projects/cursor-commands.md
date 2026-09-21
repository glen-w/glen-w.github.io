---
layout: page
title: cursor-commands
description: Reusable Cursor slash commands for backup, tests, and a local pre-release check.
importance: 3
category: ongoing
github: https://github.com/glen-w/cursor-commands
---

I kept rewriting the same Cursor prompts in every repo: zip a code backup, run the fast tests, format, and write a local pre-release note. These files are the generic versions. A product keeps its own filled copy under `.cursor/commands/`, gitignored, because that copy names ports, fixtures, and probe paths.

Open the repository in Cursor and run `/instantiate` against the product checkout, or copy `commands/*.md` (not the files whose names start with `_`) and replace every `__TOKEN__` from a project card. Skip the Streamlit and Docker commands when the product has neither.
