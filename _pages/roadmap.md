---
layout: page
permalink: /roadmap/
title: roadmap
#description:
#nav: false
#nav_order:
render_with_liquid: false #turned off so as to not break on render
---

````markdown
# Publications Tagging System - Project Roadmap

## 📚 Library

**Priority**: MEDIUM - Organization and accessibility improvements
**Objective**: Streamline library management and enhance event organization

### To-Do Items

#### Processing Script Finalization

- [ ] **Complete PDF processing automation** for new publications
- [ ] **Implement automatic thumbnail generation** for publication previews
- [ ] **Add metadata extraction** from PDFs (title, authors, abstract)
- [ ] **Create backup and versioning system** for processed files
- [ ] **Test end-to-end workflow** with sample publications

#### Multilingual PDF Filenames & Library Display (Future Enhancement)

**Current State**: When a single bibliographic entry has multiple PDFs (e.g., different language versions), the system appends sequential suffixes (`_a`, `_b`, `_c`) to the base English filename to avoid collisions.

**Planned Enhancement**: Improve handling of multilingual publications:
- [ ] **Language-aware filename generation** - Generate filenames using the actual language of each PDF (e.g., Spanish title for Spanish version, French title for French version)
- [ ] **Enhanced library page rendering** - Better visual delineation of language variants on the library page (e.g., language badges, grouped display, language selector)
- [ ] **Language detection** - Automatically detect PDF language from metadata or content
- [ ] **Consistent language tagging** - Add language tags to BibTeX entries for multilingual publications
- [ ] **Improved user experience** - Make it clear when multiple language versions are available and allow easy switching between them

**Use Cases**:
- Publications with Spanish, French, and English versions should have filenames reflecting their actual language
- Library page should clearly show when multiple language versions exist
- Users should be able to easily identify and access their preferred language version

#### Zotero Presentations Cleanup

- [ ] **Review and categorize** all presentation entries in Zotero
- [ ] **Standardize presentation metadata** (conference names, dates, locations)
- [ ] **Add consistent tags** for presentation types and topics
- [ ] **Remove duplicate entries** and merge related presentations
- [ ] **Export cleaned presentation data** to website structure

#### Event Agenda Buttons

- [ ] **Design agenda button components** for event pages
- [ ] **Implement interactive agenda display** with expandable sections
- [ ] **Add calendar integration** for event scheduling
- [ ] **Create mobile-responsive** agenda layouts
- [ ] **Test agenda functionality** across different event types

#### Content Export & Migration

- [ ] **Export books from Goodreads/Google Books sheet** - Migrate reading list data
- [ ] **Export old newsletters** - Archive and organize historical newsletter content
- [ ] **Export old blog posts** - Migrate legacy blog content to current structure

#### Filter Engine Refactor

**Current State**: Library page filters are non-cumulative - only one filter can be active at a time. Users cannot combine filters (e.g., "Conferences where I've facilitated" or "Workshops I've organized").

**Planned Enhancement**: Refactor the filter engine to support cumulative/multi-select filtering:
- [ ] **Refactor filter state management** - Track multiple active filters across categories (entry types, roles, languages)
- [ ] **Implement toggle behavior** - Allow users to activate/deactivate multiple filters simultaneously
- [ ] **Update filtering logic** - Apply AND logic so items must match all active filters
- [ ] **Enhance UI feedback** - Show multiple active filter states and update search input display
- [ ] **Update filter counts** - Consider showing counts for filter combinations
- [ ] **Maintain backward compatibility** - Ensure single-filter behavior still works correctly

**Use Cases**:
- Filter by "Conference" (entry type) + "facilitator" (role) to find conferences where user facilitated
- Filter by "Workshop" (entry type) + "organiser" (role) to find workshops user organized
- Combine any entry type with role or language tags for precise filtering

### Implementation Timeline

- **Week 1**: Processing script finalization
- **Week 2**: Zotero presentations cleanup
- **Week 3**: Event agenda button development
- **Week 4**: Content export and migration
- **Week 5**: Testing and integration

---

## 🚨 URGENT: Zotero Postprocessing System

**Priority**: URGENT - Blocking publication workflow
**Objective**: Automate the complete publication pipeline from Zotero export to website integration

**Current Problem**:

- Zotero export only creates `papers.bib` file
- PDFs are not automatically saved to website structure
- Missing tags/keywords for filtering
- No automatic thumbnail generation for publication previews

**Target State**: Fully automated pipeline that:

1. Exports from Zotero with complete metadata
2. Adds structured tags to all bib entries
3. Downloads and organizes PDFs in website directory
4. Generates publication preview thumbnails
5. Links everything correctly for seamless website integration

### Zotero Postprocessing Implementation Steps

#### Phase 1: Zotero Export Enhancement (Week 1)

- [ ] **Configure Zotero Better BibTeX plugin** for enhanced export
- [ ] **Set up custom export format** with structured tags
- [ ] **Create tag taxonomy** for consistent categorization
- [ ] **Test export workflow** with sample publications

#### Phase 2: PDF Management System (Week 1-2)

- [ ] **Create PDF download script** that processes Zotero export
- [ ] **Set up directory structure** for organized PDF storage
- [ ] **Implement PDF naming convention** for consistency
- [ ] **Add PDF metadata extraction** for additional information

#### Phase 3: Tagging Automation (Week 2)

