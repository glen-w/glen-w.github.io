---
layout: page
permalink: /network/
title: network
description: Co-author and citation networks, plus a career timeline, drawn from the library catalogue.
nav: false
network: true
---

<p class="network-intro">
  Networks built from the
  <a href="{{ '/library/' | relative_url }}">library</a>.
  Use the tabs to switch between co-authors, citations, and a timeline of the catalogue by year.
</p>

<div id="networkApp" class="network-app">
  <div class="network-tabs" role="tablist" aria-label="Publication networks">
    <button
      type="button"
      class="network-tab is-active"
      role="tab"
      id="network-tab-coauthors"
      aria-controls="network-panel-coauthors"
      aria-selected="true"
      data-tab="coauthors"
    >
      Co-authors
    </button>
    <button
      type="button"
      class="network-tab"
      role="tab"
      id="network-tab-citations"
      aria-controls="network-panel-citations"
      aria-selected="false"
      data-tab="citations"
    >
      Citations
    </button>
    <button
      type="button"
      class="network-tab"
      role="tab"
      id="network-tab-timeline"
      aria-controls="network-panel-timeline"
      aria-selected="false"
      data-tab="timeline"
    >
      Timeline
    </button>
  </div>

  <div
    role="tabpanel"
    id="network-panel-coauthors"
    class="network-panel"
    data-tab="coauthors"
    aria-labelledby="network-tab-coauthors"
  >
    <p class="network-panel-intro">
      Each person is someone Glen has published with; thicker lines mean more shared works.
      Occasional collaborators (a single shared piece) are hidden until you ask for them.
    </p>

    <div
      id="coauthorsApp"
      class="coauthors-app"
      data-graph="{{ '/assets/json/coauthors.json' | relative_url | bust_file_cache }}"
    >
      <div class="coauthors-toolbar">
        <label class="coauthors-toggle">
          <input type="checkbox" id="coauthorsShowOccasional" />
          Show occasional collaborators
        </label>
        <p id="coauthorsStatus" class="coauthors-status" aria-live="polite"></p>
      </div>

      <div class="coauthors-layout">
        <div class="coauthors-canvas-wrap" aria-hidden="false">
          <svg id="coauthorsCanvas" class="coauthors-canvas" role="img" aria-label="Co-author collaboration graph"></svg>
        </div>
        <aside id="coauthorsPanel" class="coauthors-panel" aria-live="polite">
          <p class="coauthors-panel-empty">Click a person or a link between people to see the shared works.</p>
        </aside>
      </div>
    </div>

    {% if site.data.collaborators and site.data.collaborators.size > 0 %}
    <section class="collaborators-list" aria-labelledby="collaborators-list-heading">
      <h2 id="collaborators-list-heading">Frequent collaborators</h2>
      <p>People with at least two shared works. Open a name in the library filter.</p>
      <ul>
        {% for person in site.data.collaborators %}
          <li>
            <a href="{{ '/library/' | relative_url }}#{{ person.name | url_encode | replace: '+', '%20' }}">{{ person.name }}</a>
            <span class="collaborators-count">({{ person.count }})</span>
          </li>
        {% endfor %}
      </ul>
    </section>
    {% endif %}
  </div>

  <div
    role="tabpanel"
    id="network-panel-citations"
    class="network-panel"
    data-tab="citations"
    aria-labelledby="network-tab-citations"
    hidden
  >
    <div
      id="citationsApp"
      class="citations-app"
      data-graph="{{ '/assets/json/citations.json' | relative_url | bust_file_cache }}"
    >
      <div class="citations-toolbar">
        <div class="citations-filters" role="group" aria-label="Citation direction">
          <button type="button" class="citations-filter is-active" data-direction="both" aria-pressed="true">Both</button>
          <button type="button" class="citations-filter" data-direction="cites_me" aria-pressed="false">Citing me</button>
          <button type="button" class="citations-filter" data-direction="i_cite" aria-pressed="false">I cite</button>
        </div>
        <label class="citations-toggle">
          <input type="checkbox" id="citationsShowOccasional" />
          Show occasional links
        </label>
        <p id="citationsStatus" class="citations-status" aria-live="polite"></p>
      </div>

      <div class="citations-layout">
        <div class="citations-canvas-wrap">
          <svg id="citationsCanvas" class="citations-canvas" role="img" aria-label="Author citation network"></svg>
        </div>
        <aside id="citationsPanel" class="citations-panel" aria-live="polite">
          <p class="citations-panel-empty">Click a person or an arrow to see the papers behind the link.</p>
        </aside>
      </div>
    </div>

    {% if site.data.citers and site.data.citers.size > 0 %}
    <section class="citers-list" aria-labelledby="citers-list-heading">
      <h2 id="citers-list-heading">Frequent citers</h2>
      <p>Authors who cite Glen’s work at least twice.</p>
      <ul>
        {% for person in site.data.citers %}
          <li>
            <span class="citers-name">{{ person.name }}</span>
            <span class="citers-count">({{ person.count }})</span>
          </li>
        {% endfor %}
      </ul>
    </section>
    {% else %}
    <p class="citations-missing">
      No citation graph yet. Run
      <code>PYTHONPATH=. python processing/library/citations.py</code>
      then rebuild the site.
    </p>
    {% endif %}
  </div>

  <div
    role="tabpanel"
    id="network-panel-timeline"
    class="network-panel"
    data-tab="timeline"
    aria-labelledby="network-tab-timeline"
    hidden
  >
    <p class="network-panel-intro">
      Catalogue items by year. Bars stack by kind of work; switch to role to see the primary role on each item.
      Drag the lower chart to focus a span of years.
    </p>

    <div
      id="timelineApp"
      class="timeline-app"
      data-catalog="{{ '/assets/json/library.json' | relative_url | bust_file_cache }}"
    >
      <div class="timeline-toolbar">
        <div class="timeline-modes" role="group" aria-label="Stack by">
          <button type="button" class="timeline-mode is-active" data-mode="type" aria-pressed="true">Type</button>
          <button type="button" class="timeline-mode" data-mode="role" aria-pressed="false">Role</button>
        </div>
        <label class="timeline-range">
          From
          <select id="timelineFrom" aria-label="From year"></select>
        </label>
        <label class="timeline-range">
          To
          <select id="timelineTo" aria-label="To year"></select>
        </label>
        <p id="timelineStatus" class="timeline-status" aria-live="polite"></p>
      </div>

      <div class="timeline-layout">
        <div class="timeline-canvas-wrap">
          <svg id="timelineCanvas" class="timeline-canvas" role="img" aria-label="Career timeline of library items by year"></svg>
          <svg id="timelineContext" class="timeline-context" role="img" aria-label="Year range brush"></svg>
        </div>
        <aside id="timelinePanel" class="timeline-panel" aria-live="polite">
          <p class="timeline-panel-empty">Click a bar to see the works in that year.</p>
        </aside>
      </div>
      <ul id="timelineLegend" class="timeline-legend"></ul>
    </div>
  </div>

  <script>
    (function () {
      var hash = window.location.hash.toLowerCase();
      var initial = hash.indexOf("#citations") === 0
        ? "citations"
        : hash.indexOf("#timeline") === 0
          ? "timeline"
          : "coauthors";
      var tabs = document.querySelectorAll("#networkApp .network-tab");
      var panels = document.querySelectorAll("#networkApp .network-panel");
      tabs.forEach(function (tab) {
        var active = tab.dataset.tab === initial;
        tab.classList.toggle("is-active", active);
        tab.setAttribute("aria-selected", active ? "true" : "false");
      });
      panels.forEach(function (panel) {
        panel.hidden = panel.dataset.tab !== initial;
      });
    })();
  </script>
