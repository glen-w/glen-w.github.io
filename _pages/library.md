---
layout: page
permalink: /library/
title: library
description:
nav: true
nav_order: 10
---

<!-- _pages/library.md -->
<!-- Test: {{ site.time }} -->

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

<!-- Clear Filters Link -->
<div class="search-actions">
  <a href="#" onclick="clearFilters(); return false;" class="clear-filters-link">
    <i class="fas fa-times"></i> Clear filters
  </a>
</div>

<!-- Filter Section -->
<div class="library-filters">
  <h4>filter</h4>
  
  <!-- Entry Type Filters -->
  <div class="filter-group entry-type-filters">
    <div class="filter-tags">
      {% for entry_type in site.data.dynamic_filters.entry_types %}
        <a href="#" onclick="filterByTag('{{ entry_type }}'); return false;" class="badge badge-light">{{ entry_type }}</a>
      {% endfor %}
    </div>
  </div>
  
  <!-- Role Tags Filters -->
  <div class="filter-group role-tags-filters">
    <div class="filter-tags">
      {% for role_tag in site.data.dynamic_filters.role_tags %}
        <a href="#" onclick="filterByTag('{{ role_tag }}'); return false;" class="tag">{{ role_tag }}</a>
      {% endfor %}
    </div>
  </div>
  
  <!-- Language Tags Filters -->
  <div class="filter-group language-tags-filters">
    <div class="filter-tags">
      {% for language_tag in site.data.dynamic_filters.language_tags %}
        <a href="#" onclick="filterByTag('{{ language_tag }}'); return false;" class="tag">{{ language_tag }}</a>
      {% endfor %}
    </div>
  </div>
  
  <!-- View Map Button -->
  <div class="filter-actions">
    <a href="#" onclick="toggleMap(); return false;" class="view-map-link" id="mapToggleBtn">
      <i class="fas fa-map-marker-alt"></i> View Map
    </a>
  </div>
</div>

<!-- Map Container (initially hidden) -->
<div id="libraryMapContainer" class="library-map-container" style="display: none;">
  <div id="libraryMap" class="library-map"></div>
</div>

<!-- Item Count Display -->
<div id="itemCountDisplay" class="item-count-display" style="display: none;">
  <span id="itemCountText">Showing 0 items</span>
</div>

<div class="publications">

{% bibliography %}

</div>

<!-- Library Map Styles -->
<style>
.library-map-container {
  margin: 2rem 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border: 1px solid #e0e0e0;
}

.library-map {
  height: 400px;
  width: 100%;
}

.filter-actions {
  display: inline-block;
  margin-right: 1rem;
  margin-bottom: 0.5rem;
}

/* Search actions styling */
.search-actions {
  margin: 1rem 0;
  text-align: left;
}

/* Clear filters and View Map link styling */
.clear-filters-link,
.view-map-link {
  color: var(--global-text-color);
  text-decoration: none;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  
  &:hover {
    color: var(--global-theme-color);
    text-decoration: none;
  }
  
  i {
    font-size: 0.8rem;
  }
}

/* Filter group spacing */
.filter-group {
  margin-bottom: 0.75rem;
}

.filter-group.entry-type-filters {
  margin-bottom: 1rem;
}

/* Increased spacing for all filter tags */
.filter-group .filter-tags {
  gap: 0.75rem;
  row-gap: 0.75rem;
}

.filter-group.role-tags-filters {
  margin-bottom: 1rem;
}

.filter-group.language-tags-filters {
  margin-bottom: 0.75rem;
}

/* Additional styling for filter badges and tags to match bibliography behavior */
.library-filters .filter-tags .badge,
.library-filters .filter-tags .tag {
  cursor: pointer;
  user-select: none;
  text-decoration: none;
  color: inherit;
  margin-right: 0 !important; /* Override bibliography margin to use gap instead */
  margin-bottom: 0 !important; /* Override bibliography margin to use gap instead */
  
  &:hover {
    text-decoration: none;
    color: inherit;
  }
  
  &:visited {
    color: inherit;
  }
  
  &.active {
    background-color: var(--global-theme-color) !important;
    color: var(--global-card-bg-color) !important;
    border-color: var(--global-theme-color) !important;
  }
}

/* Marker cluster styling */
.marker-cluster {
  background-color: rgba(0, 123, 255, 0.6);
  border: 2px solid rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  color: white;
  height: 40px;
  line-height: 40px;
  text-align: center;
  width: 40px;
  font-weight: bold;
  font-size: 14px;
}

