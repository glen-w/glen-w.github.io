---
layout: page
permalink: /citations/
title: citations
nav: false
citations: true
---

<p class="citations-nav">
  <a href="{{ '/collaborators/' | relative_url }}">Co-author map</a>
  ·
  <a href="{{ '/library/' | relative_url }}">Library</a>
</p>

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

<style>
.citations-nav,
.citations-missing {
  max-width: 42rem;
  color: var(--global-text-color-light);
}

.citations-nav {
  margin: 0 0 1.25rem;
}

.citations-nav a {
  color: var(--global-theme-color);
}

.citations-app {
  margin: 1rem 0 2rem;
}

.citations-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
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

.citations-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.95rem;
  cursor: pointer;
  user-select: none;
}

.citations-status {
  margin: 0;
  font-size: 0.9rem;
  color: var(--global-text-color-light);
}

.citations-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(14rem, 18rem);
  gap: 1rem;
  align-items: stretch;
  min-height: 28rem;
}

.citations-canvas-wrap {
  border: 1px solid var(--global-divider-color);
  background: var(--global-bg-color);
  min-height: 28rem;
  overflow: hidden;
}

.citations-canvas {
  width: 100%;
  height: 100%;
  min-height: 28rem;
  display: block;
  cursor: grab;
  touch-action: none;
}

.citations-canvas:active {
  cursor: grabbing;
}

.citations-panel {
  border: 1px solid var(--global-divider-color);
  padding: 0.9rem 1rem;
  font-size: 0.95rem;
  overflow: auto;
  max-height: 32rem;
}

.citations-panel-empty {
  margin: 0;
  color: var(--global-text-color-light);
}

.citations-panel h3 {
  margin: 0 0 0.5rem;
  font-size: 1.05rem;
}

.citations-panel .meta {
  margin: 0 0 0.75rem;
  color: var(--global-text-color-light);
  font-size: 0.9rem;
}

.citations-panel ul {
  margin: 0;
  padding-left: 1.1rem;
}

.citations-panel li {
  margin: 0.35rem 0;
}

.citations-panel a {
  color: var(--global-theme-color);
}

.citers-list {
  margin-top: 2rem;
  max-width: 40rem;
}

.citers-list h2 {
  font-size: 1.25rem;
  margin-bottom: 0.35rem;
}

.citers-count {
  color: var(--global-text-color-light);
  font-size: 0.9rem;
}

@media (max-width: 767.98px) {
  .citations-layout {
    grid-template-columns: 1fr;
    min-height: 0;
  }

  .citations-canvas-wrap,
  .citations-canvas {
    min-height: 22rem;
  }

  .citations-panel {
    max-height: none;
    min-height: 10rem;
  }
}
</style>
