---
layout: page
permalink: /code/
title: code
description:
nav: true
nav_order: 35
---

{% include repository/contributions.liquid %}

{% if site.data.repositories.github_repos %}
{% assign sorted_repos = site.data.repositories.github_repos | sort_natural: "name" %}

<div class="repositories">
  {% for repo in sorted_repos %}
    {% include repository/repo.liquid repository=repo %}
  {% endfor %}
</div>
{% endif %}
