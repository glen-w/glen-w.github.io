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
<div class="repositories">
  {% for repo in site.data.repositories.github_repos %}
    {% include repository/repo.liquid repository=repo %}
  {% endfor %}
</div>
{% endif %}
