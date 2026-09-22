---
layout: page
permalink: /code/
title: code
description:
nav: true
nav_order: 35
---

{% include repository/contributions.liquid %}

Public repositories. Some are local-first tools you run yourself; some are sites or notes. The graph above is recent activity, not a ranking. Each card links the repository, plus the live site and the docs when those exist.

{% if site.data.repositories.github_repos %}
{% assign sorted_repos = site.data.repositories.github_repos | sort_natural: "name" %}

<div class="repositories">
  {% for repo in sorted_repos %}
    {% include repository/repo.liquid repository=repo %}
  {% endfor %}
</div>
{% endif %}