- [ ] **Develop tag assignment logic** based on publication content
- [ ] **Create tag validation system** to ensure consistency
- [ ] **Implement bulk tagging** for existing publications
- [ ] **Set up tag maintenance workflow** for new publications

#### Phase 4: Thumbnail Generation (Week 2-3)

- [ ] **Create PDF thumbnail generator** using first page
- [ ] **Implement image optimization** for web display
- [ ] **Set up thumbnail storage** in assets structure
- [ ] **Test thumbnail integration** with publication pages

#### Phase 5: Integration & Testing (Week 3)

- [ ] **Test complete pipeline** end-to-end
- [ ] **Validate all links** and file references
- [ ] **Performance testing** for large publication sets
- [ ] **Documentation** of complete workflow

### Technical Requirements

#### Zotero Configuration

- Better BibTeX plugin installation
- Custom export format with tags
- PDF attachment handling
- Metadata completeness validation

#### Scripting Requirements

- Python script for PDF processing
- Tag management and validation
- Thumbnail generation (PIL/Pillow)
- File organization and linking

---

## 📚 Paper Processing Script Enhancements

**Priority**: HIGH - Improves publication metadata quality
**Objective**: Automatically enhance bibliography entries with rich metadata from academic databases

**Current State**:

- Basic PDF processing and thumbnail generation working
- DOI finding integrated into paper processing pipeline
- Automatic backup system implemented

**Target State**: Enhanced pipeline that automatically populates:

1. **Abstracts** from Crossref/Semantic Scholar
2. **Keywords** from academic databases
3. **ISSN/ISBN** from Crossref
4. **Citation counts** and impact metrics
5. **Enhanced author information** and ORCIDs

### Implementation Phases

#### Phase 1: Core Metadata Enhancement ✅ COMPLETED

- [x] **DOI finding integration** - Integrated into paper processing script
- [x] **Abstract extraction** - From Crossref API
- [x] **Keyword extraction** - From Crossref subject fields
- [x] **ISSN/ISBN extraction** - From Crossref metadata
- [x] **Volume/issue/pages** - From Crossref publication details
- [x] **Automatic backup system** - Before any modifications
- [x] **Rate limiting** - Respects API limits (Crossref: 1s, Semantic Scholar: 0.5s)

#### Phase 2: Citation Metrics & Author Info (Next)

- [ ] **Citation counts** - From Semantic Scholar API
- [ ] **Altmetric scores** - Social media and news mentions
- [ ] **ORCID integration** - Author identifier lookup
- [ ] **Affiliation data** - Institution information
- [ ] **Co-author networks** - Collaboration mapping

#### Phase 3: Advanced Classification (Future)

- [ ] **Subject classification** - Academic taxonomy mapping
- [ ] **Research methodology** - Method classification
- [ ] **Geographic scope** - Regional coverage analysis
- [ ] **Funding information** - Grant and funding details
- [ ] **Data availability** - Repository and dataset links

### Technical Implementation

#### API Integration

- **Crossref API**: Primary source for published papers (free, no auth)
- **Semantic Scholar API**: Secondary source for citations and altmetrics (free, no auth)
- **Rate limiting**: Prevents API blocking and ensures reliable operation

#### Metadata Fields Added

```bibtex
abstract = {Paper abstract from academic databases}
keywords = {Automatically extracted subject keywords}
issn = {International Standard Serial Number}
isbn = {International Standard Book Number}
citation_count = {Number of academic citations}
doi_updated = {true}  # Flag for newly added DOIs
```
````

#### Script Usage

```bash
# Run with metadata enhancement (default)
python3 process_papers.py

# Skip metadata enhancement
python3 process_papers.py --skip-doi-finding

# Metadata-only mode (skip PDF/thumbnail processing)
python3 process_papers.py --metadata-only

# Verbose output for debugging
python3 process_papers.py --verbose

# Control backup behavior
python3 process_papers.py --no-backup --keep-backups 10
```

### Benefits

- **Richer metadata**: Abstracts and keywords improve searchability
- **Standard identifiers**: ISSN/ISBN for proper journal/book identification
- **Impact tracking**: Citation counts show research influence
- **Automated workflow**: No manual metadata entry required
- **Data quality**: Consistent formatting and completeness

#### Directory Structure

```
assets/
├── pdf/
│   ├── publications/
│   │   ├── 2024/
│   │   ├── 2023/
│   │   └── ...
├── img/
│   └── publication_preview/
│       ├── 2024/
│       ├── 2023/
│       └── ...
```

#### Tag Structure

```yaml
# Publication Type
type: [journal_article, conference_paper, report, book_chapter, working_paper]

# Research Area
topic: [ocean, energy, climate, policy, governance, technology]

# Author Role
role: [lead_author, co_author, editor, contributor]

# Geographic Focus
region: [global, europe, north_america, asia_pacific, africa]

# Methodology
method: [qualitative, quantitative, mixed, review, case_study]
```

---

## Publications Tagging System - Project Roadmap

## Project Overview

**Objective**: Implement a comprehensive tagging and filtering system for the publications page to enhance discoverability and user experience.

**Current State**: Publications page (`/writing/`) has basic text search functionality using Jekyll Scholar and `papers.bib`, but lacks structured categorization and multi-criteria filtering.

**Target State**: Publications page with tag-based filtering, multi-tag selection, integrated search, and visual tag management system.

---

## Project Structure

### Phase 1: Foundation & Planning (Week 1)

