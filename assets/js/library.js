(() => {
  const EXPAND_FLAGS = new Set(["abs", "photos", "figures", "speakers", "quotes", "audio", "award"]);
  const VIZ_HASHES = new Set(["explore", "co-authors", "coauthors", "citations", "timeline"]);
  const FLAG_TO_PANEL = {
    abs: "abstract",
    photos: "photos",
    figures: "figures",
    speakers: "speakers",
    quotes: "quotes",
    audio: "audio",
    award: "award",
  };

  const state = {
    items: [],
    details: null,
    detailsPromise: null,
    q: "",
    kind: null,
    value: "",
    type: null,
    role: null,
    selectedOnly: false,
    catalogUrl: "",
    detailsUrl: "",
  };

  const els = {};
  const filterMeta = new Map();

  document.addEventListener("DOMContentLoaded", init);

  async function init() {
    const root = document.getElementById("libraryApp");
    if (!root) return;

    els.root = root;
    els.results = document.getElementById("libraryResults");
    els.status = document.getElementById("libraryStatus");
    els.search = document.getElementById("bibsearch");
    els.countDisplay = document.getElementById("itemCountDisplay");
    els.countText = document.getElementById("itemCountText");
    els.selectedBtn = document.getElementById("selectedToggleBtn");
    els.mapBtn = document.getElementById("mapToggleBtn");
    els.exploreBtn = document.getElementById("exploreToggleBtn");

    state.catalogUrl = root.dataset.catalog;
    state.detailsUrl = root.dataset.details;

    bindUi();
    if (isVizHash(currentHash())) setExploreOpen(true, { updateHash: false });

    try {
      setStatus("Loading catalogue…", true);
      const response = await fetch(state.catalogUrl, { credentials: "same-origin" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const catalog = await response.json();
      state.items = Array.isArray(catalog.items) ? catalog.items : [];
      applyUrlState();
      render();
      requestAnimationFrame(() => jumpToHash({ retry: true }));
    } catch (error) {
      console.error("Library catalogue failed to load", error);
      setStatus("Could not load the library catalogue.", false);
    }
  }

  function bindUi() {
    document.querySelectorAll(".library-filters [data-filter]").forEach((chip) => {
      const value = chip.dataset.filter;
      const kind = chip.dataset.kind;
      const text = chip.textContent.trim();
      const countMatch = text.match(/^(.*)\s+\((\d+)\)\s*$/);
      filterMeta.set(chip, {
        kind,
        value,
        label: countMatch ? countMatch[1] : text,
        baseCount: countMatch ? Number(countMatch[2]) : 0,
      });
      chip.addEventListener("click", (event) => {
        event.preventDefault();
        if (chip.disabled) return;
        applyChip(value, kind);
      });
    });

    const clearLink = document.getElementById("clearFiltersLink");
    if (clearLink) {
      clearLink.addEventListener("click", (event) => {
        event.preventDefault();
        clearFilters();
        render();
      });
    }

    if (els.search) {
      let timeoutId;
      els.search.addEventListener("input", () => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
          const term = els.search.value.trim();
          if (!term) {
            if (!state.selectedOnly) clearFilters({ keepSearch: false });
            else {
              state.q = "";
              state.kind = null;
              state.value = "";
              state.type = null;
              state.role = null;
              syncFilterBadges();
            }
            render();
            return;
          }
          state.selectedOnly = false;
          updateSelectedButton();
          state.q = term.toLowerCase();
          state.kind = "text";
          state.value = term;
          state.type = null;
          state.role = null;
          syncFilterBadges();
          render();
        }, 300);
      });
    }

    if (els.selectedBtn) {
      els.selectedBtn.addEventListener("click", (event) => {
        event.preventDefault();
        toggleSelected();
      });
    }

    if (els.mapBtn) {
      els.mapBtn.addEventListener("click", (event) => {
        event.preventDefault();
        toggleMap();
      });
    }

    if (els.exploreBtn) {
      els.exploreBtn.addEventListener("click", (event) => {
        event.preventDefault();
        toggleExplore();
      });
    }

    window.addEventListener("hashchange", onLibraryHashChange);

    if (els.results) {
      els.results.addEventListener("click", onResultsClick);
    }
  }

  function applyUrlState() {
    const params = new URLSearchParams(window.location.search);
    const filterParam = params.get("filter");
    const action = params.get("action");
    const hash = decodeURIComponent(window.location.hash.replace(/^#/, ""));

    if (filterParam) {
      const kind = kindForFilter(filterParam);
      applyChip(filterParam, kind, { render: false });
      return;
    }

    if (action !== "jump" && hash && !isVizHash(hash)) {
      if (els.search) els.search.value = hash;
      state.q = hash.toLowerCase();
      state.kind = "text";
      state.value = hash;
      state.type = null;
      state.role = null;
    }
  }

  function kindForFilter(value) {
    const chip = [...document.querySelectorAll(".library-filters [data-filter]")].find((el) => el.dataset.filter === value);
    return chip ? chip.dataset.kind : "text";
  }

  function applyChip(value, kind, { render: shouldRender = true } = {}) {
    state.selectedOnly = false;
    updateSelectedButton();

    if (kind === "type" || kind === "role") {
      const key = kind === "type" ? "type" : "role";
      if (state[key] === value) state[key] = null;
      else state[key] = value;
      state.kind = null;
      state.value = "";
      state.q = "";
      if (els.search) els.search.value = "";
      syncFilterBadges();
      if (shouldRender) render();
      return;
    }

    state.type = null;
    state.role = null;
    state.kind = kind || "text";
    state.value = value;
    state.q = value.toLowerCase();
    if (els.search) els.search.value = value;
    syncFilterBadges();
    if (shouldRender) render();
  }

  function clearFilters({ keepSearch = false } = {}) {
    state.kind = null;
    state.value = "";
    state.q = "";
    state.type = null;
    state.role = null;
    state.selectedOnly = false;
    if (!keepSearch && els.search) els.search.value = "";
    syncFilterBadges();
    updateSelectedButton();
  }

  function toggleSelected() {
    state.selectedOnly = !state.selectedOnly;
    if (state.selectedOnly) {
      state.kind = null;
      state.value = "";
      state.q = "";
      state.type = null;
      state.role = null;
      if (els.search) els.search.value = "";
      syncFilterBadges();
    } else if (state.kind === "selected") {
      state.kind = null;
    }
    updateSelectedButton();
    render();
  }

  function updateSelectedButton() {
    if (!els.selectedBtn) return;
    els.selectedBtn.setAttribute("aria-pressed", state.selectedOnly ? "true" : "false");
    els.selectedBtn.innerHTML = state.selectedOnly
      ? '<i class="fas fa-eye-slash" aria-hidden="true"></i> hide selected publications'
      : '<i class="fas fa-eye" aria-hidden="true"></i> show selected publications';
  }

  function countsTowardFilters(item) {
    return !item.nocount;
  }

  function countItemsFor(kind, value) {
    return state.items.reduce((total, item) => {
      if (!countsTowardFilters(item)) return total;
      if (kind === "type") {
        if ((item.type || "") !== value) return total;
        if (state.role && !(item.roles || []).includes(state.role)) return total;
        return total + 1;
      }
      if (kind === "role") {
        if (!(item.roles || []).includes(value)) return total;
        if (state.type && (item.type || "") !== state.type) return total;
        return total + 1;
      }
      return total;
    }, 0);
  }

  function syncFilterBadges() {
    document.querySelectorAll(".library-filters [data-filter]").forEach((chip) => {
      const meta = filterMeta.get(chip);
      if (!meta) return;
      const { kind, value, label, baseCount } = meta;
      let active = false;
      let count = baseCount;
      let unavailable = false;

      if (kind === "type") {
        active = state.type === value;
        if (state.role) {
          count = countItemsFor("type", value);
          unavailable = count === 0 && !active;
        }
      } else if (kind === "role") {
        active = state.role === value;
        if (state.type) {
          count = countItemsFor("role", value);
          unavailable = count === 0 && !active;
        }
      } else if (kind === "lang") {
        active = state.kind === "lang" && state.value === value;
      }

      chip.textContent = `${label} (${count})`;
      chip.classList.toggle("active", active);
      chip.classList.toggle("is-unavailable", unavailable);
      chip.disabled = unavailable;
      chip.setAttribute("aria-pressed", active ? "true" : "false");
      if (unavailable) chip.setAttribute("aria-disabled", "true");
      else chip.removeAttribute("aria-disabled");
    });
  }

  function matchingItems() {
    return state.items.filter(itemMatches);
  }

  function itemMatches(item) {
    if (state.type && (item.type || "") !== state.type) return false;
    if (state.role && !(item.roles || []).includes(state.role)) return false;

    if (!state.kind || !state.value) return true;

    if (state.kind === "lang") {
      return (item.langs || []).includes(state.value.toLowerCase());
    }

    const haystack = [item.title, item.authors, item.venue, item.year, item.type, ...(item.roles || []), ...(item.langs || [])]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    return haystack.includes(state.q);
  }

  function render() {
    const matches = matchingItems();
    const selected = state.selectedOnly ? state.items.filter((item) => item.selected) : [];
    const fragment = document.createDocumentFragment();

    if (!matches.length && !selected.length) {
      els.results.replaceChildren();
      const empty = document.createElement("p");
      empty.id = "libraryStatus";
      empty.className = "library-status";
      empty.textContent = "No matching publications.";
      els.results.appendChild(empty);
      els.status = empty;
      updateCount(0);
      els.results.setAttribute("aria-busy", "false");
      notifyProgressBar();
      return;
    }

    if (selected.length) {
      const block = document.createElement("section");
      block.className = "selected-publications";
      const selectedHeading = document.createElement("h2");
      selectedHeading.className = "bibliography";
      selectedHeading.textContent = "selected publications";
      block.appendChild(selectedHeading);
      appendYearGroups(block, selected, { idSuffix: "--selected" });
      fragment.appendChild(block);
    }

    appendYearGroups(fragment, matches);

    els.results.replaceChildren(fragment);
    els.status = null;
    els.results.setAttribute("aria-busy", "false");
    updateCount(matches.length);
    notifyProgressBar();
    watchResultImages();
  }

  function appendYearGroups(parent, items, { idSuffix = "" } = {}) {
    let currentYear = null;
    let list = null;
    items.forEach((item) => {
      if (item.year !== currentYear) {
        currentYear = item.year;
        const heading = document.createElement("h2");
        heading.className = "bibliography";
        heading.textContent = String(item.year || "");
        parent.appendChild(heading);
        list = document.createElement("ol");
        list.className = "bibliography";
        parent.appendChild(list);
      }
      list.appendChild(renderCard(item, { idSuffix }));
    });
  }

  function notifyProgressBar() {
    if (typeof window.refreshProgressBar === "function") {
      window.refreshProgressBar();
    }
  }

  function watchResultImages() {
    if (!els.results) return;
    els.results.querySelectorAll("img").forEach((img) => {
      if (img.complete) return;
      img.addEventListener("load", notifyProgressBar, { once: true });
      img.addEventListener("error", notifyProgressBar, { once: true });
    });
  }

  function renderCard(item, { idSuffix = "" } = {}) {
    const li = document.createElement("li");
    const row = document.createElement("div");
    row.className = "row";

    const thumbCol = document.createElement("div");
    thumbCol.className = "col col-sm-2 abbr";
    if (item.thumb) {
      const img = document.createElement("img");
      img.className = "preview rounded";
      img.src = item.thumb;
      img.width = 80;
      img.height = 107;
      img.loading = "lazy";
      img.decoding = "async";
      img.alt = "";
      img.addEventListener("error", () => {
        if (img.dataset.fallback) return;
        img.dataset.fallback = "1";
        img.src = item.thumb.replace("-480.webp", ".jpeg");
      });
      thumbCol.appendChild(img);
    }
    row.appendChild(thumbCol);

    const body = document.createElement("div");
    body.className = "col-sm-8";
    body.id = `${item.id}${idSuffix}`;

    const title = document.createElement("div");
    title.className = "title";
    title.textContent = item.title;
    body.appendChild(title);

    const typeRow = document.createElement("div");
    typeRow.className = "item-type-and-roles";
    if (item.type) {
      typeRow.appendChild(chipButton("badge badge-light", item.type, "type", item.type));
    }
    (item.roles || []).forEach((role) => {
      typeRow.appendChild(chipButton("tag", role, "role", role));
    });
    if (typeRow.childElementCount) body.appendChild(typeRow);

    if (item.venue) {
      const venue = document.createElement("div");
      venue.className = "periodical";
      const em = document.createElement("em");
      em.textContent = item.venue;
      venue.appendChild(em);
      body.appendChild(venue);
    }

    if (item.authorsHtml || item.authors) {
      const author = document.createElement("div");
      author.className = "author";
      if (item.authorsHtml) author.innerHTML = item.authorsHtml;
      else author.textContent = item.authors;
      body.appendChild(author);
    }

    const links = document.createElement("div");
    links.className = "links";
    if (item.info) {
      links.appendChild(iconLink(item.info, "fa-circle-info", "View details", { internal: true }));
    }
    if (item.pdf) {
      links.appendChild(iconLink(item.pdf, "fa-file-pdf", "View PDF"));
    }
    if (item.url) {
      links.appendChild(iconLink(item.url, "fa-globe", "Open website"));
    }
    if (item.doi) {
      links.appendChild(iconLink(item.doi, "fa-search", "Open DOI"));
    }
    if (item.slides) {
      links.appendChild(iconLink(item.slides, "fa-file-powerpoint", "View slides"));
    }
    if (item.agenda) {
      links.appendChild(iconLink(item.agenda, "fa-file-lines", "View agenda"));
    }
    if (item.video) {
      links.appendChild(iconLink(item.video, "fa-circle-play", "View video"));
    }
    (item.links || []).forEach((href) => {
      links.appendChild(iconLink(href, "fa-up-right-from-square", "Additional link"));
    });
    (item.flags || []).forEach((flag) => {
      if (!EXPAND_FLAGS.has(flag)) return;
      const panel = FLAG_TO_PANEL[flag];
      const labels = {
        abs: ["fa-file-lines", "View abstract"],
        photos: ["fa-camera", "View photos"],
        figures: ["fa-chart-bar", "View figures"],
        speakers: ["fa-users", "View speakers"],
        quotes: ["fa-quote-left", "View quotes"],
        audio: ["fa-volume-high", "View audio"],
        award: ["fa-trophy", "View award"],
      };
      const [icon, label] = labels[flag];
      links.appendChild(expandButton(panel, icon, label, item.id));
    });
    body.appendChild(links);

    if (item.langs && item.langs.length) {
      const tags = document.createElement("div");
      tags.className = "all-tags";
      item.langs.forEach((lang) => {
        tags.appendChild(chipButton("tag", lang, "lang", lang));
      });
      body.appendChild(tags);
    }

    row.appendChild(body);
    li.appendChild(row);
    return li;
  }

  function chipButton(className, label, kind, value) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = className;
    btn.textContent = label;
    btn.dataset.filter = value;
    btn.dataset.kind = kind;
    btn.addEventListener("click", (event) => {
      event.preventDefault();
      applyChip(value, kind);
    });
    return btn;
  }

  function iconLink(href, icon, label, { internal = false } = {}) {
    const a = document.createElement("a");
    a.className = "btn btn-sm z-depth-0";
    a.href = href;
    a.title = label;
    a.setAttribute("aria-label", label);
    if (!internal) {
      a.target = "_blank";
      a.rel = "noopener noreferrer";
    }
    a.innerHTML = `<i class="fa-solid ${icon}" aria-hidden="true"></i>`;
    return a;
  }

  function expandButton(panel, icon, label, itemId) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `btn btn-sm z-depth-0 ${panel === "abstract" ? "abstract" : panel}`;
    btn.dataset.expand = panel;
    btn.dataset.itemId = itemId;
    btn.title = label;
    btn.setAttribute("aria-label", label);
    btn.setAttribute("aria-expanded", "false");
    btn.innerHTML = `<i class="fa-solid ${icon}" aria-hidden="true"></i>`;
    return btn;
  }

  async function onResultsClick(event) {
    const button = event.target.closest("[data-expand]");
    if (!button || !els.results.contains(button)) return;
    event.preventDefault();
    const panel = button.dataset.expand;
    const itemId = button.dataset.itemId;
    const card = button.closest(".col-sm-8");
    if (!card) return;

    try {
      await ensureDetails();
      injectPanel(card, itemId, panel);
      togglePanel(card, panel, button);
    } catch (error) {
      console.error("Could not load library details", error);
    }
  }

  function ensureDetails() {
    if (state.details) return Promise.resolve(state.details);
    if (state.detailsPromise) return state.detailsPromise;
    state.detailsPromise = fetch(state.detailsUrl, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then((data) => {
        state.details = data || {};
        return state.details;
      })
      .catch((error) => {
        state.detailsPromise = null;
        throw error;
      });
    return state.detailsPromise;
  }

  function injectPanel(card, itemId, panel) {
    if (card.querySelector(`.${panel}.hidden`)) return;
    const detail = (state.details && state.details[itemId]) || {};
    const wrapper = document.createElement("div");
    wrapper.className = `${panel} hidden`;

    if (panel === "abstract") {
      wrapper.innerHTML = `<div class="abstract-label">Abstract:</div><div class="abstract-content"><p style="white-space: pre-wrap;"></p></div>`;
      wrapper.querySelector("p").textContent = detail.abstract || "Abstract not available.";
    } else if (panel === "photos" || panel === "figures") {
      const label = panel === "photos" ? "Photos" : "Figures";
      const images = detail[panel] || [];
      const grid = document.createElement("div");
      grid.className = `gallery-grid ${panel}-grid`;
      images.forEach((image, index) => {
        const img = document.createElement("img");
        img.src = image.src;
        img.alt = image.alt || label;
        img.className = "gallery-image";
        img.loading = "lazy";
        img.dataset.galleryType = panel;
        img.dataset.galleryIndex = String(index);
        img.addEventListener("click", () => {
          if (typeof window.openGalleryModal === "function") {
            window.openGalleryModal(img);
          }
        });
        grid.appendChild(img);
      });
      const caption = document.createElement("div");
      caption.className = `${panel}-label`;
      caption.textContent = `${label}:`;
      wrapper.appendChild(caption);
      wrapper.appendChild(grid);
    } else if (panel === "speakers") {
      wrapper.innerHTML = `<div class="speakers-label">Speakers:</div>`;
      const list = document.createElement("ul");
      list.className = "speakers-list";
      (detail.speakers || []).forEach((speaker) => {
        const li = document.createElement("li");
        li.textContent = speaker;
        list.appendChild(li);
      });
      wrapper.appendChild(list);
    } else if (panel === "quotes") {
      wrapper.innerHTML = `<div class="quotes-label">Quotes:</div>`;
      const list = document.createElement("ul");
      (detail.quotes || []).forEach((quote) => {
        const li = document.createElement("li");
        li.textContent = quote;
        list.appendChild(li);
      });
      wrapper.appendChild(list);
    } else if (panel === "audio") {
      wrapper.innerHTML = `<div class="audio-label">Audio:</div>`;
      (detail.audio || []).forEach((src) => {
        const audio = document.createElement("audio");
        audio.controls = true;
        audio.src = src.startsWith("/") || src.includes("://") ? src : `/assets/audio/${src}`;
        wrapper.appendChild(audio);
      });
    } else if (panel === "award") {
      wrapper.innerHTML = `<div class="award-label">Award:</div>`;
      const p = document.createElement("p");
      p.textContent = detail.award || "";
      wrapper.appendChild(p);
    }

    card.appendChild(wrapper);
  }

  function togglePanel(card, panel, button) {
    card.querySelectorAll(".hidden.open").forEach((open) => {
      if (!open.classList.contains(panel)) open.classList.remove("open");
    });
    const target = card.querySelector(`.${panel}.hidden`);
    if (!target) return;
    const willOpen = !target.classList.contains("open");
    target.classList.toggle("open", willOpen);
    button.setAttribute("aria-expanded", willOpen ? "true" : "false");
    card.querySelectorAll("[data-expand]").forEach((other) => {
      if (other !== button) other.setAttribute("aria-expanded", "false");
    });
  }

  function updateCount(count) {
    if (!els.countDisplay || !els.countText) return;
    const filtering = Boolean(state.type || state.role || (state.kind && state.value));
    if (!filtering) {
      els.countDisplay.style.display = "none";
      els.countDisplay.classList.remove("show");
      return;
    }
    els.countText.textContent = `showing ${count} item${count === 1 ? "" : "s"}`;
    els.countDisplay.style.display = "block";
    els.countDisplay.classList.add("show");
  }

  function setStatus(message, busy) {
    if (!els.results) return;
    els.results.replaceChildren();
    const status = document.createElement("p");
    status.id = "libraryStatus";
    status.className = "library-status";
    status.textContent = message;
    els.results.appendChild(status);
    els.status = status;
    els.results.setAttribute("aria-busy", busy ? "true" : "false");
  }

  function jumpToHash({ retry = false } = {}) {
    const params = new URLSearchParams(window.location.search);
    if (params.get("action") !== "jump") return;
    const hash = decodeURIComponent(window.location.hash.replace(/^#/, ""));
    if (!hash) return;
    if (scrollToId(hash)) return;
    if (retry) {
      clearFilters();
      render();
      scrollToId(hash);
    }
  }

  function scrollToId(id) {
    const target = document.getElementById(id);
    if (!target) return false;
    target.scrollIntoView({ behavior: "auto", block: "center" });
    target.style.backgroundColor = "#fff3cd";
    target.style.transition = "background-color 0.5s ease";
    window.setTimeout(() => {
      target.style.backgroundColor = "";
    }, 2000);
    return true;
  }

  // --- Map (lazy Leaflet, unchanged behaviour) ---
  let libraryMap = null;
  let mapInitialized = false;

  function hashValue() {
    return decodeURIComponent(window.location.hash.replace(/^#/, ""));
  }

  function onLibraryHashChange() {
    const hash = hashValue();
    if (isVizHash(hash)) {
      setMapOpen(false);
      setExploreOpen(true, { updateHash: false });
      return;
    }
    const exploreContainer = document.getElementById("libraryExploreContainer");
    if (exploreContainer && !isHidden(exploreContainer)) {
      setExploreOpen(false, { updateHash: false });
    }
    const action = new URLSearchParams(window.location.search).get("action");
    if (!hash || action === "jump") return;
    state.selectedOnly = false;
    updateSelectedButton();
    state.q = hash.toLowerCase();
    state.kind = "text";
    state.value = hash;
    state.type = null;
    state.role = null;
    if (els.search) els.search.value = hash;
    syncFilterBadges();
    render();
  }

  function currentHash() {
    return decodeURIComponent(window.location.hash.replace(/^#/, "")).toLowerCase();
  }

  function isVizHash(hash) {
    return VIZ_HASHES.has(String(hash || "").toLowerCase());
  }

  function networkTabFromHash() {
    const hash = currentHash();
    if (hash === "citations") return "citations";
    if (hash === "timeline") return "timeline";
    if (hash === "co-authors" || hash === "coauthors") return "coauthors";
    const selected = document.querySelector("#networkApp .network-tab.is-active");
    return selected?.dataset.tab || "coauthors";
  }

  function isHidden(el) {
    if (!el) return true;
    return el.style.display === "none" || window.getComputedStyle(el).display === "none";
  }

  function toggleMap() {
    const mapContainer = document.getElementById("libraryMapContainer");
    if (!mapContainer) return;
    const opening = isHidden(mapContainer);
    if (opening) setExploreOpen(false);
    setMapOpen(opening);
  }

  function toggleExplore() {
    const exploreContainer = document.getElementById("libraryExploreContainer");
    if (!exploreContainer) return;
    const opening = isHidden(exploreContainer);
    if (opening) setMapOpen(false);
    setExploreOpen(opening);
  }

  function setMapOpen(open) {
    const mapContainer = document.getElementById("libraryMapContainer");
    if (!mapContainer || !els.mapBtn) return;
    mapContainer.style.display = open ? "block" : "none";
    els.mapBtn.setAttribute("aria-pressed", open ? "true" : "false");
    els.mapBtn.innerHTML = open
      ? '<i class="fas fa-map-marker-alt" aria-hidden="true"></i> hide map'
      : '<i class="fas fa-map-marker-alt" aria-hidden="true"></i> view map';
    if (open && !mapInitialized) initializeLibraryMap();
  }

  function setExploreOpen(open, { updateHash = true } = {}) {
    const exploreContainer = document.getElementById("libraryExploreContainer");
    if (!exploreContainer || !els.exploreBtn) return;
    exploreContainer.style.display = open ? "block" : "none";
    els.exploreBtn.setAttribute("aria-pressed", open ? "true" : "false");
    els.exploreBtn.innerHTML = open
      ? '<i class="fas fa-project-diagram" aria-hidden="true"></i> hide explore'
      : '<i class="fas fa-project-diagram" aria-hidden="true"></i> explore';
    if (open) {
      if (updateHash && !isVizHash(currentHash())) {
        const url = new URL(window.location.href);
        url.hash = "explore";
        history.replaceState(null, "", url);
      }
      window.dispatchEvent(
        new CustomEvent("network:tab", { detail: { tab: networkTabFromHash() } })
      );
    } else if (updateHash && isVizHash(currentHash())) {
      const url = new URL(window.location.href);
      history.replaceState(null, "", url.pathname + url.search);
    }
  }

  function initializeLibraryMap() {
    if (!document.querySelector('link[href*="leaflet"]')) {
      const leafletCSS = document.createElement("link");
      leafletCSS.rel = "stylesheet";
      leafletCSS.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
      leafletCSS.integrity = "sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=";
      leafletCSS.crossOrigin = "anonymous";
      document.head.appendChild(leafletCSS);

      const clusterCSS = document.createElement("link");
      clusterCSS.rel = "stylesheet";
      clusterCSS.href = "https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css";
      clusterCSS.crossOrigin = "anonymous";
      document.head.appendChild(clusterCSS);

      const clusterDefaultCSS = document.createElement("link");
      clusterDefaultCSS.rel = "stylesheet";
      clusterDefaultCSS.href = "https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css";
      clusterDefaultCSS.crossOrigin = "anonymous";
      document.head.appendChild(clusterDefaultCSS);
    }

    if (!window.L) {
      const leafletJS = document.createElement("script");
      leafletJS.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
      leafletJS.integrity = "sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=";
      leafletJS.crossOrigin = "anonymous";
      leafletJS.onload = loadMarkerCluster;
      document.head.appendChild(leafletJS);
    } else {
      loadMarkerCluster();
    }
  }

  function loadMarkerCluster() {
    if (!window.L.markerClusterGroup) {
      const clusterJS = document.createElement("script");
      clusterJS.src = "https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js";
      clusterJS.crossOrigin = "anonymous";
      clusterJS.onload = createLibraryMap;
      document.head.appendChild(clusterJS);
    } else {
      createLibraryMap();
    }
  }

  function createLibraryMap() {
    libraryMap = window.L.map("libraryMap").setView([50.0, 10.0], 4);
    window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 18,
    }).addTo(libraryMap);

    const markers = window.L.markerClusterGroup({
      chunkedLoading: true,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false,
      zoomToBoundsOnClick: true,
      maxClusterRadius: 50,
      iconCreateFunction(cluster) {
        const count = cluster.getChildCount();
        let size = "small";
        if (count > 10) size = "large";
        else if (count > 5) size = "medium";
        return window.L.divIcon({
          html: `<div class="cluster-icon cluster-${size}">${count}</div>`,
          className: `marker-cluster marker-cluster-${size}`,
          iconSize: window.L.point(40, 40),
          iconAnchor: window.L.point(20, 20),
        });
      },
    });
    libraryMap.addLayer(markers);

    fetch("/assets/mapping/location_coordinates.json")
      .then((response) => response.json())
      .then((data) => {
        const conferences = (data.locations || []).filter((conf) => conf.geocoded);
        conferences.forEach((conf) => {
          const marker = window.L.marker([conf.coordinates.lat, conf.coordinates.lng]);
          marker.bindPopup(createPopupContent(conf));
          markers.addLayer(marker);
        });
        if (conferences.length > 0) {
          libraryMap.fitBounds(markers.getBounds().pad(0.1));
        }
      })
      .catch((error) => console.error("Error loading conference data:", error));

    mapInitialized = true;
  }

  function createPopupContent(conf) {
    const date = formatDate(conf.year, conf.month);
    const eventType = conf.tag || conf.entry_type || "";
    return `
    <div class="popup-content">
      <div class="popup-title">${escapeHtml(conf.title || "")}</div>
      <div class="popup-details">
        <div class="popup-detail"><i class="fas fa-calendar"></i> ${escapeHtml(date)}</div>
        <div class="popup-detail"><i class="fas fa-tag"></i> ${escapeHtml(eventType)}</div>
        <div class="popup-detail"><i class="fas fa-map-marker-alt"></i> ${escapeHtml(conf.address || "")}</div>
      </div>
      <a href="/library/?action=jump#${encodeURIComponent(conf.bibtex_key || "")}" class="popup-link">
        <i class="fas fa-external-link-alt"></i> View Details
      </a>
    </div>`;
  }

  function formatDate(year, month) {
    if (!year) return "Date unknown";
    const monthNames = {
      jan: "January",
      feb: "February",
      mar: "March",
      apr: "April",
      may: "May",
      jun: "June",
      jul: "July",
      aug: "August",
      sep: "September",
      oct: "October",
      nov: "November",
      dec: "December",
    };
    const monthName = month ? monthNames[String(month).toLowerCase()] : "";
    return monthName ? `${monthName} ${year}` : String(year);
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text == null ? "" : String(text);
    return div.innerHTML;
  }
})();
