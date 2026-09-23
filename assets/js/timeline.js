(() => {
  const GROUPS = [
    {
      id: "publications",
      label: "Publications",
      color: "#1b6ca8",
      types: ["Journal Article", "Report", "Report Section", "Book", "Book Chapter"],
    },
    {
      id: "events",
      label: "Events",
      color: "#2a9d8f",
      types: ["Conference", "Workshop", "Training", "Webinar", "Side Event"],
    },
    {
      id: "writing",
      label: "Writing",
      color: "#c4a35a",
      types: ["Blog", "Newspaper", "Oped"],
    },
    {
      id: "process",
      label: "Process",
      color: "#e76f51",
      types: ["Submission", "Negotiation", "Fellowship"],
    },
    {
      id: "other",
      label: "Other",
      color: "#6c757d",
      types: ["Poster", "Radio"],
    },
    {
      id: "code",
      label: "Code",
      color: "#2f4858",
      types: ["Code"],
    },
  ];

  const ROLE_ORDER = [
    "lead author",
    "author",
    "co-author",
    "speaker",
    "facilitator",
    "organiser",
    "participant",
    "delegate",
    "attendee",
    "interview",
    "quoted",
    "contributor",
    "unspecified",
  ];

  const ROLE_COLORS = {
    "lead author": "#1b6ca8",
    author: "#4c78a8",
    "co-author": "#72b7b2",
    speaker: "#e45756",
    facilitator: "#f58518",
    organiser: "#54a24b",
    participant: "#eeca3b",
    delegate: "#ff9da6",
    attendee: "#bab0ac",
    interview: "#b279a2",
    quoted: "#9d755d",
    contributor: "#2f4858",
    unspecified: "#6c757d",
  };

  const state = {
    items: [],
    mode: "type",
    yearMin: null,
    yearMax: null,
    from: null,
    to: null,
    selected: null,
  };

  const els = {};

  document.addEventListener("DOMContentLoaded", init);

  async function init() {
    const root = document.getElementById("timelineApp");
    if (!root || typeof d3 === "undefined") return;

    els.root = root;
    els.focus = d3.select("#timelineCanvas");
    els.panel = document.getElementById("timelinePanel");
    els.status = document.getElementById("timelineStatus");
    els.legend = document.getElementById("timelineLegend");
    els.from = document.getElementById("timelineFrom");
    els.to = document.getElementById("timelineTo");

    root.querySelectorAll(".timeline-mode").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.mode = btn.dataset.mode || "type";
        state.selected = null;
        root.querySelectorAll(".timeline-mode").forEach((other) => {
          const active = other === btn;
          other.classList.toggle("is-active", active);
          other.setAttribute("aria-pressed", active ? "true" : "false");
        });
        render();
      });
    });

    if (els.from) {
      els.from.addEventListener("change", () => {
        const next = Number(els.from.value);
        if (!Number.isFinite(next)) return;
        state.from = Math.min(next, state.to);
        syncRangeControls();
        writeRange();
        render();
      });
    }
    if (els.to) {
      els.to.addEventListener("change", () => {
        const next = Number(els.to.value);
        if (!Number.isFinite(next)) return;
        state.to = Math.max(next, state.from);
        syncRangeControls();
        writeRange();
        render();
      });
    }

    window.addEventListener("network:tab", (event) => {
      if (event.detail?.tab === "timeline" && state.items.length) {
        requestAnimationFrame(() => render());
      }
    });

    window.addEventListener("resize", () => {
      if (!panelVisible()) return;
      render();
    });

    try {
      setStatus("Loading timeline…");
      const [catalogResponse, codeResponse] = await Promise.all([
        fetch(root.dataset.catalog || "", { credentials: "same-origin" }),
        root.dataset.code
          ? fetch(root.dataset.code, { credentials: "same-origin" }).catch(() => null)
          : Promise.resolve(null),
      ]);
      if (!catalogResponse.ok) throw new Error(`HTTP ${catalogResponse.status}`);
      const catalog = await catalogResponse.json();
      const libraryItems = (Array.isArray(catalog.items) ? catalog.items : []).filter(
        (item) => Number.isFinite(item.year)
      );
      let codeItems = [];
      if (codeResponse && codeResponse.ok) {
        const code = await codeResponse.json();
        codeItems = (Array.isArray(code.items) ? code.items : []).filter((item) =>
          Number.isFinite(item.year)
        );
      }
      state.items = libraryItems.concat(codeItems);
      const years = state.items.map((item) => item.year);
      state.yearMin = d3.min(years);
      state.yearMax = d3.max(years);
      const params = new URLSearchParams(window.location.search);
      const from = Number(params.get("from"));
      const to = Number(params.get("to"));
      state.from =
        Number.isFinite(from) && from >= state.yearMin && from <= state.yearMax ? from : state.yearMin;
      state.to = Number.isFinite(to) && to >= state.from && to <= state.yearMax ? to : state.yearMax;
      fillYearSelects();
      render();
    } catch (error) {
      console.error("Career timeline failed to load", error);
      setStatus("Could not load the library catalogue.");
    }
  }

  function panelVisible() {
    const panel = document.getElementById("network-panel-timeline");
    return panel && !panel.hidden;
  }

  function setStatus(text) {
    if (els.status) els.status.textContent = text || "";
  }

  function groupForType(type) {
    return GROUPS.find((group) => group.types.includes(type)) || GROUPS[GROUPS.length - 1];
  }

  function primaryRole(item) {
    const role = (item.roles || [])[0];
    return role || "unspecified";
  }

  function seriesKeys() {
    if (state.mode === "role") {
      const present = new Set(state.items.map(primaryRole));
      const known = ROLE_ORDER.filter((role) => present.has(role));
      const extra = [...present].filter((role) => !ROLE_ORDER.includes(role)).sort();
      return known.concat(extra);
    }
    return GROUPS.map((group) => group.id).filter((id) =>
      state.items.some((item) => groupForType(item.type).id === id)
    );
  }

  function seriesLabel(key) {
    if (state.mode === "role") return key;
    const group = GROUPS.find((entry) => entry.id === key);
    return group ? group.label : key;
  }

  function seriesColor(key) {
    if (state.mode === "role") return ROLE_COLORS[key] || "#6c757d";
    const group = GROUPS.find((entry) => entry.id === key);
    return group ? group.color : "#6c757d";
  }

  function itemKey(item) {
    return state.mode === "role" ? primaryRole(item) : groupForType(item.type).id;
  }

  function fillYearSelects() {
    [els.from, els.to].forEach((select) => {
      if (!select) return;
      select.innerHTML = "";
      for (let year = state.yearMin; year <= state.yearMax; year += 1) {
        const option = document.createElement("option");
        option.value = String(year);
        option.textContent = String(year);
        select.appendChild(option);
      }
    });
    syncRangeControls();
  }

  function syncRangeControls() {
    if (els.from) els.from.value = String(state.from);
    if (els.to) els.to.value = String(state.to);
  }

  function writeRange() {
    const url = new URL(window.location.href);
    if (state.from === state.yearMin) url.searchParams.delete("from");
    else url.searchParams.set("from", String(state.from));
    if (state.to === state.yearMax) url.searchParams.delete("to");
    else url.searchParams.set("to", String(state.to));
    history.replaceState(null, "", url);
  }

  function rows() {
    const keys = seriesKeys();
    const data = [];
    for (let year = state.yearMin; year <= state.yearMax; year += 1) {
      const row = { year };
      keys.forEach((key) => {
        row[key] = 0;
      });
      data.push(row);
    }
    const byYear = new Map(data.map((row) => [row.year, row]));
    state.items.forEach((item) => {
      const row = byYear.get(item.year);
      if (!row) return;
      const key = itemKey(item);
      row[key] = (row[key] || 0) + 1;
    });
    return data;
  }

  function render() {
    if (!state.items.length || !panelVisible()) return;

    const wrap = els.root.querySelector(".timeline-canvas-wrap");
    const width = Math.max(wrap ? wrap.clientWidth - 16 : 640, 280);
    const focusHeight = 280;
    const margin = { top: 8, right: 12, bottom: 28, left: 32 };
    const keys = seriesKeys();
    const data = rows();
    const focusData = data.filter((row) => row.year >= state.from && row.year <= state.to);
    const focusStacked = d3.stack().keys(keys)(focusData);
    const maxY =
      d3.max(focusData, (row) => keys.reduce((sum, key) => sum + (row[key] || 0), 0)) || 1;
    const inRange = state.items.filter((item) => item.year >= state.from && item.year <= state.to);

    setStatus(
      `${inRange.length} items · ${state.from}–${state.to}` +
        (state.mode === "role" ? " · primary role" : "")
    );

    const innerW = width - margin.left - margin.right;
    const innerH = focusHeight - margin.top - margin.bottom;
    const x = d3
      .scaleBand()
      .domain(focusData.map((row) => row.year))
      .range([0, innerW])
      .padding(0.15);
    const y = d3.scaleLinear().domain([0, maxY]).nice().range([innerH, 0]);

    els.focus.attr("viewBox", `0 0 ${width} ${focusHeight}`).attr("width", width).attr("height", focusHeight);
    els.focus.selectAll("*").remove();
    const focus = els.focus.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    focus
      .append("g")
      .attr("transform", `translate(0,${innerH})`)
      .call(
        d3
          .axisBottom(x)
          .tickValues(x.domain().filter((year) => focusData.length <= 12 || year % 2 === 0))
          .tickFormat(d3.format("d"))
      )
      .call((axis) => axis.selectAll("text").attr("fill", "currentColor"))
      .call((axis) => axis.selectAll("line, path").attr("stroke", "currentColor"));

    focus
      .append("g")
      .call(d3.axisLeft(y).ticks(5).tickFormat(d3.format("d")))
      .call((axis) => axis.selectAll("text").attr("fill", "currentColor"))
      .call((axis) => axis.selectAll("line, path").attr("stroke", "currentColor"));

    focus
      .selectAll("g.series")
      .data(focusStacked)
      .join("g")
      .attr("class", "series")
      .attr("fill", (layer) => seriesColor(layer.key))
      .selectAll("rect")
      .data((layer) => layer.map((segment) => ({ ...segment, key: layer.key })))
      .join("rect")
      .attr("x", (segment) => x(segment.data.year))
      .attr("y", (segment) => y(segment[1]))
      .attr("height", (segment) => Math.max(0, y(segment[0]) - y(segment[1])))
      .attr("width", x.bandwidth())
      .attr("opacity", (segment) => {
        if (!state.selected) return 1;
        if (state.selected.key !== segment.key) return 0.35;
        if (state.selected.year != null && state.selected.year !== segment.data.year) return 0.35;
        return 1;
      })
      .style("cursor", "pointer")
      .append("title")
      .text((segment) => {
        const count = segment[1] - segment[0];
        return `${segment.data.year} · ${seriesLabel(segment.key)} · ${count}`;
      });

    focus.selectAll("rect").on("click", (event, segment) => {
      state.selected = { year: segment.data.year, key: segment.key };
      render();
    });

    renderLegend(keys);
    renderPanel(inRange);
  }

  function renderLegend(keys) {
    if (!els.legend) return;
    els.legend.innerHTML = "";
    keys.forEach((key) => {
      const item = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.innerHTML = `<span class="timeline-swatch" style="background:${seriesColor(key)}"></span>${escapeHtml(seriesLabel(key))}`;
      button.addEventListener("click", () => {
        state.selected = { year: null, key };
        render();
      });
      item.appendChild(button);
      els.legend.appendChild(item);
    });
  }

  function renderPanel(inRange) {
    if (!els.panel) return;
    if (!state.selected) {
      els.panel.innerHTML =
        '<p class="timeline-panel-empty">Click a bar to see the works in that year, or a legend label to see that kind across the selected years.</p>';
      return;
    }

    const { year, key } = state.selected;
    const matches = inRange.filter((item) => {
      if (itemKey(item) !== key) return false;
      if (year != null && item.year !== year) return false;
      return true;
    });
    const heading = year != null ? `${year} · ${seriesLabel(key)}` : seriesLabel(key);
    const shown = matches.slice(0, 40);
    const more = matches.length - shown.length;
    const links = [
      libraryLinks(key, matches),
      key === "code" || matches.some((item) => item.type === "Code")
        ? `<a href="/code/">Open /code/</a>`
        : year != null
          ? `<a href="/library/#${year}">Search ${year} in the library</a>`
          : "",
    ]
      .filter(Boolean)
      .join(" · ");

    els.panel.innerHTML = `
      <h3>${escapeHtml(heading)}</h3>
      <p class="meta">${matches.length} item${matches.length === 1 ? "" : "s"}</p>
      ${links ? `<p class="timeline-links">${links}</p>` : ""}
      <ul>
        ${shown
          .map((item) => {
            const href = item.info || item.url || "/library/";
            const detail =
              item.type === "Code"
                ? [item.repo || item.venue, item.description].filter(Boolean).join(" · ")
                : [item.type, (item.roles || [])[0], item.venue].filter(Boolean).join(" · ");
            return `<li><a href="${escapeAttr(href)}">${escapeHtml(item.title || item.id)}</a>${
              detail ? `<br><span class="meta">${escapeHtml(detail)}</span>` : ""
            }</li>`;
          })
          .join("")}
      </ul>
      ${more > 0 ? `<p class="meta">${more} more in this range.</p>` : ""}
    `;
  }

  function libraryLinks(key, matches) {
    if (key === "code" || matches.some((item) => item.type === "Code")) {
      return "";
    }
    if (state.mode === "role" && key !== "unspecified") {
      return `<a href="/library/?filter=${encodeURIComponent(key)}">Open “${escapeHtml(key)}” in the library</a>`;
    }
    const group = GROUPS.find((entry) => entry.id === key);
    if (!group) return "";
    const types = [...new Set(matches.map((item) => item.type).filter((type) => group.types.includes(type)))];
    if (!types.length) return "";
    return types
      .map(
        (type) =>
          `<a href="/library/?filter=${encodeURIComponent(type)}">${escapeHtml(type)}</a>`
      )
      .join(" · ");
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeAttr(value) {
    return escapeHtml(value).replace(/'/g, "&#39;");
  }
})();