- [ ] Requirements finalization
- [ ] Tag taxonomy design
- [ ] Technical architecture planning
- [ ] Migration strategy development

### Phase 2: Data Structure & Configuration (Week 2)

- [ ] Extend BibTeX structure
- [ ] Update configuration files
- [ ] Create tag management system
- [ ] Sample data preparation

### Phase 3: Core Functionality (Weeks 3-4)

- [ ] Tag parsing and extraction
- [ ] Filtering engine development
- [ ] Search integration
- [ ] URL state management

### Phase 4: User Interface (Weeks 5-6)

- [ ] Tag cloud component
- [ ] Filter controls
- [ ] Active tag display
- [ ] Responsive design

### Phase 5: Testing & Optimization (Week 7)

- [ ] Functionality testing
- [ ] Performance optimization
- [ ] Cross-browser compatibility
- [ ] User experience refinement

### Phase 6: Documentation & Deployment (Week 8)

- [ ] User documentation
- [ ] Technical documentation
- [ ] Migration guide
- [ ] Production deployment

---

## Detailed Implementation Plan

### 1. Tag Taxonomy Design

#### 1.1 Tag Categories

```yaml
# Three main tag categories with specific values:

types:
  - journal_article # Peer-reviewed journal publications
  - submission # Submitted manuscripts
  - report # Policy reports, technical reports
  - blog # Blog posts, opinion pieces
  - presentation # Conference presentations, talks
  - workshop # Workshop materials, proceedings

roles:
  - lead_author # Primary author responsibility
  - co_author # Contributing author
  - editor # Editorial role
  - facilitator # Workshop/conference facilitation
  - speaker # Presentation delivery
  - group_author # Part of collaborative authorship

topics:
  - ocean # Marine/ocean-related research
  - energy # Energy policy and technology
  - academia # Academic research and policy
  - climate # Climate change and policy
  - law # Legal and regulatory aspects
  - policy # Policy analysis and recommendations
  - governance # Governance and institutional aspects
  - technology # Technology and innovation
  - sustainability # Sustainable development
  - international # International relations and cooperation
```

#### 1.2 Tag Naming Conventions

- Use snake_case for all tag values
- Keep tags concise but descriptive
- Avoid abbreviations unless universally understood
- Maintain consistency across categories

### 2. Technical Architecture

#### 2.1 Data Flow

```
papers.bib → Jekyll Scholar → Liquid Templates → JavaScript Engine → DOM Updates
     ↓              ↓              ↓              ↓              ↓
Tag Fields → Tag Extraction → Tag Rendering → Filter Logic → Filtered Display
```

#### 2.2 Component Structure

```
bib_search.liquid (Main Interface)
├── tag_cloud.liquid (Tag Display)
├── filter_controls.liquid (Search + Tag Controls)
├── active_tags.liquid (Selected Tags Display)
└── bibsearch.js (Core Logic)
    ├── TagManager (Tag parsing and management)
    ├── FilterEngine (Search and filter logic)
    ├── URLManager (State persistence)
    └── UIManager (DOM updates and interactions)
```

### 3. Implementation Details

#### 3.1 BibTeX Structure Extension

**Current Structure:**

```bibtex
@article{Example2024,
  title = {Example Title},
  author = {Author, A.},
  year = {2024},
  keywords = {existing, keywords}
}
```

**Extended Structure:**

```bibtex
@article{Example2024,
  title = {Example Title},
  author = {Author, A.},
  year = {2024},
  keywords = {existing, keywords},
  type_tags = {journal_article, report},
  role_tags = {lead_author},
  topic_tags = {ocean, climate, policy}
}
```

#### 3.2 Configuration Updates

**Add to \_config.yml:**

```yaml
# Publication Tag System Configuration
publication_tags:
  enabled: true

  # Tag categories and their display names
  categories:
    types:
      label: "Publication Type"
      values: ["journal_article", "submission", "report", "blog", "presentation", "workshop"]
    roles:
      label: "Author Role"
      values: ["lead_author", "co_author", "editor", "facilitator", "speaker", "group_author"]
    topics:
      label: "Research Topics"
      values: ["ocean", "energy", "academia", "climate", "law", "policy", "governance", "technology", "sustainability", "international"]

  # Display settings
  display:
    show_tag_cloud: true
    show_active_tags: true
    max_tags_per_category: 10
    tag_cloud_style: "cloud" # cloud, list, or pills

  # Filtering behavior
  filtering:
    default_logic: "AND" # AND or OR between different categories
    same_category_logic: "OR" # AND or OR within same category
    preserve_text_search: true
```

#### 3.3 Liquid Template Updates

**Update \_includes/bib_search.liquid:**

```liquid
{% if site.publication_tags.enabled %}
  <div class="publication-tag-system">
    <!-- Tag Cloud -->
    {% include tag_cloud.liquid %}

    <!-- Search and Filter Controls -->
    {% include filter_controls.liquid %}

    <!-- Active Tags Display -->
    {% include active_tags.liquid %}
  </div>

  <!-- Enhanced Search Script -->
  <script src="{{ '/assets/js/enhanced_bibsearch.js' | relative_url | bust_file_cache }}" type="module"></script>
{% else %}
  <!-- Fallback to original search -->
  {% include bib_search.liquid %}
{% endif %}
```

**Create \_includes/tag_cloud.liquid:**

