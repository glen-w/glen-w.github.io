---
layout: page
title: data dumps
description: Ingest your own GDPR and app exports into DuckDB, then explore them locally.
importance: 7
category: ongoing
github: https://github.com/glen-w/data_dumps
---

**data dumps** ingests your own GDPR and app exports into DuckDB, then explores them in a local [Marimo](https://marimo.io) dashboard. It is not a hosted service. Dumps and the warehouse stay on your machine, outside the git tree.

---

## Why data dumps

Takeout zips are awkward to read one by one. data dumps is a local warehouse for the exports you already requested:

- One ingest command, one DuckDB file
- A loopback dashboard, including Compare and Correlations once more than one source is loaded
- IPs, phones, ads, and KYC stay out of the source tables

If you only need to open one CSV, stay in a spreadsheet. If you want several exports in one place, on disk, this is the tool.

---

## Getting started

Python 3.11+ and [uv](https://docs.astral.sh/uv/). Put exports under `~/Documents/data_dumps_raw` (or `DATA_DUMPS_ROOT`).

```sh
git clone https://github.com/glen-w/data_dumps.git
cd data_dumps
uv sync
uv run ingest /path/to/my_spotify_data.zip
uv run marimo run notebooks/explorer.py --host 127.0.0.1 --port 2718
```

The dashboard has no password. Bind it to localhost. Stop it before the next ingest — the warehouse is single-writer.

---

## Links

- [GitHub](https://github.com/glen-w/data_dumps)
- [Product site](https://glenwright.earth/data_dumps/)
- [Getting your data](https://github.com/glen-w/data_dumps/blob/main/docs/guides/getting-your-data.md)
