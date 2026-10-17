---
layout: services
title: services
permalink: /services/
description: Ocean & marine policy, evidence & research ops, and workshops & facilitation for ocean, energy and climate teams.
nav: true
nav_order: 72
---

<!-- pages/services.md -->
<div class="services">
{% assign sorted_services = site.services | sort: "importance" %}

  <div class="container">
    {% for service in sorted_services %}
      {% include services.liquid %}
    {% endfor %}
  </div>
</div>

<div class="contact-actions contact-actions--center">
  <a class="contact-actions__link" href="https://meet.glenwright.earth/u/book/meeting">Schedule a meeting</a>
</div>