```liquid
<div class="tag-cloud-container">
  <h3>Filter by Tags</h3>

  {% for category in site.publication_tags.categories %}
    <div class="tag-category">
      <h4>{{ category[1].label }}</h4>
      <div class="tag-list">
        {% for tag in category[1].values %}
          <button class="tag-btn" data-category="{{ category[0] }}" data-tag="{{ tag }}">
            {{ tag | replace: '_', ' ' | titleize }}
          </button>
        {% endfor %}
      </div>
    </div>
  {% endfor %}
</div>
```

#### 3.4 JavaScript Implementation

**Create assets/js/enhanced_bibsearch.js:**

```javascript
import { TagManager } from "./modules/TagManager.js";
import { FilterEngine } from "./modules/FilterEngine.js";
import { URLManager } from "./modules/URLManager.js";
import { UIManager } from "./modules/UIManager.js";

class EnhancedBibSearch {
  constructor() {
    this.tagManager = new TagManager();
    this.filterEngine = new FilterEngine();
    this.urlManager = new URLManager();
    this.uiManager = new UIManager();

    this.initialize();
  }

  initialize() {
    this.setupEventListeners();
    this.loadInitialState();
    this.renderTagCloud();
  }

  setupEventListeners() {
    // Tag button clicks
    document.addEventListener("click", (e) => {
      if (e.target.classList.contains("tag-btn")) {
        this.handleTagClick(e.target);
      }
    });

    // Search input
    const searchInput = document.getElementById("enhanced-bibsearch");
    if (searchInput) {
      searchInput.addEventListener(
        "input",
        this.debounce((e) => {
          this.handleSearchInput(e.target.value);
        }, 300)
      );
    }

    // Clear button
    const clearBtn = document.getElementById("clear-filters");
    if (clearBtn) {
      clearBtn.addEventListener("click", () => this.clearAllFilters());
    }
  }

  handleTagClick(tagButton) {
    const category = tagButton.dataset.category;
    const tag = tagButton.dataset.tag;

    this.tagManager.toggleTag(category, tag);
    this.updateFilters();
    this.updateUI();
  }

  handleSearchInput(searchTerm) {
    this.filterEngine.setTextSearch(searchTerm);
    this.updateFilters();
  }

  updateFilters() {
    const activeTags = this.tagManager.getActiveTags();
    const searchTerm = this.filterEngine.getTextSearch();

    this.filterEngine.applyFilters(activeTags, searchTerm);
    this.urlManager.updateURL(activeTags, searchTerm);
  }

  updateUI() {
    this.uiManager.updateTagCloud(this.tagManager.getActiveTags());
    this.uiManager.updateActiveTagsDisplay(this.tagManager.getActiveTags());
    this.uiManager.updatePublicationCount(this.filterEngine.getVisibleCount());
  }

  clearAllFilters() {
    this.tagManager.clearAllTags();
    this.filterEngine.clearTextSearch();
    this.updateFilters();
    this.updateUI();
  }

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
}

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  new EnhancedBibSearch();
});
```

### 4. Migration Strategy

#### 4.1 Phase 1: Preparation

- [ ] Backup current `papers.bib`
- [ ] Create tag mapping for existing publications
- [ ] Test tag parsing with sample entries

#### 4.2 Phase 2: Gradual Rollout

- [ ] Start with 10-20 most important publications
- [ ] Add tags to new publications as they're added
- [ ] Gradually tag remaining publications over time

#### 4.3 Phase 3: Validation

- [ ] Test filtering with tagged publications
- [ ] Verify search integration works correctly
- [ ] Check URL state management

### 5. Testing Strategy

#### 5.1 Unit Testing

- [ ] Tag parsing and validation
- [ ] Filter logic correctness
- [ ] URL state management
- [ ] Search integration

#### 5.2 Integration Testing

- [ ] End-to-end filtering workflows
- [ ] Cross-browser compatibility
- [ ] Mobile responsiveness
- [ ] Performance under load

#### 5.3 User Testing

- [ ] Tag discovery and usage
- [ ] Filter combination logic
- [ ] Search and tag integration
- [ ] Overall user experience

### 6. Performance Considerations

#### 6.1 Optimization Strategies

- **Lazy Loading**: Load tag data only when needed
- **Debounced Search**: Prevent excessive API calls
- **Caching**: Cache parsed tag data in localStorage
- **Virtual Scrolling**: For large publication lists

#### 6.2 Monitoring

- **Search Performance**: Track filter response times
- **Memory Usage**: Monitor tag data memory footprint
- **User Behavior**: Track most used tag combinations

### 7. Future Enhancements

#### 7.1 Advanced Features

- **Tag Suggestions**: AI-powered tag recommendations
- **Tag Analytics**: Usage statistics and trends
- **Export Functionality**: Filtered publication lists
- **Social Sharing**: Share filtered publication views

#### 7.2 Integration Opportunities

- **Academic APIs**: Integration with citation databases
- **Social Media**: Share publications with relevant tags
- **Newsletter Integration**: Tag-based publication digests

---

## Success Metrics

### Technical Metrics

- [ ] Filter response time < 100ms
- [ ] 100% cross-browser compatibility
- [ ] Mobile performance score > 90
- [ ] Zero JavaScript errors in production

### User Experience Metrics

- [ ] Tag usage rate > 60% of visitors
- [ ] Average filter combinations > 2 per session
- [ ] Search + tag combination usage > 40%
- [ ] User satisfaction score > 4.5/5

