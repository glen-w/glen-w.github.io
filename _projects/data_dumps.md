---
layout: page
title: Data Dumps
description: Ingest your own GDPR and app exports into DuckDB, then explore them locally.
img: /assets/img/projects/thumbs/data_dumps.png
importance: 7
category: ongoing
github: https://github.com/glen-w/data_dumps
website: https://glenwright.earth/data_dumps/
docs: https://github.com/glen-w/data_dumps/blob/main/docs/guides/getting-your-data.md
---

<div align="center">
  <img src="/assets/img/projects/thumbs/data_dumps.png" alt="Data Dumps logo" width="200"/>
</div>

The exports I have a legal right to arrive as zips that are awkward to open one by one. A spreadsheet is enough for a single CSV. Several years of takeouts is a different problem.

Data Dumps puts those exports into one warehouse on this machine and opens them in a local dashboard. Nothing is hosted. The files stay here.

Once more than one source is loaded, I can compare them. Phone numbers, IPs, ads, and identity documents stay out of the tables I actually query.

I am running it on my own exports, and adding a source when I request the next dump.
