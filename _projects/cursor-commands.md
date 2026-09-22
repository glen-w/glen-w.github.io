---
layout: page
title: Cursor Commands
description: Reusable Cursor slash commands for backup, tests, and a local pre-release check.
img: /assets/img/projects/thumbs/cursor_commands.png
importance: 3
category: ongoing
hidden: true
github: https://github.com/glen-w/cursor-commands
---

<div align="center">
  <img src="/assets/img/projects/thumbs/cursor_commands.png" alt="Cursor logo" width="160"/>
</div>

I kept rewriting the same prompts in every repository: make a code backup, run the fast tests, format, and write a local note before a release. The useful part was the habit, not the wording I invented each time.

These are the generic versions, as plain prompts you copy into a product and fill in once. The filled copy stays on that machine, because it names ports, fixtures, and how to probe that product. This repository is the templates, not an application.

A product keeps its own copy. Commands that would tag, push, prune images, or touch another project's port stay off. Docker and interface restarts are there only when the product uses them.

I am using the set across my own checkouts, and keeping the public templates generic enough that a new repository can start from them without inheriting someone else's paths.
