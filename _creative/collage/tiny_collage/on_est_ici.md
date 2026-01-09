---
layout: page
title: "on est ici"
img: assets/img/collage/tiny_collage/on_est_ici.jpg
description:
category: collage
importance: 2

---

{% if page.img %}
{% include figure.liquid loading="eager" path=page.img class="img-fluid rounded z-depth-1" %}
{% endif %}
