---
title: creative
layout: page
permalink: /creative/
description: mostly collage (the original cut and paste, and the one true art form).
nav: true
nav_order: 60
display_categories: [collage]

# Optional: toggle these
enable_project_categories: true
horizontal: false
---

<div class="projects">
  {% if site.enable_project_categories and page.display_categories %}
    <!-- Categorized display -->
    {% for category in page.display_categories %}
    <a id="{{ category }}" href=".#{{ category }}">
      <h2 class="category">{{ category }}</h2>
    </a>
    {% assign categorized_projects = site.creative | where: "category", category %}
    {% assign sorted_projects = categorized_projects | sort: "importance" %}
    {% if page.horizontal %}
    <div class="container">
      <div class="row row-cols-1 row-cols-md-2">
      {% for project in sorted_projects %}
        {% include projects_horizontal.liquid %}
      {% endfor %}
      </div>
    </div>
    {% else %}
    <div class="row row-cols-1 row-cols-md-3">
      {% for project in sorted_projects %}
        {% include projects.liquid %}
      {% endfor %}
    </div>
    {% endif %}
    {% endfor %}
  {% else %}
    <!-- Un-categorized display -->
    {% assign sorted_projects = site.creative | sort: "importance" %}
    {% if page.horizontal %}
    <div class="container">
      <div class="row row-cols-1 row-cols-md-2">
      {% for project in sorted_projects %}
        {% include projects_horizontal.liquid %}
      {% endfor %}
      </div>
    </div>
    {% else %}
    <div class="row row-cols-1 row-cols-md-3">
      {% for project in sorted_projects %}
        {% include projects.liquid %}
      {% endfor %}
    </div>
    {% endif %}
  {% endif %}
</div>

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0" >
        {% include figure.liquid loading="eager" path="assets/img/collage/with_or_without_you.jpg" class="img-fluid rounded z-depth-1"  zoomable=true %}
        <div class="caption">
          With or without you
      </div>
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/7.jpg" class="img-fluid rounded z-depth-1" %}
    </div>
</div>

Images can be made zoomable.
Simply add `data-zoomable` to `<img>` tags that you want to make zoomable.
<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/collage/with_or_without_you.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/collage/with_or_without_you.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
The rest of the images in this post are all zoomable, arranged into different mini-galleries.
<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid path="assets/img/collage/with_or_without_you.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid path="assets/img/collage/with_or_without_you.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid path="assets/img/collage/with_or_without_you.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>