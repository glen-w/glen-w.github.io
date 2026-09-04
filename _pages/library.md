---
layout: page
permalink: /library/
title: library
description:
nav: true
nav_order: 10
medium_zoom: true
---

<div
  id="libraryApp"
  data-catalog="{{ '/assets/json/library.json' | relative_url | bust_file_cache }}"
  data-details="{{ '/assets/json/library-details.json' | relative_url | bust_file_cache }}"
>
  <div class="library-search">
    <label for="bibsearch" class="sr-only">Filter publications</label>
    <input
      type="search"
      id="bibsearch"
      class="search bibsearch-form-input"
      spellcheck="false"
      autocomplete="off"
      placeholder="Type to filter"
    >
  </div>

  <div class="search-actions">
    <a href="/library/" id="clearFiltersLink" class="clear-filters-link">
      <i class="fas fa-times" aria-hidden="true"></i> Clear filters
    </a>
  </div>

  <div class="library-filters">
    <h4>filter</h4>

    <div class="filter-group entry-type-filters">
      <div class="filter-group-title" id="filter-type-label">type</div>
      <div class="filter-tags" role="group" aria-labelledby="filter-type-label">
        {% for entry_type in site.data.dynamic_filters.entry_types %}
          {% assign count = site.data.dynamic_filters.entry_type_counts[entry_type] | default: 0 %}
          {% if count > 0 %}
            <button type="button" class="badge badge-light" data-filter="{{ entry_type }}" data-kind="type" aria-pressed="false">{{ entry_type }} ({{ count }})</button>
          {% endif %}
        {% endfor %}
      </div>
    </div>

    <div class="filter-group role-tags-filters">
      <div class="filter-group-title" id="filter-role-label">role</div>
      <div class="filter-tags" role="group" aria-labelledby="filter-role-label">
        {% for role_tag in site.data.dynamic_filters.role_tags %}
          {% assign count = site.data.dynamic_filters.role_tag_counts[role_tag] | default: 0 %}
          {% if count > 0 %}
            <button type="button" class="tag" data-filter="{{ role_tag }}" data-kind="role" aria-pressed="false">{{ role_tag }} ({{ count }})</button>
          {% endif %}
        {% endfor %}
      </div>
    </div>

    <div class="filter-group language-tags-filters">
      <div class="filter-group-title" id="filter-lang-label">language</div>
      <div class="filter-tags" role="group" aria-labelledby="filter-lang-label">
        {% for language_tag in site.data.dynamic_filters.language_tags %}
          {% assign count = site.data.dynamic_filters.language_tag_counts[language_tag] | default: 0 %}
          {% if count > 0 %}
            <button type="button" class="tag" data-filter="{{ language_tag }}" data-kind="lang" aria-pressed="false">{{ language_tag }} ({{ count }})</button>
          {% endif %}
        {% endfor %}
      </div>
    </div>

    <div class="filter-actions">
      <button type="button" class="view-map-link" id="mapToggleBtn" aria-pressed="false">
        <i class="fas fa-map-marker-alt" aria-hidden="true"></i> view map
      </button>
      <button type="button" class="view-map-link" id="selectedToggleBtn" aria-pressed="false">
        <i class="fas fa-eye" aria-hidden="true"></i> show selected publications
      </button>
    </div>
  </div>

  <div id="libraryMapContainer" class="library-map-container" style="display: none;">
    <div id="libraryMap" class="library-map" role="region" aria-label="Publication locations"></div>
  </div>

  <div id="itemCountDisplay" class="item-count-display" style="display: none;" aria-live="polite">
    <span id="itemCountText">showing 0 items</span>
  </div>

  <noscript>
    <p>This catalogue needs JavaScript to filter and search. Selected works:</p>
    <ul>
      {% for item in site.data.library_selected %}
        <li>
          {% if item.url %}
            <a href="{{ item.url }}">{{ item.title }}</a>
          {% elsif item.pdf %}
            <a href="{{ item.pdf | relative_url }}">{{ item.title }}</a>
          {% else %}
            {{ item.title }}
          {% endif %}
          {% if item.year %} ({{ item.year }}){% endif %}
        </li>
      {% endfor %}
    </ul>
    <p><a href="https://github.com/glen-w/glen-w.github.io/blob/master/_bibliography/papers.bib">Full bibliography on GitHub</a></p>
  </noscript>

  <div id="libraryResults" class="publications" aria-busy="true" aria-live="polite">
    <p id="libraryStatus" class="library-status">Loading catalogue…</p>
  </div>
</div>

<script defer src="{{ '/assets/js/library.js' | relative_url | bust_file_cache }}"></script>

<style>
.library-map-container {
  margin: 2rem 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border: 1px solid #e0e0e0;
}

.library-map {
  height: 400px;
  width: 100%;
}

.filter-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.search-actions {
  margin: 1rem 0;
  text-align: left;
}

