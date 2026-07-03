---
layout: page
title: TranscriptX
description: A local-first transcript analysis toolkit
img: /assets/img/projects/thumbs/transcriptx_logo.png
importance: 5
category: ongoing
---

<div align="center">
  <img src="/assets/img/projects/thumbs/transcriptx_logo.png" alt="TranscriptX Logo" width="200"/>
</div>

TranscriptX is a **local-first transcript analysis toolkit**. It treats transcripts as canonical data and runs deterministic, reproducible analysis pipelines on your machine.

TranscriptX does not perform audio transcription — you bring your own transcript files from external tools (WhisperX, AssemblyAI, Deepgram, Otter, manual export, and others). The focus is on **analysis**: modular pipelines, structured outputs, and a space in which interpretation can develop without locking you into a single theory of language or meaning.

---

## Why TranscriptX

Most transcript tools are either cloud SaaS (Otter, Fireflies), transcription tools (Whisper, AssemblyAI), or research libraries with limited UX. TranscriptX sits in a different space:

- **Analyze transcripts locally** — your data stays on your machine
- **Run modular analysis pipelines** — apply the lenses you need, when you need them
- **Produce reproducible outputs** — traceable, structured, and revisit-able
- **Support both personal workflows and academic research**

The goal isn't to automate interpretation. It's to create a reliable space in which interpretation can develop — quickly when you need a snapshot, and slowly when you want to understand change.

---

## What kind of questions is TranscriptX for?

TranscriptX is useful when you find yourself asking things like:

- *What actually happened in this conversation?*
- *Where did tension rise or stall?*
- *Who speaks, who responds, and who shapes the flow?*
- *What themes keep returning — or quietly disappear?*
- *How does tone shift over time, or across sessions?*
- *What changes when the same people meet again and again?*

It's designed for researchers, facilitators, analysts, organisers, and anyone working seriously with spoken language — especially when intuition alone isn't enough, but full automation would be misleading.

---

## How it works

TranscriptX has two layers:

- **Engine** — pipeline and analysis modules
- **GUI** — Streamlit web interface

**Entry points:**

- **Web app (primary)** — the `transcriptx` console script starts the Streamlit app
- **Python API (secondary)** — typed workflows for automation and notebooks (`AnalysisRequest` + `run_analysis`)

A typical workflow is: raw transcript → managed import → analysis. Managed import admits files (WhisperX JSON, SRT, VTT, and others) into a canonical storage format; analysis modules then run against that canonical data.

TranscriptX runs in **file-first mode** out of the box. Groups, corrections, speaker mapping, and search/discovery are backed by files and sidecars.

---

## What TranscriptX does today

- Modular, dependency-aware analysis pipeline
- Speaker and interaction analysis
- Sentiment, emotion, NER, topics, similarity
- Structured, traceable outputs (JSON, CSV, visualisations)
- Voice prosody dashboards (per-speaker profiles, timelines, comparisons)
- Voice charts: pause/turn-delivery and rhythm indices (audio-gated)
- **Groups** — analyze multiple transcripts as a single unit (DB-backed, experimental)

Each analysis run writes structured artifacts under an outputs directory: per-run folders, manifests, and module subdirectories. Nothing is overwritten; outputs are indexed and traceable.

---

## Outputs you actually use

TranscriptX produces outputs meant to be *read*, *browsed*, and *thought with*:

- Clear visualisations (timelines, charts, networks, word clouds)
- Human-readable summaries and highlights
- Structured data (JSON, CSV) for deeper analysis or reuse
- Speaker-level and conversation-level views
- Group-level analysis across multiple transcripts

The web interface makes it easy to explore results interactively; the Python API supports scripted and repeatable workflows.

---

## Getting started

**Docker (recommended):** No local Python required. Build the image and run the web app — then open http://localhost:8501.

**Local install:** Python 3.10+. Core: `pip install transcriptx`. Full optional stack: `pip install transcriptx[full]`.

Configuration precedence: environment variables → run/draft override → project config → defaults.

---

## Product direction

TranscriptX is evolving toward a **personal audio analysis companion**. Long-term goals include analyzing personal recordings, voice note workflows, conversational analytics, and integration with local AI models. Tools like Plaud, Granola, and Otter address similar spaces, but TranscriptX is **local-first and modular** — your data stays on your machine, and the pipeline is yours to extend.

---

## Status & roadmap

**Current stage:** transcript analysis toolkit (beta).

Next phases:

1. Improved UX and stability
2. Richer analysis modules
3. Personal audio analysis workflows
4. Integration with local LLMs (Ollama)
5. Optional remote compute workflows (e.g. Colab)

TranscriptX is an active, evolving project. If you're curious, want to collaborate, or have a use case in mind, feel free to get in touch.
