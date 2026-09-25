---
layout: page
title: catalogue of failures
permalink: /failures/
nav: false
nav_order: 60
_styles: |
  .failures-index { list-style: none; padding: 0; margin: 0; }
  .failures-index > li {
    display: grid;
    grid-template-columns: 3.2rem 1fr;
    gap: 0.75rem;
    padding: 0.85rem 0;
    border-bottom: 1px solid var(--global-divider-color, rgba(0,0,0,0.08));
  }
  .failures-year {
    font-variant-numeric: tabular-nums;
    color: var(--global-text-color-light, #666);
    padding-top: 0.15rem;
  }
  .failures-title { font-weight: 600; }
  .failures-role { display: block; font-weight: 400; }
  .failures-meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.35rem;
    margin-top: 0.35rem;
  }
  .failure-badge {
    font-size: 0.7rem;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    border: 1px solid currentColor;
    border-radius: 999px;
    padding: 0.05rem 0.45rem;
    line-height: 1.4;
  }
  .failure-badge--applied { color: var(--global-text-color-light, #666); }
  .failure-badge--interview { color: #1d4e89; }
  .failure-badge--offer { color: #1b7f4a; }
  .failure-badge--rejection { color: #9b3a3a; }
  .failure-badge--unknown { color: var(--global-text-color-light, #666); }
  .failures-meta .btn { margin: 0; }
  .failures-meta [aria-expanded="true"] { color: var(--global-theme-color, #0069d9); }
  .failure-panel {
    display: none;
    margin-top: 0.6rem;
    padding: 0.75rem 1rem;
    border: 1px dashed var(--global-text-color, #333);
    font-size: 0.9rem;
    text-align: justify;
  }
  .failure-panel.open { display: block; }
  .failure-panel p:last-child { margin-bottom: 0; }
---

<ol class="failures-index">
  {% assign cards = site.failures | sort: "year" | reverse %}
  {% for item in cards %}
    <li>
      <div class="failures-year">{{ item.year }}</div>
      <div>
        <a class="failures-title" href="{{ item.url | relative_url }}">{{ item.organisation }}</a>
        <span class="failures-role">{{ item.role }}</span>
        {% assign slug = item.relative_path | split: "/" | last | split: "." | first %}
        {% assign asset = "/assets/failures/" | append: slug %}
        <div class="failures-meta">
          <span class="failure-badge failure-badge--{{ item.outcome | default: 'unknown' }}">{{ item.outcome | default: "unknown" }}</span>
          {% if item.has_job_ad %}
            <a class="btn btn-sm z-depth-0" href="{{ asset | append: '/job-ad.md' | relative_url }}" title="Job ad" aria-label="Job ad"><i class="fa-solid fa-bullhorn" aria-hidden="true"></i></a>
          {% endif %}
          {% if item.has_cv and item.cv_file %}
            <a class="btn btn-sm z-depth-0" href="{{ asset | append: '/' | append: item.cv_file | relative_url }}" title="CV" aria-label="CV"><i class="fa-solid fa-id-card" aria-hidden="true"></i></a>
          {% endif %}
          {% if item.has_cover %}
            <a class="btn btn-sm z-depth-0" href="{{ asset | append: '/application.md' | relative_url }}" title="Cover letter" aria-label="Cover letter"><i class="fa-solid fa-envelope-open-text" aria-hidden="true"></i></a>
          {% endif %}
          {% if item.has_application %}
            <a class="btn btn-sm z-depth-0" href="{{ asset | append: '/application.md' | relative_url }}" title="Application" aria-label="Application"><i class="fa-solid fa-file-lines" aria-hidden="true"></i></a>
          {% endif %}
          {% if item.has_emails %}
            <a class="btn btn-sm z-depth-0" href="{{ asset | append: '/emails.md' | relative_url }}" title="Email thread" aria-label="Email thread"><i class="fa-solid fa-envelope" aria-hidden="true"></i></a>
          {% endif %}
          <button type="button" class="btn btn-sm z-depth-0" data-expand="summary" title="Summary" aria-label="Summary" aria-expanded="false"><i class="fa-solid fa-align-left" aria-hidden="true"></i></button>
          <button type="button" class="btn btn-sm z-depth-0" data-expand="reflection" title="Personal reflection" aria-label="Personal reflection" aria-expanded="false"><i class="fa-solid fa-pen" aria-hidden="true"></i></button>
        </div>
        <div class="failure-panel" data-panel="summary"><p>{{ item.summary }}</p></div>
        <div class="failure-panel" data-panel="reflection">{{ item.reflection | markdownify }}</div>
      </div>
    </li>
  {% endfor %}
</ol>

<script>
  document.querySelectorAll(".failures-index [data-expand]").forEach((button) => {
    button.addEventListener("click", () => {
      const item = button.closest("li");
      const panel = item.querySelector(`[data-panel="${button.dataset.expand}"]`);
      const willOpen = !panel.classList.contains("open");
      panel.classList.toggle("open", willOpen);
      button.setAttribute("aria-expanded", willOpen ? "true" : "false");
    });
  });
</script>
