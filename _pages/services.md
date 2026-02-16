---
layout: services
title: services
permalink: /services/
description:
nav: false # temporarily hidden from navbar
nav_order: 75
---

<!-- pages/services.md -->
<div class="services">
{% assign sorted_services = site.services | sort: "importance" %}

  <!-- Generate rows for each service -->
  <div class="container">
    {% for service in sorted_services %}
      {% include services.liquid %}
    {% endfor %}
  </div>
</div>