### Content Metrics

- [ ] 80% of publications tagged within 3 months
- [ ] Tag coverage across all categories > 70%
- [ ] Consistent tag usage across similar publications

---

## Risk Assessment & Mitigation

### High Risk

- **Performance Impact**: Large publication lists may slow down filtering
  - _Mitigation_: Implement virtual scrolling and lazy loading
- **Browser Compatibility**: Complex JavaScript may not work in older browsers
  - _Mitigation_: Progressive enhancement and fallback support

### Medium Risk

- **Tag Inconsistency**: Users may apply tags inconsistently
  - _Mitigation_: Tag validation and suggestion system
- **Migration Complexity**: Large number of existing publications
  - _Mitigation_: Gradual rollout and automated tagging tools

### Low Risk

- **User Adoption**: Users may not immediately understand the system
  - _Mitigation_: Clear documentation and onboarding

---

## Timeline Summary

| Week | Phase              | Deliverables                                | Dependencies      |
| ---- | ------------------ | ------------------------------------------- | ----------------- |
| 1    | Foundation         | Requirements, Architecture, Migration Plan  | None              |
| 2    | Data Structure     | Extended BibTeX, Configuration, Sample Data | Week 1 completion |
| 3-4  | Core Functionality | Tag Engine, Filtering, Search Integration   | Week 2 completion |
| 5-6  | User Interface     | Tag Cloud, Controls, Responsive Design      | Week 4 completion |
| 7    | Testing            | Functionality, Performance, UX Testing      | Week 6 completion |
| 8    | Documentation      | User Guides, Technical Docs, Deployment     | Week 7 completion |

**Total Duration**: 8 weeks
**Team Size**: 1-2 developers
**Effort Estimate**: 120-160 hours

---

## Next Steps

1. **Immediate Actions** (This Week)

   - [ ] Review and approve this roadmap
   - [ ] Finalize tag taxonomy
   - [ ] Set up development environment

2. **Week 1 Deliverables**

   - [ ] Tag taxonomy document
   - [ ] Technical architecture diagram
   - [ ] Migration strategy document

3. **Resource Requirements**
   - [ ] Development environment setup
   - [ ] Access to current codebase
   - [ ] Sample publication data for testing

---

## Detailed Implementation Instructions (Option 1: Jekyll Archives)

### Phase 1: Configuration Setup (30 minutes)

#### Step 1.1: Enable Jekyll Archives for Publications

**File**: `_config.yml`
**Location**: Around line 265 (Jekyll Archives section)

**Current State**:

```yaml
# jekyll-archives:
#   posts:
#     enabled: [year, tags, categories]
#     permalinks:
#       year: "/blog/:year/"
#       tags: "/blog/:type/:name/"
#       categories: "/blog/:type/:name/"
#   books:
#     enabled: [year, tags, categories]
#     permalinks:
#       year: "/books/:year/"
#       tags: "/books/:type/:name/"
#       categories: "/books/:type/:name/"
```

**Updated Configuration**:

```yaml
jekyll-archives:
  posts:
    enabled: [year, tags, categories]
    permalinks:
      year: "/blog/:year/"
      tags: "/blog/:type/:name/"
      categories: "/blog/:type/:name/"
  books:
    enabled: [year, tags, categories]
    permalinks:
      year: "/books/:year/"
      tags: "/books/:type/:name/"
      categories: "/books/:type/:name/"
  # NEW SECTION FOR PUBLICATIONS
  publications:
    enabled: [year, tags, categories]
    permalinks:
      year: "/writing/:year/"
      tags: "/writing/:type/:name/"
      categories: "/writing/:type/:name/"
```

#### Step 1.2: Add Publication Tag Configuration

**File**: `_config.yml`
**Location**: After the Jekyll Scholar section (around line 350)

**Add This Configuration**:

```yaml
# Publication Tag System Configuration
publication_tags:
  enabled: true

  # Tag categories and their display names
  categories:
    types:
      label: "Publication Type"
      values: ["journal_article", "submission", "report", "blog", "presentation", "workshop"]
    roles:
      label: "Author Role"
      values: ["lead_author", "co_author", "editor", "facilitator", "speaker", "group_author"]
    topics:
      label: "Research Topics"
      values: ["ocean", "energy", "academia", "climate", "law", "policy", "governance", "technology", "sustainability", "international"]

  # Display settings
  display:
    show_tag_cloud: true
    show_active_tags: true
    max_tags_per_category: 10
    tag_cloud_style: "pills" # cloud, list, or pills

  # Filtering behavior
  filtering:
    default_logic: "AND" # AND or OR between different categories
    same_category_logic: "OR" # AND or OR within same category
    preserve_text_search: true
```

### Phase 2: BibTeX Structure Updates (1-2 hours)

#### Step 2.1: Tag Format Convention

**Use existing `keywords` field with structured format**:

```bibtex
keywords = {type:journal_article, role:lead_author, topic:ocean, topic:climate}
```

**Tag Format Rules**:

- `category:value` format (e.g., `type:journal_article`)
- Multiple values of same category separated by commas
- Use snake_case for all values
- Keep existing keywords if they exist

#### Step 2.2: Sample Publications to Tag First

**Start with these 5-10 publications for testing**:

1. **Ocean-related journal articles**:

