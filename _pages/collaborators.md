---
layout: page
permalink: /collaborators/
title: collaborators
description: People Glen Wright has published with, drawn from the library catalogue. Node size is shared works; colour is the first year of collaboration.
nav: false
coauthors: true
---

<p class="collaborators-intro">
  A map of co-authors from the
  <a href="{{ '/library/' | relative_url }}">library</a>.
  Each person is someone Glen has published with; thicker lines mean more shared works.
  Occasional collaborators (a single shared piece) are hidden until you ask for them.
  For who cites whom, see the
  <a href="{{ '/citations/' | relative_url }}">citation map</a>.
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
{% else %}
<noscript>
  <p>Turn on JavaScript to explore the graph, or regenerate the catalogue so <code>collaborators.yml</code> is written.</p>
</noscript>
{% endif %}

<style>
.collaborators-intro {
  max-width: 40rem;
  margin-bottom: 1.25rem;
  color: var(--global-text-color-light);
}

.coauthors-app {
  margin: 1rem 0 2rem;
}

.coauthors-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.coauthors-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.95rem;
  cursor: pointer;
  user-select: none;
}

.coauthors-status {
  margin: 0;
  font-size: 0.9rem;
  color: var(--global-text-color-light);
}

.coauthors-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(14rem, 18rem);
  gap: 1rem;
  align-items: stretch;
  min-height: 28rem;
}

.coauthors-canvas-wrap {
  border: 1px solid var(--global-divider-color);
  background: var(--global-bg-color);
  min-height: 28rem;
  overflow: hidden;
}

.coauthors-canvas {
  width: 100%;
  height: 100%;
  min-height: 28rem;
  display: block;
  cursor: grab;
  touch-action: none;
}

.coauthors-canvas:active {
  cursor: grabbing;
}

.coauthors-panel {
  border: 1px solid var(--global-divider-color);
  padding: 0.9rem 1rem;
  font-size: 0.95rem;
  overflow: auto;
  max-height: 32rem;
}

.coauthors-panel-empty {
  margin: 0;
  color: var(--global-text-color-light);
}

.coauthors-panel h3 {
  margin: 0 0 0.5rem;
  font-size: 1.05rem;
}

.coauthors-panel .meta {
  margin: 0 0 0.75rem;
  color: var(--global-text-color-light);
  font-size: 0.9rem;
}

.coauthors-panel ul {
  margin: 0;
  padding-left: 1.1rem;
}

.coauthors-panel li {
  margin: 0.35rem 0;
}

.coauthors-panel a {
  color: var(--global-theme-color);
}

.collaborators-list {
  margin-top: 2rem;
  max-width: 40rem;
}

.collaborators-list h2 {
  font-size: 1.25rem;
  margin-bottom: 0.35rem;
}

.collaborators-list ul {
  padding-left: 1.2rem;
}

.collaborators-count {
  color: var(--global-text-color-light);
  font-size: 0.9rem;
}

@media (max-width: 767.98px) {
  .coauthors-layout {
    grid-template-columns: 1fr;
    min-height: 0;
  }

  .coauthors-canvas-wrap,
  .coauthors-canvas {
    min-height: 22rem;
  }

  .coauthors-panel {
    max-height: none;
    min-height: 10rem;
  }
}
</style>
