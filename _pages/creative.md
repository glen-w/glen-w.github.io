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

# Enable flipbook/carousel layouts
images:
  slider: true
---


<div class="projects">
  {% if site.enable_project_categories and page.display_categories %}
    <!-- Categorized display -->
    {% for category in page.display_categories %}
    <a id="{{ category }}" href=".#{{ category }}">
      <h2 class="category">{{ category }}</h2>
    </a>
    {% assign categorized_projects = site.creative | where: "category", category %}
    
    <!-- Collect all unique series from paths with metadata -->
    {% assign all_series_keys = '' | split: '' %}
    {% for item in categorized_projects %}
      {% assign path_parts = item.path | split: '/' %}
      {% if path_parts.size >= 3 %}
        {% assign series_key = path_parts[2] %}
        {% assign found = false %}
        {% for existing_key in all_series_keys %}
          {% if existing_key == series_key %}
            {% assign found = true %}
          {% endif %}
        {% endfor %}
        {% unless found %}
          {% assign all_series_keys = all_series_keys | push: series_key %}
        {% endunless %}
      {% endif %}
    {% endfor %}
    
    <!-- Separate series by show status and get priorities -->
    {% assign series_show_true = '' | split: '' %}
    {% assign series_show_more = '' | split: '' %}
    {% assign series_priorities = '' | split: '' %}
    
    {% for series_key in all_series_keys %}
      {% assign series_show = 'true' %}
      {% assign series_priority = 999 %}
      {% if site.data.series and site.data.series[series_key] %}
        {% if site.data.series[series_key].show %}
          {% comment %} Convert to string to handle both boolean true and string 'true' {% endcomment %}
          {% assign series_show_raw = site.data.series[series_key].show %}
          {% if series_show_raw == true %}
            {% assign series_show = 'true' %}
          {% elsif series_show_raw == false %}
            {% assign series_show = 'false' %}
          {% else %}
            {% assign series_show = series_show_raw | downcase %}
          {% endif %}
        {% endif %}
        {% if site.data.series[series_key].priority %}
          {% assign series_priority = site.data.series[series_key].priority %}
        {% endif %}
      {% endif %}
      
      {% if series_show == 'true' %}
        {% assign series_show_true = series_show_true | push: series_key %}
        {% assign priority_pair = series_priority | append: '|' | append: series_key %}
        {% assign series_priorities = series_priorities | push: priority_pair %}
      {% elsif series_show == 'more' %}
        {% assign series_show_more = series_show_more | push: series_key %}
      {% endif %}
    {% endfor %}
    
    <!-- Sort series by priority (lower numbers first), then alphabetically -->
    {% assign sorted_series_keys = '' | split: '' %}
    {% assign processed_series = '' | split: '' %}
    
    <!-- First, process series with priorities (sorted by priority value) -->
    {% assign max_iterations = series_priorities.size %}
    {% for i in (1..max_iterations) %}
      {% assign lowest_priority = 9999 %}
      {% assign lowest_series = '' %}
      {% assign lowest_pair = '' %}
      
      {% for priority_pair in series_priorities %}
        {% assign pair_parts = priority_pair | split: '|' %}
        {% assign pair_priority = pair_parts[0] | plus: 0 %}
        {% assign pair_key = pair_parts[1] %}
        {% assign already_processed = false %}
        {% for processed in processed_series %}
          {% if processed == pair_key %}
            {% assign already_processed = true %}
          {% endif %}
        {% endfor %}
        
        {% unless already_processed %}
          {% if pair_priority < lowest_priority %}
            {% assign lowest_priority = pair_priority %}
            {% assign lowest_series = pair_key %}
            {% assign lowest_pair = priority_pair %}
          {% elsif pair_priority == lowest_priority %}
            {% if lowest_series == '' or pair_key < lowest_series %}
              {% assign lowest_series = pair_key %}
              {% assign lowest_pair = priority_pair %}
            {% endif %}
          {% endif %}
        {% endunless %}
      {% endfor %}
      
      {% if lowest_series != '' %}
        {% assign sorted_series_keys = sorted_series_keys | push: lowest_series %}
        {% assign processed_series = processed_series | push: lowest_series %}
      {% endif %}
    {% endfor %}
    
    <!-- Display projects grouped by series (show: true, sorted by priority) -->
    {% for series_key in sorted_series_keys %}
      {% assign series_projects = '' | split: '' %}
      {% for item in categorized_projects %}
        {% assign path_parts = item.path | split: '/' %}
        {% if path_parts.size >= 3 and path_parts[2] == series_key %}
          {% assign series_projects = series_projects | push: item %}
        {% endif %}
      {% endfor %}
      {% assign series_projects = series_projects | sort: "importance" %}
      
      {% if series_projects.size > 0 %}
        {% comment %} Get display name from series.yml, fallback to folder name with underscores replaced {% endcomment %}
        {% assign series_display_name = series_key | replace: '_', ' ' %}
        {% if site.data.series and site.data.series[series_key] and site.data.series[series_key].name %}
          {% assign series_display_name = site.data.series[series_key].name %}
        {% endif %}
        
        {% comment %} Check if this series has a custom layout defined {% endcomment %}
        {% assign series_layout = null %}
        {% if site.data.series and site.data.series[series_key] %}
          {% assign series_layout = site.data.series[series_key].layout %}
        {% endif %}
        
        {% comment %} Wrap each series in an isolated section to prevent layout interference {% endcomment %}
        <section class="series-section" data-series-key="{{ series_key }}" data-series-layout="{{ series_layout | default: 'grid' }}">
          <h3 class="series">{{ series_display_name }}</h3>
        
          {% if series_layout == 'flipbook' %}
             {% include flipbook.liquid series_projects=series_projects series_name=series_display_name %}
           {% elsif series_layout == 'carousel' %}
             {% include carousel.liquid series_projects=series_projects series_name=series_display_name %}
           {% elsif series_layout == 'masonry' %}
             {% include masonry.liquid series_projects=series_projects series_name=series_display_name %}
           {% elsif series_layout == 'thumbnails' %}
             {% include thumbnails.liquid series_projects=series_projects series_name=series_display_name %}
           {% else %}
        {% comment %} Default card grid layout - show first 6, then toggle for rest {% endcomment %}
        {% assign total_projects = series_projects.size %}
        {% assign initial_count = 6 %}
        {% if total_projects > initial_count %}
          {% comment %} Split into visible and hidden items {% endcomment %}
          {% if page.horizontal %}
          <div class="container">
            <div class="row row-cols-1 row-cols-md-2 series-grid-visible">
            {% for project in series_projects limit: initial_count %}
              {% include projects_creative_horizontal.liquid %}
            {% endfor %}
            </div>
            <div class="row row-cols-1 row-cols-md-2 series-grid-hidden" style="display: none;">
            {% for project in series_projects offset: initial_count %}
              {% include projects_creative_horizontal.liquid %}
            {% endfor %}
            </div>
            <div class="series-more-toggle-container">
              <button class="series-more-toggle" type="button" data-series-key="{{ series_key }}" aria-expanded="false">
                See more from this series
              </button>
            </div>
          </div>
          {% else %}
          <div class="row row-cols-1 row-cols-md-3 series-grid-visible">
            {% for project in series_projects limit: initial_count %}
              {% include projects_creative.liquid %}
            {% endfor %}
          </div>
          <div class="row row-cols-1 row-cols-md-3 series-grid-hidden" style="display: none;">
            {% for project in series_projects offset: initial_count %}
              {% include projects_creative.liquid %}
            {% endfor %}
          </div>
          <div class="series-more-toggle-container">
            <button class="series-more-toggle" type="button" data-series-key="{{ series_key }}" aria-expanded="false">
              See more from this series
            </button>
          </div>
          {% endif %}
        {% else %}
          {% comment %} Show all items if 6 or fewer {% endcomment %}
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
        {% endif %}
      {% endif %}
        </section>
      {% endif %}
    {% endfor %}
    
    <!-- Display series with show: more under "Show more" section -->
    {% if series_show_more.size > 0 %}
      {% assign sorted_more_series = series_show_more | sort %}
      <div data-read-more="Show more" data-read-less="Show less">
        {% for series_key in sorted_more_series %}
          {% assign series_projects = '' | split: '' %}
          {% for item in categorized_projects %}
            {% assign path_parts = item.path | split: '/' %}
            {% if path_parts.size >= 3 and path_parts[2] == series_key %}
              {% assign series_projects = series_projects | push: item %}
            {% endif %}
          {% endfor %}
          {% assign series_projects = series_projects | sort: "importance" %}
          
          {% if series_projects.size > 0 %}
            {% comment %} Get display name from series.yml, fallback to folder name with underscores replaced {% endcomment %}
            {% assign series_display_name = series_key | replace: '_', ' ' %}
            {% if site.data.series and site.data.series[series_key] and site.data.series[series_key].name %}
              {% assign series_display_name = site.data.series[series_key].name %}
            {% endif %}
            
            {% comment %} Check if this series has a custom layout defined {% endcomment %}
            {% assign series_layout = null %}
            {% if site.data.series and site.data.series[series_key] %}
              {% assign series_layout = site.data.series[series_key].layout %}
            {% endif %}
            
            {% comment %} Wrap each series in an isolated section to prevent layout interference {% endcomment %}
            <section class="series-section" data-series-key="{{ series_key }}" data-series-layout="{{ series_layout | default: 'grid' }}">
              <h3 class="series">{{ series_display_name }}</h3>
          
          {% if series_layout == 'flipbook' %}
            {% include flipbook.liquid series_projects=series_projects series_name=series_display_name %}
          {% elsif series_layout == 'carousel' %}
            {% include carousel.liquid series_projects=series_projects series_name=series_display_name %}
          {% elsif series_layout == 'masonry' %}
            {% include masonry.liquid series_projects=series_projects series_name=series_display_name %}
          {% elsif series_layout == 'thumbnails' %}
            {% include thumbnails.liquid series_projects=series_projects series_name=series_display_name %}
          {% else %}
            {% comment %} Default card grid layout - show first 6, then toggle for rest {% endcomment %}
            {% assign total_projects = series_projects.size %}
            {% assign initial_count = 6 %}
            {% if total_projects > initial_count %}
              {% comment %} Split into visible and hidden items {% endcomment %}
              {% if page.horizontal %}
              <div class="container">
                <div class="row row-cols-1 row-cols-md-2 series-grid-visible">
                {% for project in series_projects limit: initial_count %}
                  {% include projects_creative_horizontal.liquid %}
                {% endfor %}
                </div>
                <div class="row row-cols-1 row-cols-md-2 series-grid-hidden" style="display: none;">
                {% for project in series_projects offset: initial_count %}
                  {% include projects_creative_horizontal.liquid %}
                {% endfor %}
                </div>
                <div class="series-more-toggle-container">
                  <button class="series-more-toggle" type="button" data-series-key="{{ series_key }}" aria-expanded="false">
                    See more from this series
                  </button>
                </div>
              </div>
              {% else %}
              <div class="row row-cols-1 row-cols-md-3 series-grid-visible">
                {% for project in series_projects limit: initial_count %}
                  {% include projects_creative.liquid %}
                {% endfor %}
              </div>
              <div class="row row-cols-1 row-cols-md-3 series-grid-hidden" style="display: none;">
                {% for project in series_projects offset: initial_count %}
                  {% include projects_creative.liquid %}
                {% endfor %}
              </div>
              <div class="series-more-toggle-container">
                <button class="series-more-toggle" type="button" data-series-key="{{ series_key }}" aria-expanded="false">
                  See more from this series
                </button>
              </div>
              {% endif %}
            {% else %}
              {% comment %} Show all items if 6 or fewer {% endcomment %}
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
            {% endif %}
          {% endif %}
            </section>
          {% endif %}
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
  
  // Series grid "See more" toggle functionality
  const seriesMoreToggles = document.querySelectorAll('.series-more-toggle');
  
  seriesMoreToggles.forEach(function(toggle) {
    toggle.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      const seriesKey = toggle.getAttribute('data-series-key');
      const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
      const seriesSection = toggle.closest('.series-section');
      
      if (!seriesSection) return;
      
      const hiddenGrid = seriesSection.querySelector('.series-grid-hidden');
      const visibleGrid = seriesSection.querySelector('.series-grid-visible');
      
      if (!hiddenGrid) return;
      
      if (isExpanded) {
        // Collapse - hide additional items
        hiddenGrid.style.display = 'none';
        toggle.textContent = 'See more from this series';
        toggle.setAttribute('aria-expanded', 'false');
      } else {
        // Expand - show additional items
        hiddenGrid.style.display = '';
        toggle.textContent = 'See less from this series';
        toggle.setAttribute('aria-expanded', 'true');
        
        // Smooth scroll to show the newly revealed content
        setTimeout(function() {
          hiddenGrid.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
      }
    });
    
    // Support keyboard navigation
    toggle.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        toggle.click();
      }
    });
  });
});
</script>