```bibtex
@article{Wright2011a,
  title = {Marine energy},
  keywords = {type:journal_article, role:lead_author, topic:ocean, topic:energy, wave energy, New Zealand, tidal energy},
  # ... rest of entry
}
```

2. **Climate policy reports**:

```bibtex
@article{Wright2010,
  title = {Designing Climate Law: A Comparative Analysis of the US and EU},
  keywords = {type:journal_article, role:lead_author, topic:climate, topic:law, topic:policy, US, EU, Kyoto Protocol},
  # ... rest of entry
}
```

3. **Workshop presentations**:

```bibtex
@inproceedings{Example2024,
  title = {Example Workshop Presentation},
  keywords = {type:workshop, role:facilitator, topic:ocean, topic:governance},
  # ... rest of entry
}
```

#### Step 2.3: Batch Tagging Script

**Create a simple script to help with tagging** (optional):

**File**: `scripts/tag_publications.py`

```python
#!/usr/bin/env python3
"""
Simple script to help tag publications in papers.bib
Usage: python scripts/tag_publications.py
"""

import re
import sys

def suggest_tags(title, abstract=""):
    """Suggest tags based on title and abstract content"""
    title_lower = title.lower()
    abstract_lower = abstract.lower()

    suggestions = []

    # Type suggestions
    if any(word in title_lower for word in ['journal', 'article', 'paper']):
        suggestions.append('type:journal_article')
    elif any(word in title_lower for word in ['report', 'study']):
        suggestions.append('type:report')
    elif any(word in title_lower for word in ['blog', 'post']):
        suggestions.append('type:blog')
    elif any(word in title_lower for word in ['presentation', 'talk']):
        suggestions.append('type:presentation')
    elif any(word in title_lower for word in ['workshop', 'conference']):
        suggestions.append('type:workshop')

    # Topic suggestions
    if any(word in title_lower for word in ['ocean', 'marine', 'sea']):
        suggestions.append('topic:ocean')
    if any(word in title_lower for word in ['energy', 'renewable']):
        suggestions.append('topic:energy')
    if any(word in title_lower for word in ['climate', 'warming']):
        suggestions.append('topic:climate')
    if any(word in title_lower for word in ['law', 'legal', 'regulation']):
        suggestions.append('topic:law')
    if any(word in title_lower for word in ['policy', 'governance']):
        suggestions.append('topic:policy')

    # Role suggestions (default to lead_author)
    suggestions.append('role:lead_author')

    return suggestions

def main():
    print("Publication Tagging Helper")
    print("=" * 40)
    print()

    # Read papers.bib
    try:
        with open('_bibliography/papers.bib', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: papers.bib not found in _bibliography/ directory")
        sys.exit(1)

    # Find all entries
    entries = re.findall(r'@(\w+)\{([^,]+),\s*\n(.*?)\n\}', content, re.DOTALL)

    print(f"Found {len(entries)} publications")
    print()

    for entry_type, key, fields in entries[:5]:  # Show first 5
        # Extract title
        title_match = re.search(r'title\s*=\s*\{([^}]+)\}', fields)
        if title_match:
            title = title_match.group(1)
            suggestions = suggest_tags(title)

            print(f"Entry: {key}")
            print(f"Title: {title}")
            print(f"Suggested tags: {', '.join(suggestions)}")
            print("-" * 40)

    print("\nTo add tags, edit papers.bib and add to keywords field:")
    print("keywords = {type:journal_article, role:lead_author, topic:ocean}")

if __name__ == "__main__":
    main()
```

### Phase 3: Template Creation (45 minutes)

#### Step 3.1: Create Tag Cloud Include

**File**: `_includes/publication_tag_cloud.liquid`

```liquid
{% comment %}
  Publication Tag Cloud Component
  Displays all available tags organized by category
{% endcomment %}

{% if site.publication_tags.enabled %}
  {% comment %} Extract all tags from bibliography {% endcomment %}
  {% assign all_tags = '' | split: ',' %}
  {% assign tag_categories = '' | split: ',' %}

  {% for entry in site.bibliography %}
    {% if entry.keywords %}
      {% for keyword in entry.keywords %}
        {% if keyword contains ':' %}
          {% assign parts = keyword | split: ':' %}
          {% assign category = parts[0] | strip %}
          {% assign tag_value = parts[1] | strip %}

          {% unless all_tags contains tag_value %}
            {% assign all_tags = all_tags | push: tag_value %}
          {% endunless %}

          {% unless tag_categories contains category %}
            {% assign tag_categories = tag_categories | push: category %}
          {% endunless %}
        {% endif %}
      {% endfor %}
    {% endif %}
  {% endfor %}

  <div class="publication-tag-system">
    <h3>Filter Publications by Tags</h3>

    {% for category in tag_categories %}
      {% assign category_label = site.publication_tags.categories[category].label | default: category | capitalize %}
      {% assign category_values = site.publication_tags.categories[category].values %}

      <div class="tag-category mb-3">
        <h4 class="h5 text-muted">{{ category_label }}</h4>
        <div class="tag-list">
          {% for tag in all_tags %}
            {% assign has_this_tag = false %}
            {% for entry in site.bibliography %}
              {% if entry.keywords contains tag %}
                {% assign has_this_tag = true %}
                {% break %}
              {% endif %}
            {% endfor %}

            {% if has_this_tag %}
              {% assign tag_url = '/writing/tags/' | append: tag | slugify | append: '/' %}
              <a href="{{ tag_url | relative_url }}" class="tag-link btn btn-sm btn-outline-secondary me-2 mb-2">
                {{ tag | replace: '_', ' ' | titleize }}
              </a>
            {% endif %}
          {% endfor %}
        </div>
      </div>
    {% endfor %}

    <div class="tag-actions mt-3">
      <a href="{{ '/writing/' | relative_url }}" class="btn btn-outline-primary btn-sm"> <i class="fa-solid fa-times"></i> Clear All Filters </a>
    </div>
  </div>
{% endif %}
```

