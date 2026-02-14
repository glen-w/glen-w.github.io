---
layout: page
permalink: /library/
title: library
description:
nav: true
nav_order: 30
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
    <div class="filter-group-title">type</div>
    <div class="filter-tags">
      {% for entry_type in site.data.dynamic_filters.entry_types %}
        {% assign count = site.data.dynamic_filters.entry_type_counts[entry_type] | default: 0 %}
        {% if count > 0 %}
          <a href="#" onclick="filterByTag('{{ entry_type }}'); return false;" class="badge badge-light">{{ entry_type }} ({{ count }})</a>
        {% endif %}
      {% endfor %}
    </div>
  </div>
  
  <!-- Role Tags Filters -->
  <div class="filter-group role-tags-filters">
    <div class="filter-group-title">role</div>
    <div class="filter-tags">
      {% for role_tag in site.data.dynamic_filters.role_tags %}
        {% assign count = site.data.dynamic_filters.role_tag_counts[role_tag] | default: 0 %}
        {% if count > 0 %}
          <a href="#" onclick="filterByTag('{{ role_tag }}'); return false;" class="tag">{{ role_tag }} ({{ count }})</a>
        {% endif %}
      {% endfor %}
    </div>
  </div>
  
  <!-- Language Tags Filters -->
  <div class="filter-group language-tags-filters">
    <div class="filter-group-title">language</div>
    <div class="filter-tags">
      {% for language_tag in site.data.dynamic_filters.language_tags %}
        {% assign count = site.data.dynamic_filters.language_tag_counts[language_tag] | default: 0 %}
        {% if count > 0 %}
          <a href="#" onclick="filterByTag('{{ language_tag }}'); return false;" class="tag">{{ language_tag }} ({{ count }})</a>
        {% endif %}
      {% endfor %}
    </div>
  </div>
  
  <!-- View Map Button -->
  <div class="filter-actions">
    <a href="#" onclick="toggleMap(); return false;" class="view-map-link" id="mapToggleBtn">
      <i class="fas fa-map-marker-alt"></i> view map
    </a>
    <a href="#" onclick="toggleSelectedPublications(); return false;" class="view-map-link" id="selectedToggleBtn">
      <i class="fas fa-eye-slash"></i> hide selected publications
    </a>
  </div>
</div>

<!-- Map Container (initially hidden) -->
<div id="libraryMapContainer" class="library-map-container" style="display: none;">
  <div id="libraryMap" class="library-map"></div>
</div>

<!-- Selected Publications Container -->
<div id="selectedPublicationsContainer" class="selected-publications-container">
  <h2>selected publications</h2>
  {% include selected_papers.liquid %}
</div>

<!-- Item Count Display -->
<div id="itemCountDisplay" class="item-count-display" style="display: none;">
  <span id="itemCountText">showing 0 items</span>
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

.selected-publications-container {
  margin: 2rem 0;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border: 1px solid #e0e0e0;
  background-color: var(--global-bg-color);
}

.selected-publications-container h2 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.5rem;
  color: var(--global-text-color);
}

.filter-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
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

.filter-group.role-tags-filters {
  margin-bottom: 1rem;
}

.filter-group.language-tags-filters {
  margin-bottom: 0.75rem;
}