<style>
/* Series grid toggle styles */
.series-grid-hidden {
  margin-top: 1rem;
}

.series-more-toggle-container {
  text-align: center;
  margin: 1.5rem 0;
  padding: 1rem 0;
}

.series-more-toggle {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.95rem;
  padding: 0.5rem 1rem;
  text-decoration: underline;
  transition: opacity 0.3s ease;
  color: rgba(0, 0, 0, 0.55);
}

.series-more-toggle:hover {
  text-decoration: none;
  opacity: 0.8;
}

.series-more-toggle:focus {
  outline: 2px solid currentColor;
  outline-offset: 2px;
  text-decoration: none;
}

.series-more-toggle[aria-expanded="true"]::after {
  content: " (show less)";
  font-size: 0.85em;
  opacity: 0.7;
}

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

/* Thumbnails layout styles */
.thumbnails-container {
  margin: 1.5rem 0;
}

.thumbnails-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.75rem;
  padding: 0.5rem 0;
}

@media (min-width: 576px) {
  .thumbnails-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }
}

@media (min-width: 768px) {
  .thumbnails-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 1.25rem;
  }
}

.thumbnail-item {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
}

.thumbnail-wrapper {
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.thumbnail-image-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.thumbnail-image-container:hover {
  opacity: 0.85;
  transform: scale(1.02);
}

.thumbnail-image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
</style>

{% comment %} Load flipbook, carousel, masonry, and poetry scripts/styles if needed {% endcomment %}
{% assign has_flipbook = false %}
{% assign has_carousel = false %}
{% assign has_masonry = false %}
{% assign has_poems = false %}
{% if site.data.series %}
  {% for category in page.display_categories %}
    {% assign categorized_projects = site.creative | where: "category", category %}
    {% assign all_series_keys = '' | split: '' %}
    {% for item in categorized_projects %}
      {% assign path_parts = item.path | split: '/' %}
      {% if path_parts.size >= 3 %}
        {% assign series_key = path_parts[2] %}
        {% assign found = false %}
        {% for existing_key in all_series_keys %}
          {% if existing_key == series_key %}
            {% assign found = true %}
          {% endif %}
        {% endfor %}
        {% unless found %}
          {% assign all_series_keys = all_series_keys | push: series_key %}
        {% endunless %}
      {% endif %}
      {% if item.category == 'poems' %}
        {% assign has_poems = true %}
      {% endif %}
    {% endfor %}
    {% for series_key in all_series_keys %}
      {% if site.data.series[series_key] %}
        {% if site.data.series[series_key].layout == 'flipbook' %}
          {% assign has_flipbook = true %}
        {% elsif site.data.series[series_key].layout == 'carousel' %}
          {% assign has_carousel = true %}
        {% elsif site.data.series[series_key].layout == 'masonry' %}
          {% assign has_masonry = true %}
        {% endif %}
      {% endif %}
    {% endfor %}
  {% endfor %}
{% endif %}

{% if has_flipbook %}
  <!-- jQuery is already loaded in scripts.liquid -->
  <!-- Turn.js for flipbook (requires jQuery) -->
  {% assign version_placeholder = '{{version}}' %}
  <script
    defer
    src="{{ site.third_party_libraries.turnjs.url.js | replace: version_placeholder, site.third_party_libraries.turnjs.version }}"
    integrity="{{ site.third_party_libraries.turnjs.integrity.js }}"
    crossorigin="anonymous"
  ></script>
  <script defer src="{{ '/sandbox/flipbook.js' | relative_url }}" type="text/javascript"></script>
  <link rel="stylesheet" href="{{ '/sandbox/flipbook.css' | relative_url }}">
{% endif %}

{% if has_carousel %}
  <!-- Carousel scripts already loaded via page.images.slider -->
  <script defer src="{{ '/sandbox/carousel.js' | relative_url }}" type="text/javascript"></script>
  <link rel="stylesheet" href="{{ '/sandbox/carousel.css' | relative_url }}">
{% endif %}

{% if has_masonry %}
  <!-- Masonry layout (Masonry.js and imagesLoaded already loaded via enable_masonry) -->
  <script defer src="{{ '/sandbox/masonry-layout.js' | relative_url }}" type="text/javascript"></script>
  <link rel="stylesheet" href="{{ '/sandbox/masonry-layout.css' | relative_url }}">
{% endif %}

{% if has_poems %}
  <!-- Poetry typewriter modal -->
  <script defer src="{{ '/sandbox/poetry-typewriter.js' | relative_url }}" type="text/javascript"></script>
  <link rel="stylesheet" href="{{ '/sandbox/poetry-typewriter.css' | relative_url }}">
{% endif %}

{% comment %} Read More Toggle functionality for show: more series {% endcomment %}
{% comment %} Check if any series has show: more {% endcomment %}
{% assign has_show_more = false %}
{% if site.data.series %}
  {% for category in page.display_categories %}
    {% assign categorized_projects = site.creative | where: "category", category %}
    {% assign all_series_keys = '' | split: '' %}
    {% for item in categorized_projects %}
      {% assign path_parts = item.path | split: '/' %}
      {% if path_parts.size >= 3 %}
        {% assign series_key = path_parts[2] %}
        {% assign found = false %}
        {% for existing_key in all_series_keys %}
          {% if existing_key == series_key %}
            {% assign found = true %}
          {% endif %}
        {% endfor %}
        {% unless found %}
          {% assign all_series_keys = all_series_keys | push: series_key %}
        {% endunless %}
      {% endif %}
    {% endfor %}
    {% for series_key in all_series_keys %}
      {% if site.data.series[series_key] and site.data.series[series_key].show %}
        {% assign series_show_raw = site.data.series[series_key].show %}
        {% if series_show_raw != true and series_show_raw != false %}
          {% assign series_show_check = series_show_raw | downcase %}
          {% if series_show_check == 'more' %}
            {% assign has_show_more = true %}
          {% endif %}
        {% endif %}
      {% endif %}
    {% endfor %}
  {% endfor %}
{% endif %}

{% if has_show_more %}
<style>
/* Read More Toggle Styles */
.js-enabled .read-more-content.read-more-collapsed {
  display: none;
}

.js-enabled .read-more-content.read-more-expanded {
  display: block;
}

.read-more-toggle {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  font-family: inherit;
  font-size: inherit;
  padding: 0;
  text-decoration: underline;
  margin: 1rem 0;
  display: inline-block;
}

.read-more-toggle:hover,
.read-more-toggle:focus {
  text-decoration: none;
  opacity: 0.8;
}

.read-more-toggle:focus {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}

.read-more-content {
  transition: opacity 0.3s ease;
}
</style>

<script src="{{ '/assets/js/read-more.js' | relative_url | bust_file_cache }}" type="text/javascript"></script>
{% endif %}