#### Step 3.2: Create Active Tags Display

**File**: `_includes/publication_active_tags.liquid`

```liquid
{% comment %}
  Active Tags Display Component
  Shows currently selected tags and allows removal
{% endcomment %}

{% if page.url contains '/tags/' or page.url contains '/categories/' %}
  <div class="active-tags-display mb-4">
    <h4>Currently Filtering By:</h4>
    <div class="active-tags">
      {% if page.url contains '/tags/' %}
        {% assign current_tag = page.url | split: '/' | last | replace: '-', ' ' | titleize %}
        <span class="badge bg-primary me-2">
          {{ current_tag }}
          <a href="{{ '/writing/' | relative_url }}" class="text-white text-decoration-none ms-1">×</a>
        </span>
      {% endif %}

      {% if page.url contains '/categories/' %}
        {% assign current_category = page.url | split: '/' | last | replace: '-', ' ' | titleize %}
        <span class="badge bg-secondary me-2">
          {{ current_category }}
          <a href="{{ '/writing/' | relative_url }}" class="text-white text-decoration-none ms-1">×</a>
        </span>
      {% endif %}
    </div>

    <div class="mt-2">
      <a href="{{ '/writing/' | relative_url }}" class="btn btn-outline-secondary btn-sm">
        <i class="fa-solid fa-arrow-left"></i> Back to All Publications
      </a>
    </div>
  </div>
{% endif %}
```

#### Step 3.3: Update Writing Page

**File**: `_pages/writing.md`

**Current Content**:

```liquid
---
layout: page
permalink: /writing/
title: writing
description: 
nav: true
nav_order: 10
---
<!-- _pages/writing.md -->

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

<div class="publications">
  {% bibliography %}
</div>
```

**Updated Content**:

```liquid
---
layout: page
permalink: /writing/
title: writing
description: 
nav: true
nav_order: 10
---
<!-- _pages/writing.md -->

<!-- Publication Tag System -->
{% include publication_tag_cloud.liquid %}

<!-- Active Tags Display -->
{% include publication_active_tags.liquid %}

<!-- Enhanced Search -->
{% if site.publication_tags.enabled %}
  <div class="enhanced-search mb-4">
    <div class="input-group">
      <input type="text" id="enhanced-bibsearch" class="form-control" placeholder="Search publications and filter by tags above...">
      <button class="btn btn-outline-secondary" type="button" id="clear-search"><i class="fa-solid fa-times"></i> Clear</button>
    </div>
  </div>
{% else %}
  <!-- Fallback to original search -->
  {% include bib_search.liquid %}
{% endif %}

<div class="publications">
  {% bibliography %}
</div>
```

### Phase 4: Enhanced Search Integration (30 minutes)

#### Step 4.1: Create Enhanced Search JavaScript

**File**: `assets/js/enhanced_bibsearch.js`

```javascript
/**
 * Enhanced Bibliography Search with Tag Integration
 * Works alongside Jekyll Archives for tag-based filtering
 */

document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("enhanced-bibsearch");
  const clearButton = document.getElementById("clear-search");

  if (!searchInput) return;

  // Initialize search with URL parameters
  initializeSearch();

  // Enhanced search with tag awareness
  searchInput.addEventListener(
    "input",
    debounce(function () {
      const searchTerm = this.value.toLowerCase();
      performEnhancedSearch(searchTerm);
    }, 300)
  );

  // Clear search
  if (clearButton) {
    clearButton.addEventListener("click", function () {
      searchInput.value = "";
      performEnhancedSearch("");
    });
  }

  // Handle tag clicks (if on tag page)
  handleTagPageSearch();
});

function initializeSearch() {
  const urlParams = new URLSearchParams(window.location.search);
  const searchTerm = urlParams.get("search");

  if (searchTerm) {
    const searchInput = document.getElementById("enhanced-bibsearch");
    if (searchInput) {
      searchInput.value = searchTerm;
      performEnhancedSearch(searchTerm);
    }
  }
}

function performEnhancedSearch(searchTerm) {
  const publications = document.querySelectorAll(".bibliography > li");
  let visibleCount = 0;

  publications.forEach(function (pub) {
    const text = pub.textContent.toLowerCase();
    const isVisible = searchTerm === "" || text.includes(searchTerm);

    if (isVisible) {
      pub.style.display = "";
      visibleCount++;
    } else {
      pub.style.display = "none";
    }
  });

  // Update publication count
  updatePublicationCount(visibleCount, publications.length);

  // Hide empty year groups
  hideEmptyYearGroups();
}

function updatePublicationCount(visible, total) {
  let countElement = document.getElementById("publication-count");

  if (!countElement) {
    countElement = document.createElement("div");
    countElement.id = "publication-count";
    countElement.className = "text-muted mb-3";

    const searchContainer = document.querySelector(".enhanced-search");
    if (searchContainer) {
      searchContainer.appendChild(countElement);
    }
  }

  countElement.textContent = `Showing ${visible} of ${total} publications`;
}

function hideEmptyYearGroups() {
  const yearHeaders = document.querySelectorAll("h2.bibliography");

  yearHeaders.forEach(function (header) {
    const nextElement = header.nextElementSibling;
    if (nextElement && nextElement.tagName === "OL") {
      const visiblePublications = nextElement.querySelectorAll('li[style=""]');
      if (visiblePublications.length === 0) {
        header.style.display = "none";
        nextElement.style.display = "none";
      } else {
        header.style.display = "";
        nextElement.style.display = "";
      }
    }
  });
}

function handleTagPageSearch() {
  // If we're on a tag page, integrate with existing search
  const tagPage = window.location.pathname.includes("/tags/") || window.location.pathname.includes("/categories/");

  if (tagPage && searchInput) {
    searchInput.placeholder = "Search within filtered publications...";
  }
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
```

