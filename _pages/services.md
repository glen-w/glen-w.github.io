---
layout: services
title: services
permalink: /services/
description: Ocean & marine policy, evidence & research ops, and workshops & facilitation for ocean, energy and climate teams.
nav: true
nav_order: 72
---

<!-- pages/services.md -->
<div class="contact-actions contact-actions--lead" markdown="1">

[Schedule a meeting](https://meet.glenwright.earth){: .contact-actions__link }

</div>

<div class="services">
{% assign sorted_services = site.services | sort: "importance" %}

  <div class="container">
    {% for service in sorted_services %}
      {% include services.liquid %}
    {% endfor %}
  </div>
</div>
