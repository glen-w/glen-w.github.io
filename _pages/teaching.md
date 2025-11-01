---
layout: page
title: teaching
permalink: /teaching/
description:
nav: true
nav_order: 50
display_categories: [Sciences Po, International Ocean Institute, Miscellaneous]
horizontal: false
---

<div class="teaching">

{% if site.teaching and page.display_categories %}
{% for category in page.display_categories %}
<a id="{{ category }}" href=".#{{ category }}">
<h2 class="category">{{ category }}</h2>
</a>

    {% assign categorized_courses = site.teaching | where: "category", category %}
    {% if categorized_courses and categorized_courses != empty %}
      {% assign sorted_courses = categorized_courses | sort: "importance" %}
      <div class="row row-cols-1 row-cols-md-3">
        {% for course in sorted_courses %}
          {% include teaching.liquid course=course %}
        {% endfor %}
      </div>
    {% else %}
      <p>No courses found under "{{ category }}".</p>
    {% endif %}

{% endfor %}
{% else %}

  <p>No teaching data found. Make sure the <code>_teaching/</code> folder exists and is defined in <code>_config.yml</code>.</p>
{% endif %}

</div>