### Phase 5: Styling (15 minutes)

#### Step 5.1: Add CSS for Tag System

**File**: `_sass/_publications.scss` (create new file)

```scss
// Publication Tag System Styles

.publication-tag-system {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;

  h3 {
    margin-bottom: 1.5rem;
    color: #495057;
    font-size: 1.25rem;
  }

  .tag-category {
    margin-bottom: 1.5rem;

    h4 {
      font-size: 0.9rem;
      font-weight: 600;
      margin-bottom: 0.75rem;
      color: #6c757d;
    }

    .tag-list {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }
  }

  .tag-link {
    font-size: 0.8rem;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    text-decoration: none;
    transition: all 0.2s ease;

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
  }

  .tag-actions {
    border-top: 1px solid #dee2e6;
    padding-top: 1rem;
  }
}

.active-tags-display {
  background: #e3f2fd;
  border-radius: 6px;
  padding: 1rem;

  h4 {
    font-size: 1rem;
    margin-bottom: 0.75rem;
    color: #1976d2;
  }

  .active-tags {
    margin-bottom: 1rem;

    .badge {
      font-size: 0.8rem;
      padding: 0.5rem 0.75rem;
    }
  }
}

.enhanced-search {
  .input-group {
    max-width: 600px;
  }

  #publication-count {
    font-size: 0.9rem;
    margin-top: 0.5rem;
  }
}

// Responsive adjustments
@media (max-width: 768px) {
  .publication-tag-system {
    padding: 1rem;

    .tag-list {
      gap: 0.25rem;
    }

    .tag-link {
      font-size: 0.75rem;
      padding: 0.2rem 0.6rem;
    }
  }
}
```

#### Step 5.2: Import New Styles

**File**: `assets/css/main.scss`

**Add this line** (if it doesn't exist):

```scss
@import "publications";
```

### Phase 6: Testing & Validation (30 minutes)

#### Step 6.1: Test Tag Generation

1. **Start Jekyll server**: `bundle exec jekyll serve`
2. **Visit `/writing/` page**
3. **Verify tag cloud appears**
4. **Check tag links work** (should go to `/writing/tags/[tag-name]/`)

#### Step 6.2: Test Tag Pages

1. **Click on a tag** (e.g., "ocean")
2. **Verify filtered publications display**
3. **Check URL structure** (`/writing/tags/ocean/`)
4. **Test back navigation**

#### Step 6.3: Test Search Integration

1. **Use enhanced search bar**
2. **Verify publication count updates**
3. **Test clear functionality**
4. **Check year group hiding**

### Phase 7: Migration & Cleanup (1 hour)

#### Step 7.1: Tag Existing Publications

**Priority order**:

1. **High-impact publications** (most cited, most relevant)
2. **Recent publications** (last 2 years)
3. **Representative samples** (one from each topic area)
4. **Remaining publications** (gradually over time)

#### Step 7.2: Validate Tag Consistency

**Check for**:

- Consistent tag naming (snake_case)
- Proper category prefixes
- No duplicate tags
- Meaningful tag values

#### Step 7.3: Update Documentation

**Files to update**:

- `README.md` - Add tag system documentation
- `CUSTOMIZE.md` - Add tag customization instructions
- `_config.yml` - Add comments explaining tag system

---

## Implementation Checklist

### Configuration (30 min)

- [ ] Enable Jekyll Archives for publications
- [ ] Add publication tag configuration
- [ ] Test Jekyll build

### Templates (45 min)

- [ ] Create publication tag cloud include
- [ ] Create active tags display include
- [ ] Update writing page
- [ ] Test template rendering

### Functionality (30 min)

- [ ] Create enhanced search JavaScript
- [ ] Test search integration
- [ ] Verify tag filtering

### Styling (15 min)

- [ ] Create publication styles
- [ ] Import styles to main CSS
- [ ] Test responsive design

### Testing (30 min)

- [ ] Test tag generation
- [ ] Test tag pages
- [ ] Test search integration
- [ ] Cross-browser testing

### Migration (1 hour)

- [ ] Tag 10-20 key publications
- [ ] Validate tag consistency
- [ ] Update documentation
- [ ] Final testing

**Total Implementation Time**: ~3 hours
**Complexity**: Low (minimal new code, leverages existing infrastructure)
**Risk**: Very Low (backward compatible, gradual rollout)

This roadmap provides comprehensive step-by-step instructions for implementing the Jekyll Archives approach with minimal code changes and maximum leverage of existing functionality.

```

```