</div>

<style>
.network-intro {
  max-width: 42rem;
  margin-bottom: 1.25rem;
  color: var(--global-text-color-light);
}

.network-tabs {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid var(--global-divider-color);
  padding-bottom: 0.5rem;
}

.network-tab {
  border: 1px solid transparent;
  border-bottom: none;
  background: transparent;
  color: var(--global-text-color-light);
  font: inherit;
  font-size: 0.95rem;
  padding: 0.35rem 0.75rem;
  cursor: pointer;
  margin-bottom: -1px;
}

.network-tab.is-active {
  border-color: var(--global-divider-color);
  border-bottom-color: var(--global-bg-color);
  color: var(--global-theme-color);
}

.network-panel-intro {
  max-width: 40rem;
  margin: 0 0 1rem;
  color: var(--global-text-color-light);
}

.coauthors-app,
.citations-app {
  margin: 0 0 2rem;
}

.coauthors-toolbar,
.citations-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.coauthors-toggle,
.citations-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.95rem;
  cursor: pointer;
  user-select: none;
}

.coauthors-status,
.citations-status {
  margin: 0;
  font-size: 0.9rem;
  color: var(--global-text-color-light);
}

.coauthors-layout,
.citations-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(14rem, 18rem);
  gap: 1rem;
  align-items: stretch;
  min-height: 28rem;
}

.coauthors-canvas-wrap,
.citations-canvas-wrap {
  border: 1px solid var(--global-divider-color);
  background: var(--global-bg-color);
  min-height: 28rem;
  overflow: hidden;
}

.coauthors-canvas,
.citations-canvas {
  width: 100%;
  height: 100%;
  min-height: 28rem;
  display: block;
  cursor: grab;
  touch-action: none;
}

.coauthors-canvas:active,
.citations-canvas:active {
  cursor: grabbing;
}

.coauthors-panel,
.citations-panel {
  border: 1px solid var(--global-divider-color);
  padding: 0.9rem 1rem;
  font-size: 0.95rem;
  overflow: auto;
  max-height: 32rem;
}

.coauthors-panel-empty,
.citations-panel-empty {
  margin: 0;
  color: var(--global-text-color-light);
}