.marker-cluster-medium {
  background-color: rgba(255, 193, 7, 0.8);
  color: #212529;
}

.marker-cluster-large {
  background-color: rgba(220, 53, 69, 0.8);
  color: white;
}

.cluster-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  font-weight: bold;
  font-size: 14px;
}

/* Item count display styling */
.item-count-display {
  margin: 1rem 0;
  padding: 0.75rem 1rem;
  background-color: var(--global-bg-color);
  border: 1px solid var(--global-border-color);
  border-radius: 0.375rem;
  font-size: 0.9rem;
  color: var(--global-text-color);
  text-align: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.item-count-display.show {
  display: block !important;
}


/* Custom popup styles for library map */
.library-map .leaflet-popup-content-wrapper {
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.library-map .popup-content {
  min-width: 250px;
}

.library-map .popup-title {
  font-size: 1.1rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 0.5rem;
  line-height: 1.3;
}

.library-map .popup-details {
  margin: 0.5rem 0;
}

.library-map .popup-detail {
  margin: 0.3rem 0;
  font-size: 0.9rem;
  color: #666;
}

.library-map .popup-detail i {
  width: 16px;
  color: #007bff;
}

.library-map .popup-link {
  display: inline-block;
  background: #007bff;
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  font-size: 0.9rem;
  margin-top: 0.5rem;
  transition: background 0.3s;
}

.library-map .popup-link:hover {
  background: #0056b3;
  color: white;
  text-decoration: none;
}
</style>

<!-- Library Filter Script -->
<script>
// Check for jump action on page load
document.addEventListener('DOMContentLoaded', function() {
  const urlParams = new URLSearchParams(window.location.search);
  const action = urlParams.get('action');
  const hash = window.location.hash;
  
  if (action === 'jump' && hash) {
    // Wait a bit for the page to fully load, then scroll to the anchor
    setTimeout(() => {
      const targetElement = document.querySelector(hash);
      if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        // Highlight the element briefly
        targetElement.style.backgroundColor = '#fff3cd';
        targetElement.style.transition = 'background-color 0.5s ease';
        setTimeout(() => {
          targetElement.style.backgroundColor = '';
        }, 2000);
      }
    }, 500);
  }
  
  // Add listener to search input for item count updates
  const searchInput = document.getElementById('bibsearch');
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      // Use a small delay to allow the search to process
      setTimeout(() => {
        if (this.value.trim() !== '') {
          updateItemCount();
        } else {
          hideItemCount();
          clearActiveTags();
        }
      }, 100);
    });
  }
  
  // Initialize filter counts on page load with a delay to ensure bibliography is rendered
  setTimeout(() => {
    updateFilterCounts();
  }, 200);
});

// Simple filter functions that use the existing bibsearch infrastructure
function filterByTag(tag) {
  const searchInput = document.getElementById('bibsearch');
  if (searchInput) {
    searchInput.value = tag;
    // Trigger the input event to activate the existing search
    searchInput.dispatchEvent(new Event('input', { bubbles: true }));
    // Add active state to clicked tag
    setActiveTag(tag);
    
    // Update item count after a delay to ensure filtering has taken effect
    setTimeout(() => {
      updateItemCount();
    }, 150);
  }
}

function clearFilters() {
  const searchInput = document.getElementById('bibsearch');
  if (searchInput) {
    searchInput.value = '';
    // Trigger the input event to clear the search
    searchInput.dispatchEvent(new Event('input', { bubbles: true }));
    // Remove active state from all tags
    clearActiveTags();
    
    // Hide item count after a delay to ensure clearing has taken effect
    setTimeout(() => {
      hideItemCount();
    }, 150);
  }
}

function setActiveTag(tag) {
  // Remove active state from all tags first
  clearActiveTags();
  
  // Find and activate the clicked tag
  const allTags = document.querySelectorAll('.library-filters .filter-tags a.badge, .library-filters .filter-tags a.tag');
  allTags.forEach(element => {
    // Extract the base text without the count
    const baseText = element.textContent.replace(/\s*\(\d+\)\s*$/, '').trim();
    if (baseText === tag) {
      element.classList.add('active');
    }
  });
}

function clearActiveTags() {
  const allTags = document.querySelectorAll('.library-filters .filter-tags a.badge, .library-filters .filter-tags a.tag');
  allTags.forEach(element => {
    element.classList.remove('active');
  });
}

