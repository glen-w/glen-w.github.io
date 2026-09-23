---
layout: default
permalink: /network/
sitemap: false
title: network
nav: false
---

<script>
  (function () {
    var hash = (window.location.hash || "").toLowerCase();
    var target = "{{ '/library/' | relative_url }}";
    if (hash.indexOf("#citations") === 0) target += "#citations";
    else if (hash.indexOf("#timeline") === 0) target += "#timeline";
    else if (hash.indexOf("#co-author") === 0 || hash.indexOf("#coauthor") === 0) target += "#co-authors";
    else target += "#explore";
    window.location.replace(target);
  })();
</script>

<p>Moved to <a href="{{ '/library/' | relative_url }}#explore">the library</a>.</p>
