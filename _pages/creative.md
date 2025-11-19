---
title: creative
layout: page
permalink: /creative/
description:
nav: true
nav_order: 60
display_categories: [collage,poems]

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
    
    <!-- Separate projects with series from those without -->
    {% assign projects_with_series = categorized_projects | where_exp: "item", "item.series != nil and item.series != ''" %}
    {% assign projects_without_series = categorized_projects | where_exp: "item", "item.series == nil or item.series == ''" %}
    
    <!-- Group projects by series and sort series alphabetically -->
    {% assign grouped_by_series = projects_with_series | group_by: "series" | sort: "name" %}
    
    <!-- Display projects grouped by series -->
    {% for series_group in grouped_by_series %}
      <h3 class="series">{{ series_group.name }}</h3>
      {% assign series_projects = series_group.items | sort: "importance" %}
      {% if page.horizontal %}
      <div class="container">
        <div class="row row-cols-1 row-cols-md-2">
        {% for project in series_projects %}
          {% include projects_creative_horizontal.liquid %}
        {% endfor %}
        </div>
      </div>
      {% else %}
      <div class="row row-cols-1 row-cols-md-3">
        {% for project in series_projects %}
          {% include projects_creative.liquid %}
        {% endfor %}
      </div>
      {% endif %}
    {% endfor %}
    
    <!-- Display projects without series under "misc." -->
    {% if projects_without_series.size > 0 %}
      <h3 class="series">misc.</h3>
      {% assign misc_projects = projects_without_series | sort: "importance" %}
      {% if page.horizontal %}
      <div class="container">
        <div class="row row-cols-1 row-cols-md-2">
        {% for project in misc_projects %}
          {% include projects_creative_horizontal.liquid %}
        {% endfor %}
        </div>
      </div>
      {% else %}
      <div class="row row-cols-1 row-cols-md-3">
        {% for project in misc_projects %}
          {% include projects_creative.liquid %}
        {% endfor %}
      </div>
      {% endif %}
    {% endif %}
    
    {% endfor %}
  {% else %}
    <!-- Un-categorized display -->
    {% assign sorted_projects = site.creative | sort: "importance" %}
    {% if page.horizontal %}
    <div class="container">
      <div class="row row-cols-1 row-cols-md-2">
      {% for project in sorted_projects %}
        {% include projects_creative_horizontal.liquid %}
      {% endfor %}
      </div>
    </div>
      {% else %}
      <div class="row row-cols-1 row-cols-md-3">
        {% for project in sorted_projects %}
          {% include projects_creative.liquid %}
        {% endfor %}
      </div>
      {% endif %}
  {% endif %}
</div>




{% comment %}
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
{% endcomment %}

<script>
// Wait for both DOM and deferred scripts to load
window.addEventListener('load', function() {
  // Polyfills for IE11 compatibility
  if (!Element.prototype.matches) {
    Element.prototype.matches = Element.prototype.msMatchesSelector || Element.prototype.webkitMatchesSelector;
  }
  
  if (!Element.prototype.closest) {
    Element.prototype.closest = function(s) {
      var el = this;
      do {
        if (Element.prototype.matches.call(el, s)) return el;
        el = el.parentElement || el.parentNode;
      } while (el !== null && el.nodeType === 1);
      return null;
    };
  }
  
  // Initialize creative gallery functionality
  // Select img elements with the creative-gallery-image class (class is on img itself)
  var galleryImages = document.querySelectorAll('img.creative-gallery-image');
  
  galleryImages.forEach(function(img, index) {
    // Find the gallery group (using closest with polyfill)
    var wrapper = img.closest('.creative-image-wrapper');
    if (!wrapper) return;
    
    var galleryGroup = wrapper.getAttribute('data-gallery-group');
    
    // Make image clickable
    img.style.cursor = 'pointer';
    
    img.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      // Collect all images in the same gallery group
      var allWrappers = document.querySelectorAll('[data-gallery-group="' + galleryGroup + '"]');
      var galleryImagesList = [];
      var currentIndex = 0;
      
      allWrappers.forEach(function(wrapper, idx) {
        var imgElement = wrapper.querySelector('img');
        if (imgElement) {
          galleryImagesList.push({
            src: imgElement.src,
            alt: imgElement.alt || ''
          });
          if (imgElement === img) {
            currentIndex = idx;
          }
        }
      });
      
      // Open modal with gallery
      if (typeof openImageModal === 'function') {
        openImageModal(img.src, img.alt || '', galleryImagesList, currentIndex);
      } else {
        console.error('openImageModal function not found. Make sure common.js is loaded.');
      }
    });
  });
});
</script>

<style>
.creative-image-wrapper {
  position: relative;
}

.creative-gallery-image-container {
  cursor: pointer;
}

.creative-gallery-image-container img {
  transition: opacity 0.3s ease;
}

.creative-gallery-image-container:hover img {
  opacity: 0.8;
}

/* Image Modal Styles */
.image-modal {
  display: none;
  position: fixed;
  z-index: 9999;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0, 0, 0, 0.9);
}

.image-modal-content {
  position: relative;
  margin: auto;
  padding: 0;
  width: 90%;
  max-width: 1200px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.image-modal-img {
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
  margin: auto;
  display: block;
}

.image-modal-close {
  position: absolute;
  top: 15px;
  right: 35px;
  color: #f1f1f1;
  font-size: 40px;
  font-weight: bold;
  cursor: pointer;
  z-index: 10000;
}

.image-modal-close:hover,
.image-modal-close:focus {
  color: #bbb;
  text-decoration: none;
}

.image-modal-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  color: #f1f1f1;
  font-size: 30px;
  font-weight: bold;
  cursor: pointer;
  padding: 16px;
  user-select: none;
  z-index: 10000;
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.image-modal-nav:hover {
  background-color: rgba(0, 0, 0, 0.8);
}

.image-modal-prev {
  left: 20px;
}

.image-modal-next {
  right: 20px;
}

.image-modal-caption {
  color: #f1f1f1;
  text-align: center;
  padding: 10px;
  font-size: 14px;
}

@media (max-width: 768px) {
  .image-modal-nav {
    font-size: 20px;
    padding: 12px;
  }
  
  .image-modal-prev {
    left: 10px;
  }
  
  .image-modal-next {
    right: 10px;
  }
  
  .image-modal-close {
    top: 10px;
    right: 20px;
    font-size: 30px;
  }
}
</style>