function updateFilterCounts() {
  // Count items for each filter category
  const filterButtons = document.querySelectorAll('.library-filters .filter-tags a.badge, .library-filters .filter-tags a.tag');
  
  filterButtons.forEach(button => {
    const filterText = button.textContent.replace(/\s*\(\d+\)\s*$/, ''); // Remove existing count
    const count = countItemsForFilter(filterText);
    
    if (count > 0) {
      button.textContent = `${filterText} (${count})`;
      button.style.display = 'inline-flex';
    } else {
      button.style.display = 'none';
    }
  });
  
  // Also update the total item count display
  updateItemCount();
}

function countItemsForFilter(filterText) {
  // Get all bibliography items (unfiltered)
  const allItems = document.querySelectorAll('.publications ol.bibliography li');
  let count = 0;
  
  // Debug: log the filter text and total items
  console.log(`Counting items for filter: "${filterText}", total items: ${allItems.length}`);
  
  allItems.forEach((item, index) => {
    // Skip group headers - they typically don't have the full bibliography structure
    const hasTitle = item.querySelector('.title');
    const hasAuthor = item.querySelector('.author');
    const hasLinks = item.querySelector('.links');
    const isGroupHeader = !hasTitle && !hasAuthor && !hasLinks;
    
    if (isGroupHeader) {
      console.log(`Skipping group header item ${index}`);
      return;
    }
    
    // Temporarily make sure item is visible for counting (remove unloaded class and inline styles)
    const originalDisplay = item.style.display;
    const hadUnloadedClass = item.classList.contains('unloaded');
    item.style.display = '';
    item.classList.remove('unloaded');
    
    // Check if this item matches the filter
    const matches = itemMatchesFilter(item, filterText);
    if (matches) {
      count++;
      console.log(`Item ${index} matches filter "${filterText}":`, item.textContent.substring(0, 100));
    }
    
    // Restore original display state
    item.style.display = originalDisplay;
    if (hadUnloadedClass) {
      item.classList.add('unloaded');
    }
  });
  
  console.log(`Filter "${filterText}" count: ${count}`);
  return count;
}

function itemMatchesFilter(item, filterText) {
  const itemText = item.textContent.toLowerCase();
  const filterLower = filterText.toLowerCase();
  
  // First, check if this is a role tag filter by looking for role tags in the item
  const roleTags = item.querySelectorAll('.item-type .tag');
  const hasRoleTag = Array.from(roleTags).some(tag => {
    const tagText = tag.textContent.toLowerCase().trim();
    return tagText === filterLower;
  });
  
  if (hasRoleTag) {
    console.log(`Role tag "${filterLower}" found in item`);
    return true;
  }
  
  // Check for language tags
  const languageTags = item.querySelectorAll('.all-tags .tag');
  const hasLanguageTag = Array.from(languageTags).some(tag => {
    const tagText = tag.textContent.toLowerCase().trim();
    return tagText.includes(filterLower);
  });
  
  if (hasLanguageTag) {
    console.log(`Language tag "${filterLower}" found in item`);
    return true;
  }
  
  // Check for item type badges
  const itemTypeBadges = item.querySelectorAll('.item-type .badge');
  const hasItemTypeBadge = Array.from(itemTypeBadges).some(badge => {
    const badgeText = badge.textContent.toLowerCase().trim();
    return badgeText === filterLower;
  });
  
  if (hasItemTypeBadge) {
    console.log(`Item type badge "${filterLower}" found in item`);
    return true;
  }
  
  // Dynamic pattern matching based on common patterns for item types
  const patterns = {
    // Standard BibTeX entry types - proper multiword names
    'journal article': ['journal article', 'article', 'journal'],
    'conference paper': ['conference paper', 'conference', 'inproceedings'],
    'conference': ['conference', 'conference paper', 'inproceedings'],
    'book chapter': ['book chapter', 'incollection', 'chapter'],
    'book section': ['book section', 'inbook', 'section'],
    'phd thesis': ['phd thesis', 'ph.d. thesis', 'phdthesis', 'phd'],
    'master\'s thesis': ['master\'s thesis', 'master thesis', 'mastersthesis', 'master'],
    'thesis': ['thesis'],
    'report': ['report', 'techreport'],
    'briefing note': ['briefing note', 'briefing'],
    'proceedings': ['proceedings'],
    'manual': ['manual'],
    'patent': ['patent'],
    'unpublished': ['unpublished'],
    'book': ['book'],
    'other': ['misc', 'other'],
    'blog': ['blog', 'blog post'],
    'webinar': ['webinar'],
    'workshop': ['workshop'],
    'panel': ['panel'],
    'roundtable': ['roundtable'],
    'guest lecture': ['guest lecture', 'guest'],
    'newspaper': ['newspaper']
  };
  
  // Check if we have specific patterns for this filter
  if (patterns[filterLower]) {
    const patternMatches = patterns[filterLower].some(pattern => {
      const matches = itemText.includes(pattern);
      if (matches) {
        console.log(`Pattern "${pattern}" matched in item text`);
      }
      return matches;
    });
    return patternMatches;
  }
  
  // Fallback to simple text matching for other cases
  const simpleMatch = itemText.includes(filterLower);
  if (simpleMatch) {
    console.log(`Simple text match for "${filterLower}"`);
  }
  return simpleMatch;
}