.library-search {
  margin: 1rem 0;
}

.clear-filters-link,
.view-map-link {
  color: var(--global-text-color);
  text-decoration: none;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: none;
  border: 0;
  padding: 0;
  font: inherit;
  cursor: pointer;
}

.clear-filters-link:hover,
.view-map-link:hover {
  color: var(--global-theme-color);
  text-decoration: none;
}

.filter-group {
  margin-bottom: 0.75rem;
}

.filter-group.entry-type-filters,
.filter-group.role-tags-filters {
  margin-bottom: 1rem;
}

.filter-group.language-tags-filters {
  margin-bottom: 0.75rem;
}

.filter-group-title {
  color: var(--global-text-color);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.library-filters .filter-tags {
  gap: 0 !important;
  row-gap: 0 !important;
}

.library-filters .filter-tags button {
  font: inherit;
  line-height: inherit;
}

.library-filters .filter-tags .badge,
.library-filters .filter-tags .tag {
  cursor: pointer;
  user-select: none;
  text-decoration: none;
  color: inherit;
  background-color: transparent !important;
  box-shadow: none !important;
  margin-right: 0.3rem !important;
  margin-bottom: 0.3rem !important;
  padding: 0.2rem 0.35rem;
  font-size: 0.8rem;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.library-filters .filter-tags .badge:hover,
.library-filters .filter-tags .tag:hover,
.library-filters .filter-tags .badge:focus-visible,
.library-filters .filter-tags .tag:focus-visible {
  text-decoration: none;
  color: inherit;
  background-color: #dee2e6 !important;
  border-color: var(--global-theme-color) !important;
}

.library-filters .filter-tags .badge.active,
.library-filters .filter-tags .tag.active {
  background-color: #dee2e6 !important;
  color: var(--global-theme-color) !important;
  border-color: var(--global-theme-color) !important;
}

.library-filters .filter-tags .badge.badge-light {
  background-color: transparent !important;
  color: #495057 !important;
  border: 1px solid #dee2e6 !important;
}

.library-filters .filter-tags .badge.badge-light:hover,
.library-filters .filter-tags .badge.badge-light:focus-visible {
  background-color: #dee2e6 !important;
  border-color: var(--global-theme-color) !important;
}

.library-filters .filter-tags .badge.badge-light.active {
  background-color: #dee2e6 !important;
  color: var(--global-theme-color) !important;
  border-color: var(--global-theme-color) !important;
}

.publications img.preview {
  width: 80px;
  height: 107px;
  aspect-ratio: 3 / 4;
  object-fit: contain;
  object-position: center;
  display: block;
  box-sizing: border-box;
  background: var(--global-bg-color, #f5f5f5);
  border: 1px solid var(--global-divider-color, #dee2e6);
}

.publications .item-type-and-roles button,
.publications .all-tags button {
  font: inherit;
  cursor: pointer;
}

.publications .photos.hidden,
.publications .figures.hidden,
.publications .speakers.hidden,
.publications .quotes.hidden,
.publications .audio.hidden,
.publications .award.hidden {
  display: none;
}

.publications .photos.hidden.open,
.publications .figures.hidden.open,
.publications .speakers.hidden.open,
.publications .quotes.hidden.open,
.publications .audio.hidden.open,
.publications .award.hidden.open {
  display: block;
}

.marker-cluster {
  background-color: rgba(102, 187, 106, 0.7);
  border: 2px solid rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  color: white;
  height: 40px;
  line-height: 40px;
  text-align: center;
  width: 40px;
  font-weight: bold;
  font-size: 14px;
}

.marker-cluster-medium,
.marker-cluster-large {
  background-color: rgba(102, 187, 106, 0.7);
  color: white;
}

.cluster-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  font-weight: bold;
  font-size: 14px;
}

.item-count-display {
  margin: 1rem 0;
  padding: 0.75rem 1rem;
  background-color: var(--global-bg-color);
  border: 1px solid var(--global-border-color);
  border-radius: 0.375rem;
  font-size: 0.9rem;
  color: var(--global-text-color);
  text-align: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.item-count-display.show {
  display: block !important;
}

.library-map .leaflet-popup-content-wrapper {
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.library-map .popup-content {
  min-width: 250px;
}

.library-map .popup-title {
  font-size: 1.1rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 0.5rem;
  line-height: 1.3;
}

.library-map .popup-details {
  margin: 0.5rem 0;
}

.library-map .popup-detail {
  margin: 0.3rem 0;
  font-size: 0.9rem;
  color: #666;
}

.library-map .popup-detail i {
  width: 16px;
  color: #007bff;
}

.library-map .popup-link {
  display: inline-block;
  background: #007bff;
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.library-map .popup-link:hover {
  background: #0056b3;
  color: white;
  text-decoration: none;
}
</style>