/* Filter group title styling */
.filter-group-title {
  color: var(--global-text-color);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

/* Additional styling for filter badges and tags to match bibliography behavior */
.library-filters .filter-tags {
  gap: 0 !important; /* Disable gap, using margin instead for more reliable spacing */
  row-gap: 0 !important;
}

.library-filters .filter-tags .badge,
.library-filters .filter-tags .tag {
  cursor: pointer;
  user-select: none;
  text-decoration: none;
  color: inherit;
  background-color: transparent !important;
  box-shadow: none !important;
  margin-right: 0.3rem !important; /* Horizontal spacing between tags */
  margin-bottom: 0.3rem !important; /* Vertical spacing between rows */
  padding: 0.2rem 0.35rem; /* Smaller padding for filter badges */
  font-size: 0.8rem;

  &:hover {
    text-decoration: none;
    color: inherit;
    background-color: transparent !important;
  }

  &:visited {
    color: inherit;
  }

  &.active {
    background-color: transparent !important;
    color: var(--global-theme-color) !important;
    border-color: var(--global-theme-color) !important;
  }
}

/* Restore light grey background for badge-light type filters */
.library-filters .filter-tags .badge.badge-light {
  background-color: #f8f9fa !important;
  color: #495057 !important;
  border: 1px solid #dee2e6 !important;
  
  &:hover {
    background-color: #e9ecef !important;
  }
  
  &.active {
    background-color: #e9ecef !important;
    color: var(--global-theme-color) !important;
    border-color: var(--global-theme-color) !important;
  }
}

/* Marker cluster styling */
.marker-cluster {
  background-color: rgba(102, 187, 106, 0.7);
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
  background-color: rgba(102, 187, 106, 0.7);
  color: white;
}

.marker-cluster-large {
  background-color: rgba(102, 187, 106, 0.7);
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
// Flag to track if we're filtering by badge (exact match) vs manual search (free-form text)
let isBadgeFiltering = false;

// Check for jump action or filter parameter on page load
document.addEventListener('DOMContentLoaded', function() {
  const urlParams = new URLSearchParams(window.location.search);
  const action = urlParams.get('action');
  const filterParam = urlParams.get('filter');
  const hash = window.location.hash;
  
  // Handle filter parameter from library item page links
  if (filterParam) {
    // Wait for page to fully load, then trigger filtering
    setTimeout(() => {
      filterByTag(decodeURIComponent(filterParam));
      // Scroll to top of results
      window.scrollTo({ top: 0, behavior: 'smooth' });
      // Hide selected publications when filter parameter is present
      hideSelectedPublications();
    }, 500);
  }
  
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
  
  // Add listener to search input for item count updates and to detect manual typing
  const searchInput = document.getElementById('bibsearch');
  if (searchInput) {
    // Listen for manual typing (not programmatic badge clicks)
    searchInput.addEventListener('input', function(e) {
      // If this is manual typing (not from badge click), reset badge filtering flag
      // This allows bibsearch.js to do free-form text search
      if (!isBadgeFiltering) {
        // Clear active tags when user manually types (switching to free-form search)
        clearActiveTags();
      }
      
      // Use a small delay to allow the search to process
      setTimeout(() => {
        if (this.value.trim() !== '') {
          updateItemCount();
          // Hide selected publications when user searches
          hideSelectedPublications();
        } else {
          hideItemCount();
          clearActiveTags();
          isBadgeFiltering = false;
          // Show selected publications when search is cleared
          showSelectedPublications();
        }
      }, 100);
    });
    
    // Detect when user manually types (not programmatic value setting)
    let lastValue = searchInput.value;
    searchInput.addEventListener('keydown', function() {
      // User is typing - this is manual input, not badge click
      isBadgeFiltering = false;
      clearActiveTags();
    });
  }
  
  // Filter counts are now pre-calculated during build time and displayed in the template
  // No need to calculate counts dynamically on page load
  
  // Check on page load for active filters/search and hide selected publications if needed
  // Reuse searchInput variable declared on line 358
  if (searchInput && searchInput.value.trim() !== '') {
    hideSelectedPublications();
  }
  
  // Check if any filter tags are active on page load
  const activeTags = document.querySelectorAll('.library-filters .filter-tags a.badge.active, .library-filters .filter-tags a.tag.active');
  if (activeTags.length > 0) {
    hideSelectedPublications();
  }
});

// Filter functions that use exact badge/tag matching for entry types
function filterByTag(tag) {
  const searchInput = document.getElementById('bibsearch');
  if (searchInput) {
    // First, ensure all items are visible by removing unloaded classes
    // This is critical when switching between different filter types
    document.querySelectorAll('.publications .bibliography, .publications .bibliography li, .publications h2.bibliography, .publications ol.bibliography').forEach(element => {
      element.classList.remove('unloaded');
    });
    
    // Check if this is an entry type filter by checking if it matches entry types
    const entryTypes = Array.from(document.querySelectorAll('.entry-type-filters .badge')).map(b => {
      return b.textContent.replace(/\s*\(\d+\)\s*$/, '').trim();
    });
    const isEntryType = entryTypes.includes(tag);
    
    // Check if this is a role tag filter by checking if it matches role tags
    const roleTags = Array.from(document.querySelectorAll('.role-tags-filters .tag')).map(t => {
      return t.textContent.replace(/\s*\(\d+\)\s*$/, '').trim();
    });
    const isRoleTag = roleTags.includes(tag);
    
    if (isEntryType) {
      // For entry types, use exact badge matching to avoid false matches
      // (e.g., "Conference" should not match "Conference Paper" or items with "conference" in title)
      // Set flag to indicate we're doing badge filtering (not free-form text search)
      isBadgeFiltering = true;
      
      // Set the search input value for display purposes
      searchInput.value = tag;
      
      // Use exact badge matching - this will NOT match title text
      filterByExactBadge(tag);
    } else if (isRoleTag) {
      // For role tags, use exact tag matching to avoid false matches
      // (e.g., "author" should not match "co-author")
      isBadgeFiltering = true;
      searchInput.value = tag;
      filterByExactBadge(tag);
    } else {
      // For language tags, use the existing bibsearch infrastructure
      isBadgeFiltering = false;
      searchInput.value = tag;
      // Dispatch input event to trigger bibsearch.js filtering
      searchInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
    
    // Add active state to clicked tag
    setActiveTag(tag);
    
    // Hide selected publications when a filter is applied
    hideSelectedPublications();
    
    // Update item count after a delay to ensure filtering has taken effect
    setTimeout(() => {
      updateItemCount();
    }, 150);
  }
}

// Custom filtering function for entry types that uses exact badge matching
function filterByExactBadge(filterText) {
  const filterLower = filterText.toLowerCase();
  
  // Remove unloaded class from ALL elements first (items, group headers, OL elements)
  // This ensures we start with a clean slate when switching filters
  document.querySelectorAll('.publications .bibliography, .publications .bibliography li, .publications h2.bibliography, .publications ol.bibliography').forEach(element => {
    element.classList.remove('unloaded');
  });
  
  const allItems = document.querySelectorAll('.publications ol.bibliography li');
  
  // Filter items based on exact badge match
  allItems.forEach(item => {
    // Skip group headers
    const hasTitle = item.querySelector('.title');
    const hasAuthor = item.querySelector('.author');
    const hasLinks = item.querySelector('.links');
    const isGroupHeader = !hasTitle && !hasAuthor && !hasLinks;
    
    if (isGroupHeader) {
      return;
    }
    
    // Check if this item matches the filter using exact badge matching
    const matches = itemMatchesFilter(item, filterText);
    
    if (!matches) {
      item.classList.add('unloaded');
    }
  });
  
  // Hide empty groups (same logic as bibsearch.js)
  document.querySelectorAll("h2.bibliography").forEach(function (element) {
    let iterator = element.nextElementSibling;
    let hideFirstGroupingElement = true;
    while (iterator && iterator.tagName !== "H2") {
      if (iterator.tagName === "OL") {
        const ol = iterator;
        const unloadedSiblings = ol.querySelectorAll(":scope > li.unloaded");
        const totalSiblings = ol.querySelectorAll(":scope > li");
        
        if (unloadedSiblings.length === totalSiblings.length) {
          ol.previousElementSibling.classList.add("unloaded");
          ol.classList.add("unloaded");
        } else {
          hideFirstGroupingElement = false;
        }
      }
      iterator = iterator.nextElementSibling;
    }
    if (hideFirstGroupingElement) {
      element.classList.add("unloaded");
    }
  });
}

function clearFilters() {
  const searchInput = document.getElementById('bibsearch');
  if (searchInput) {
    searchInput.value = '';
    // Reset badge filtering flag
    isBadgeFiltering = false;
    // Trigger the input event to clear the search
    searchInput.dispatchEvent(new Event('input', { bubbles: true }));
    // Remove active state from all tags
    clearActiveTags();
    
    // Show selected publications when filters are cleared
    showSelectedPublications();
    
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

// Filter counts are now pre-calculated during build time in the paper processing script
// and displayed directly in the Jekyll template. No JavaScript counting needed.

function itemMatchesFilter(item, filterText) {
  const itemText = item.textContent.toLowerCase();
  const filterLower = filterText.toLowerCase();
  
  // CRITICAL: For single-word filters that are part of compound terms, check badges first
  // This prevents "book" from matching items with "Book Chapter" or "Book Section" badges
  const compoundTermFilters = {
    'book': ['book chapter', 'book section'],
    'conference': ['conference paper'],
    'thesis': ['phd thesis', 'master\'s thesis']
  };
  
  if (compoundTermFilters[filterLower]) {
    // Check badges for compound terms
    const itemTypeBadges = item.querySelectorAll('.item-type-and-roles .badge');
    if (itemTypeBadges.length > 0) {
      const hasCompoundBadge = Array.from(itemTypeBadges).some(badge => {
        const badgeText = badge.textContent.toLowerCase().trim();
        return compoundTermFilters[filterLower].some(term => badgeText === term);
      });
      
      if (hasCompoundBadge) {
        // Item has a compound term badge (e.g., "Book Chapter"), so it should NOT match the simple filter (e.g., "book")
        if (filterLower === 'book') {
          const badgeTexts = Array.from(itemTypeBadges).map(b => b.textContent.trim());
          console.log(`  ✗ Early rejection: Item has compound badge [${badgeTexts.join(', ')}] - cannot match "${filterLower}"`);
        }
        return false;
      }
    }
    
    // Also check item text for compound terms (for items without badges)
    const hasCompoundTermInText = compoundTermFilters[filterLower].some(term => itemText.includes(term));
    if (hasCompoundTermInText) {
      if (filterLower === 'book') {
        const foundTerm = compoundTermFilters[filterLower].find(term => itemText.includes(term));
        console.log(`  ✗ Early rejection: Item text contains compound term "${foundTerm}" - cannot match "${filterLower}"`);
      }
      return false;
    }
  }
  
  // First, check if this is a role tag filter by looking for role tags in the item
  // FIXED: Use correct CSS selector .item-type-and-roles instead of .item-type
  const roleTags = item.querySelectorAll('.item-type-and-roles .tag');
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
    return tagText === filterLower || tagText.includes(filterLower);
  });
  
  if (hasLanguageTag) {
    console.log(`Language tag "${filterLower}" found in item`);
    return true;
  }
  
  // Check for item type badges - this is the primary matching method
  // FIXED: Use correct CSS selector .item-type-and-roles instead of .item-type
  const itemTypeBadges = item.querySelectorAll('.item-type-and-roles .badge');
  
  // CRITICAL: If item has a badge, ONLY match on that badge - never match on title text
  // This ensures "Conference" filter doesn't match items with "conference" in title but "Journal Article" badge
  if (itemTypeBadges.length > 0) {
    const badgeTexts = Array.from(itemTypeBadges).map(b => b.textContent.trim());
    const hasItemTypeBadge = Array.from(itemTypeBadges).some(badge => {
      const badgeText = badge.textContent.toLowerCase().trim();
      // Use case-insensitive exact match - this ensures "Conference" doesn't match "Conference Paper"
      const matches = badgeText === filterLower;
      if (filterLower === 'book') {
        console.log(`  Badge check: "${badgeText}" === "${filterLower}" ? ${matches}`);
      }
      return matches;
    });
    
    if (hasItemTypeBadge) {
      if (filterLower === 'book') {
        console.log(`  ✓ Matched by badge: [${badgeTexts.join(', ')}]`);
      }
      return true;
    } else {
      // Item has a badge but it doesn't match - return false immediately
      // Do NOT check title text or patterns - badges are the source of truth
      if (filterLower === 'book') {
        console.log(`  ✗ Badge mismatch: [${badgeTexts.join(', ')}] !== "${filterLower}" - returning false`);
      }
      return false;
    }
  }
  
  // Pattern matching as fallback ONLY for items without badges
  // This handles legacy items or items that might not have badges rendered
  // IMPORTANT: Patterns should NOT overlap - each filter should have distinct patterns
  const patterns = {
    // Standard BibTeX entry types - proper multiword names
    'journal article': ['journal article', 'article'],
    // FIXED: Remove overlapping patterns - "Conference Paper" should only match "conference paper" or "inproceedings"
    'conference paper': ['conference paper', 'inproceedings'],
    // FIXED: "Conference" should only match "conference" (not "conference paper")
    'conference': ['conference'],
    'book chapter': ['book chapter', 'incollection'],
    'book section': ['book section', 'inbook'],
    'phd thesis': ['phd thesis', 'ph.d. thesis', 'phdthesis'],
    'master\'s thesis': ['master\'s thesis', 'master thesis', 'mastersthesis'],
    'thesis': ['thesis'],
    'report': ['report', 'techreport'],
    'briefing note': ['briefing note'],
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
  
  // Only use pattern matching if no badge was found
  // This prevents double-counting and ensures badges are the source of truth
  if (patterns[filterLower]) {
    // For single-word filters that could be part of compound terms (like "book" in "book chapter"),
    // check for compound terms BEFORE pattern matching to avoid false positives
    const compoundTerms = {
      'book': ['book chapter', 'book section'],
      'conference': ['conference paper'],
      'thesis': ['phd thesis', 'master\'s thesis']
    };
    
    // If this filter has compound terms, check if item contains any of them
    if (compoundTerms[filterLower]) {
      const hasCompoundTerm = compoundTerms[filterLower].some(term => itemText.includes(term));
      if (hasCompoundTerm) {
        // Item contains a compound term, so don't match the single word pattern
        // Return false immediately - don't continue to fallback matching
        const foundTerm = compoundTerms[filterLower].find(term => itemText.includes(term));
        if (filterLower === 'book') {
          console.log(`  ✗ Pattern match skipped - item contains compound term: "${foundTerm}"`);
        }
        return false;
      } else {
        // No compound term found, proceed with pattern matching
        const patternMatches = patterns[filterLower].some(pattern => {
          const matches = itemText.includes(pattern);
          if (matches) {
            console.log(`Pattern "${pattern}" matched in item text (no badge found)`);
          }
          return matches;
        });
        if (patternMatches) {
          return true;
        }
      }
    } else {
      // No compound terms to worry about, proceed with normal pattern matching
      const patternMatches = patterns[filterLower].some(pattern => {
        const matches = itemText.includes(pattern);
        if (matches) {
          console.log(`Pattern "${pattern}" matched in item text (no badge found)`);
        }
        return matches;
      });
      if (patternMatches) {
        return true;
      }
    }
  }
  
  // Final fallback: check if filter text appears anywhere in item text
  // Only use this if no badge was found (to avoid false matches)
  // For single-word filters that could be part of compound terms (like "book" in "book chapter"),
  // use word boundaries to ensure we only match standalone words
  const isSingleWord = !filterLower.includes(' ');
  const compoundTerms = {
    'book': ['book chapter', 'book section'],
    'conference': ['conference paper'],
    'thesis': ['phd thesis', 'master\'s thesis']
  };
  
  let simpleMatch = false;
  if (isSingleWord && compoundTerms[filterLower]) {
    // Check if filter text appears as a standalone word (not part of compound terms)
    const compoundPatterns = compoundTerms[filterLower];
    const hasCompoundTerm = compoundPatterns.some(term => itemText.includes(term));
    
    if (!hasCompoundTerm) {
      // Use word boundary regex to match standalone word
      const wordBoundaryRegex = new RegExp(`\\b${filterLower}\\b`);
      simpleMatch = wordBoundaryRegex.test(itemText);
    } else {
      // Item contains a compound term, so don't match the single word
      simpleMatch = false;
    }
  } else {
    // For multi-word filters or filters without compound terms, use simple includes
    simpleMatch = itemText.includes(filterLower);
  }
  
  if (simpleMatch) {
    console.log(`Simple text match for "${filterLower}" (no badge found)`);
    return true;
  }
  
  return false;
}

function updateItemCount() {
  const countDisplay = document.getElementById('itemCountDisplay');
  const countText = document.getElementById('itemCountText');
  
  if (countDisplay && countText) {
    // Get the count from the active filter button (which contains pre-calculated count from YAML)
    const activeButton = document.querySelector('.library-filters .filter-tags a.badge.active, .library-filters .filter-tags a.tag.active');
    
    if (activeButton) {
      // Extract count from button text (e.g., "Book (2)" -> 2)
      const buttonText = activeButton.textContent.trim();
      const countMatch = buttonText.match(/\((\d+)\)/);
      
      if (countMatch) {
        const count = parseInt(countMatch[1], 10);
        countText.textContent = `showing ${count} item${count !== 1 ? 's' : ''}`;
        countDisplay.classList.add('show');
        countDisplay.style.display = 'block';
        return;
      }
    }
    
    // Fallback: if no active filter, count visible items (for search queries)
    const visibleItems = document.querySelectorAll('.publications ol.bibliography li:not(.unloaded):not([style*="display: none"])');
    
    // Filter out group headers - they typically don't have the full bibliography structure
    const actualItems = Array.from(visibleItems).filter(item => {
      const hasTitle = item.querySelector('.title');
      const hasAuthor = item.querySelector('.author');
      const hasLinks = item.querySelector('.links');
      return hasTitle || hasAuthor || hasLinks;
    });
    
    const count = actualItems.length;
    
    if (count > 0) {
      countText.textContent = `showing ${count} item${count !== 1 ? 's' : ''}`;
      countDisplay.classList.add('show');
      countDisplay.style.display = 'block';
    } else {
      hideItemCount();
    }
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
  
  if (!mapContainer || !toggleBtn) return;
  
  const isHidden = mapContainer.style.display === 'none' || 
                   window.getComputedStyle(mapContainer).display === 'none';
  
  if (isHidden) {
    mapContainer.style.display = 'block';
    toggleBtn.innerHTML = '<i class="fas fa-map-marker-alt"></i> hide map';
    
    // Initialize map if not already done
    if (!mapInitialized) {
      initializeLibraryMap();
    }
  } else {
    mapContainer.style.display = 'none';
    toggleBtn.innerHTML = '<i class="fas fa-map-marker-alt"></i> view map';
  }
}

// Selected publications toggle functionality
function toggleSelectedPublications() {
  const container = document.getElementById('selectedPublicationsContainer');
  const toggleBtn = document.getElementById('selectedToggleBtn');
  
  if (!container || !toggleBtn) return;
  
  const isHidden = container.style.display === 'none' || 
                   window.getComputedStyle(container).display === 'none';
  
  if (isHidden) {
    container.style.display = 'block';
    toggleBtn.innerHTML = '<i class="fas fa-eye-slash"></i> hide selected publications';
  } else {
    container.style.display = 'none';
    toggleBtn.innerHTML = '<i class="fas fa-eye"></i> show selected publications';
  }
}

// Helper function to hide selected publications container
function hideSelectedPublications() {
  const container = document.getElementById('selectedPublicationsContainer');
  const toggleBtn = document.getElementById('selectedToggleBtn');
  
  if (container && toggleBtn) {
    container.style.display = 'none';
    toggleBtn.innerHTML = '<i class="fas fa-eye"></i> show selected publications';
  }
}

// Helper function to show selected publications container
function showSelectedPublications() {
  const container = document.getElementById('selectedPublicationsContainer');
  const toggleBtn = document.getElementById('selectedToggleBtn');
  
  if (container && toggleBtn) {
    container.style.display = 'block';
    toggleBtn.innerHTML = '<i class="fas fa-eye-slash"></i> hide selected publications';
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
        iconSize: L.point(40, 40),
        iconAnchor: L.point(20, 20)
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
  // Use custom Zotero tag if available, otherwise fall back to entry_type
  const eventType = conf.tag || formatEventType(conf.entry_type);
  
  return `
    <div class="popup-content">
      <div class="popup-title">${escapeHtml(conf.title)}</div>
      <div class="popup-details">
        <div class="popup-detail">
          <i class="fas fa-calendar"></i> ${date}
        </div>
        <div class="popup-detail">
          <i class="fas fa-tag"></i> ${escapeHtml(eventType)}
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