function updateItemCount() {
  const countDisplay = document.getElementById('itemCountDisplay');
  const countText = document.getElementById('itemCountText');
  
  if (countDisplay && countText) {
    // Count visible bibliography items (not hidden by unloaded class or inline styles)
    // Exclude group headers by filtering out items that don't have the expected bibliography structure
    const allItems = document.querySelectorAll('.publications ol.bibliography li');
    const visibleItems = document.querySelectorAll('.publications ol.bibliography li:not(.unloaded):not([style*="display: none"])');
    
    // Filter out group headers - they typically don't have the full bibliography structure
    const actualItems = Array.from(visibleItems).filter(item => {
      // Group headers typically don't have title, author, or other bibliography elements
      const hasTitle = item.querySelector('.title');
      const hasAuthor = item.querySelector('.author');
      const hasLinks = item.querySelector('.links');
      
      // If it has at least one of these elements, it's a real bibliography item
      return hasTitle || hasAuthor || hasLinks;
    });
    
    const count = actualItems.length;
    
    console.log(`Updating item count: ${count} actual items out of ${allItems.length} total items (${visibleItems.length} visible)`);
    
    // Debug: log all items to see what's being counted
    console.log('All bibliography items:');
    allItems.forEach((item, index) => {
      const isGroupHeader = !item.querySelector('.title') && !item.querySelector('.author') && !item.querySelector('.links');
      console.log(`Item ${index} (${isGroupHeader ? 'GROUP HEADER' : 'BIBLIOGRAPHY ITEM'}):`, item.textContent.substring(0, 100));
    });
    
    countText.textContent = `Showing ${count} item${count !== 1 ? 's' : ''}`;
    countDisplay.classList.add('show');
    countDisplay.style.display = 'block';
  }
  
}


function hideItemCount() {
  const countDisplay = document.getElementById('itemCountDisplay');
  
  if (countDisplay) {
    countDisplay.classList.remove('show');
    countDisplay.style.display = 'none';
  }
}

// Map toggle functionality
let libraryMap = null;
let mapInitialized = false;

function toggleMap() {
  const mapContainer = document.getElementById('libraryMapContainer');
  const toggleBtn = document.getElementById('mapToggleBtn');
  
  if (mapContainer.style.display === 'none') {
    mapContainer.style.display = 'block';
    toggleBtn.innerHTML = '<i class="fas fa-map-marker-alt"></i> Hide Map';
    
    // Initialize map if not already done
    if (!mapInitialized) {
      initializeLibraryMap();
    }
  } else {
    mapContainer.style.display = 'none';
    toggleBtn.innerHTML = '<i class="fas fa-map-marker-alt"></i> View Map';
  }
}

function initializeLibraryMap() {
  // Load Leaflet CSS and JS dynamically
  if (!document.querySelector('link[href*="leaflet"]')) {
    const leafletCSS = document.createElement('link');
    leafletCSS.rel = 'stylesheet';
    leafletCSS.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    leafletCSS.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
    leafletCSS.crossOrigin = 'anonymous';
    document.head.appendChild(leafletCSS);
    
    // Load MarkerCluster CSS
    const clusterCSS = document.createElement('link');
    clusterCSS.rel = 'stylesheet';
    clusterCSS.href = 'https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css';
    clusterCSS.crossOrigin = 'anonymous';
    document.head.appendChild(clusterCSS);
    
    const clusterDefaultCSS = document.createElement('link');
    clusterDefaultCSS.rel = 'stylesheet';
    clusterDefaultCSS.href = 'https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css';
    clusterDefaultCSS.crossOrigin = 'anonymous';
    document.head.appendChild(clusterDefaultCSS);
  }
  
  if (!window.L) {
    const leafletJS = document.createElement('script');
    leafletJS.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    leafletJS.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
    leafletJS.crossOrigin = 'anonymous';
    leafletJS.onload = function() {
      loadMarkerCluster();
    };
    document.head.appendChild(leafletJS);
  } else {
    loadMarkerCluster();
  }
}