.coauthors-panel h3,
.citations-panel h3 {
  margin: 0 0 0.5rem;
  font-size: 1.05rem;
}

.coauthors-panel .meta,
.citations-panel .meta {
  margin: 0 0 0.75rem;
  color: var(--global-text-color-light);
  font-size: 0.9rem;
}

.coauthors-panel ul,
.citations-panel ul {
  margin: 0;
  padding-left: 1.1rem;
}

.coauthors-panel li,
.citations-panel li {
  margin: 0.35rem 0;
}

.coauthors-panel a,
.citations-panel a {
  color: var(--global-theme-color);
}

.citations-filters {
  display: inline-flex;
  gap: 0.35rem;
}

.citations-filter {
  border: 1px solid var(--global-divider-color);
  background: transparent;
  color: var(--global-text-color);
  font: inherit;
  font-size: 0.9rem;
  padding: 0.25rem 0.6rem;
  cursor: pointer;
}

.citations-filter.is-active {
  border-color: var(--global-theme-color);
  color: var(--global-theme-color);
}

.collaborators-list,
.citers-list {
  margin-top: 0.5rem;
  max-width: 40rem;
}

.collaborators-list h2,
.citers-list h2 {
  font-size: 1.25rem;
  margin-bottom: 0.35rem;
}

.collaborators-list ul {
  padding-left: 1.2rem;
}

.collaborators-count,
.citers-count {
  color: var(--global-text-color-light);
  font-size: 0.9rem;
}

.citations-missing {
  max-width: 42rem;
  color: var(--global-text-color-light);
}

.timeline-app {
  margin: 0 0 2rem;
}

.timeline-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.timeline-modes {
  display: inline-flex;
  gap: 0.35rem;
}

.timeline-mode {
  border: 1px solid var(--global-divider-color);
  background: transparent;
  color: var(--global-text-color);
  font: inherit;
  font-size: 0.9rem;
  padding: 0.25rem 0.6rem;
  cursor: pointer;
}

.timeline-mode.is-active {
  border-color: var(--global-theme-color);
  color: var(--global-theme-color);
}

.timeline-range {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.9rem;
}

.timeline-range select {
  font: inherit;
  font-size: 0.9rem;
  color: var(--global-text-color);
  background: var(--global-bg-color);
  border: 1px solid var(--global-divider-color);
  padding: 0.15rem 0.35rem;
}

.timeline-status {
  margin: 0;
  font-size: 0.9rem;
  color: var(--global-text-color-light);
}

.timeline-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(14rem, 18rem);
  gap: 1rem;
  align-items: stretch;
}

.timeline-canvas-wrap {
  border: 1px solid var(--global-divider-color);
  background: var(--global-bg-color);
  min-height: 22rem;
  padding: 0.5rem 0.5rem 0.25rem;
}

.timeline-canvas {
  width: 100%;
  height: 18rem;
  display: block;
}

.timeline-context {
  width: 100%;
  height: 3.25rem;
  display: block;
  touch-action: none;
}

.timeline-panel {
  border: 1px solid var(--global-divider-color);
  padding: 0.9rem 1rem;
  font-size: 0.95rem;
  overflow: auto;
  max-height: 28rem;
}

.timeline-panel-empty {
  margin: 0;
  color: var(--global-text-color-light);
}

.timeline-panel h3 {
  margin: 0 0 0.5rem;
  font-size: 1.05rem;
}

.timeline-panel .meta,
.timeline-panel .timeline-links {
  margin: 0 0 0.75rem;
  color: var(--global-text-color-light);
  font-size: 0.9rem;
}

.timeline-panel ul {
  margin: 0;
  padding-left: 1.1rem;
}

.timeline-panel li {
  margin: 0.35rem 0;
}

.timeline-panel a {
  color: var(--global-theme-color);
}

.timeline-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem 0.9rem;
  list-style: none;
  margin: 0.75rem 0 0;
  padding: 0;
}

.timeline-legend button {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border: 0;
  background: transparent;
  color: var(--global-text-color);
  font: inherit;
  font-size: 0.85rem;
  padding: 0;
  cursor: pointer;
}

.timeline-swatch {
  width: 0.7rem;
  height: 0.7rem;
  display: inline-block;
}

.timeline-brush .selection {
  fill: var(--global-theme-color);
  fill-opacity: 0.18;
  stroke: var(--global-theme-color);
}

.timeline-brush .handle {
  fill: var(--global-theme-color);
}

@media (max-width: 767.98px) {
  .coauthors-layout,
  .citations-layout,
  .timeline-layout {
    grid-template-columns: 1fr;
    min-height: 0;
  }

  .coauthors-canvas-wrap,
  .coauthors-canvas,
  .citations-canvas-wrap,
  .citations-canvas {
    min-height: 22rem;
  }

  .coauthors-panel,
  .citations-panel,
  .timeline-panel {
    max-height: none;
    min-height: 10rem;
  }
}
</style>
