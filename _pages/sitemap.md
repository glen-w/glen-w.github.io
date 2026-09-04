---
layout: page
title: sitemap
permalink: /sitemap/
description: A map of the main sections of glenwright.earth.
nav: false
---

A short index of this site. Search engines can also use the [XML sitemap]({{ '/sitemap.xml' | relative_url }}).

## Main

- [home]({{ '/' | relative_url }})
- [library]({{ '/library/' | relative_url }})
- [projects]({{ '/projects/' | relative_url }})
  {%- assign project_rows = '' | split: '' %}
  {%- for project in site.projects %}
    {%- unless project.hidden %}
      {%- assign project_title = project.title | downcase %}
      {%- assign project_row = project_title | append: '::' | append: project.url %}
      {%- assign project_rows = project_rows | push: project_row %}
    {%- endunless %}
  {%- endfor %}
  {%- assign project_rows = project_rows | sort %}
  {%- for project_row in project_rows %}
    {%- assign project_parts = project_row | split: '::' %}
  - [{{ project_parts[0] }}]({{ project_parts[1] | relative_url }})
  {%- endfor %}
- [code]({{ '/code/' | relative_url }})
- [creative]({{ '/creative/' | relative_url }})
  - [collage]({{ '/creative/' | relative_url }}#collage)
  - [poems]({{ '/creative/' | relative_url }}#poems)
- [cv]({{ '/cv/' | relative_url }})

## More

- [bookshelf]({{ '/books/' | relative_url }})
- [jingle]({{ '/jingle/' | relative_url }})
- [map]({{ '/map.html' | relative_url }})