function loadMarkerCluster() {
  if (!window.L.markerClusterGroup) {
    const clusterJS = document.createElement('script');
    clusterJS.src = 'https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js';
    clusterJS.crossOrigin = 'anonymous';
    clusterJS.onload = function() {
      createLibraryMap();
    };
    document.head.appendChild(clusterJS);
  } else {
    createLibraryMap();
  }
}

function createLibraryMap() {
  // Initialize map
  libraryMap = L.map('libraryMap').setView([50.0, 10.0], 4);
  
  // Add OpenStreetMap tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
  }).addTo(libraryMap);
  
  // Create marker cluster group
  const markers = L.markerClusterGroup({
    chunkedLoading: true,
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: false,
    zoomToBoundsOnClick: true,
    maxClusterRadius: 50,
    iconCreateFunction: function(cluster) {
      const count = cluster.getChildCount();
      let size = 'small';
      if (count > 10) size = 'large';
      else if (count > 5) size = 'medium';
      
      return L.divIcon({
        html: '<div class="cluster-icon cluster-' + size + '">' + count + '</div>',
        className: 'marker-cluster marker-cluster-' + size,
        iconSize: L.point(40, 40)
      });
    }
  });
  
  // Add cluster group to map
  libraryMap.addLayer(markers);
  
  // Load and display conference data
  fetch('/assets/mapping/location_coordinates.json')
    .then(response => response.json())
    .then(data => {
      const conferences = data.locations || [];
      const geocodedConferences = conferences.filter(conf => conf.geocoded);
      
      geocodedConferences.forEach(conf => {
        const coords = conf.coordinates;
        const marker = L.marker([coords.lat, coords.lng]);
        
        // Create popup content
        const popupContent = createPopupContent(conf);
        marker.bindPopup(popupContent);
        
        // Add marker to cluster group
        markers.addLayer(marker);
      });
      
      // Fit map to show all markers
      if (geocodedConferences.length > 0) {
        libraryMap.fitBounds(markers.getBounds().pad(0.1));
      }
    })
    .catch(error => {
      console.error('Error loading conference data:', error);
    });
  
  mapInitialized = true;
}

function createPopupContent(conf) {
  const date = formatDate(conf.year, conf.month);
  const eventType = formatEventType(conf.entry_type);
  
  return `
    <div class="popup-content">
      <div class="popup-title">${escapeHtml(conf.title)}</div>
      <div class="popup-details">
        <div class="popup-detail">
          <i class="fas fa-calendar"></i> ${date}
        </div>
        <div class="popup-detail">
          <i class="fas fa-tag"></i> ${eventType}
        </div>
        <div class="popup-detail">
          <i class="fas fa-map-marker-alt"></i> ${escapeHtml(conf.address)}
        </div>
      </div>
      <a href="/library/?action=jump#${conf.bibtex_key}" class="popup-link">
        <i class="fas fa-external-link-alt"></i> View Details
      </a>
    </div>
  `;
}

function formatDate(year, month) {
  if (!year) return 'Date unknown';
  
  const monthNames = {
    'jan': 'January', 'feb': 'February', 'mar': 'March', 'apr': 'April',
    'may': 'May', 'jun': 'June', 'jul': 'July', 'aug': 'August',
    'sep': 'September', 'oct': 'October', 'nov': 'November', 'dec': 'December'
  };
  
  const monthName = month ? monthNames[month.toLowerCase()] : '';
  return monthName ? `${monthName} ${year}` : year;
}

function formatEventType(type) {
  const typeMap = {
    'conference': 'Conference',
    'roundtable': 'Roundtable',
    'workshop': 'Workshop',
    'misc': 'Event'
  };
  return typeMap[type.toLowerCase()] || type;
}

function generateLibraryUrl(conf) {
  // Generate the library page URL based on the title slug
  const title = conf.title || 'untitled';
  const titleSlug = slugify(title, 50);
  return `${titleSlug}/`;
}

function slugify(text, maxLength = 50) {
  // Enhanced slugify function with accent handling similar to Python slugify
  return text
    .toLowerCase()
    .normalize('NFD') // Decompose accented characters
    .replace(/[\u0300-\u036f]/g, '') // Remove accent marks
    .replace(/[^\w\s-]/g, '') // Remove special characters
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/-+/g, '-') // Replace multiple hyphens with single
    .replace(/^-|-$/g, '') // Remove leading/trailing hyphens
    .substring(0, maxLength); // Truncate to max length
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
</script>
