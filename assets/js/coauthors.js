(() => {
  const MIN_DEFAULT_COUNT = 2;

  const state = {
    graphUrl: "",
    people: [],
    edges: [],
    worksById: new Map(),
    showOccasional: false,
    selected: null,
    simulation: null,
    reduceMotion: false,
  };

  const els = {};

  document.addEventListener("DOMContentLoaded", init);

  async function init() {
    const root = document.getElementById("coauthorsApp");
    if (!root || typeof d3 === "undefined") return;

    els.root = root;
    els.svg = d3.select("#coauthorsCanvas");
    els.panel = document.getElementById("coauthorsPanel");
    els.status = document.getElementById("coauthorsStatus");
    els.toggle = document.getElementById("coauthorsShowOccasional");
    state.graphUrl = root.dataset.graph || "";
    state.reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (els.toggle) {
      els.toggle.addEventListener("change", () => {
        state.showOccasional = Boolean(els.toggle.checked);
        renderGraph();
      });
    }

    try {
      setStatus("Loading collaboration map…");
      const response = await fetch(state.graphUrl, { credentials: "same-origin" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const graph = await response.json();
      state.people = Array.isArray(graph.people) ? graph.people : [];
      state.edges = Array.isArray(graph.edges) ? graph.edges : [];
      state.worksById = new Map(
        (Array.isArray(graph.works) ? graph.works : []).map((work) => [work.id, work])
      );
      renderGraph();
    } catch (error) {
      console.error("Co-author graph failed to load", error);
      setStatus("Could not load the collaboration map.");
    }
  }

  function setStatus(text) {
    if (els.status) els.status.textContent = text || "";
  }

  function visiblePeople() {
    return state.people.filter(
      (person) => person.self || state.showOccasional || (person.count || 0) >= MIN_DEFAULT_COUNT
    );
  }

  function visibleIds(people) {
    return new Set(people.map((person) => person.id));
  }

  function visibleEdges(ids) {
    return state.edges.filter(
      (edge) => ids.has(edge.source) && ids.has(edge.target)
    );
  }

  function yearExtent(people) {
    const years = people
      .map((person) => person.firstYear)
      .filter((year) => typeof year === "number" && year > 0);
    if (!years.length) return [2000, 2026];
    return [Math.min(...years), Math.max(...years)];
  }

  function renderGraph() {
    const people = visiblePeople();
    const ids = visibleIds(people);
    const edges = visibleEdges(ids);

    if (!people.length) {
      els.svg.selectAll("*").remove();
      setStatus("No collaborators to show.");
      return;
    }

    const occasionalHidden = state.people.filter(
      (person) => !person.self && (person.count || 0) < MIN_DEFAULT_COUNT
    ).length;
    const label = state.showOccasional
      ? `${people.length} people`
      : `${people.length} people (${occasionalHidden} occasional hidden)`;
    setStatus(label);

    const wrap = els.root.querySelector(".coauthors-canvas-wrap");
    const width = Math.max(wrap ? wrap.clientWidth : 640, 320);
    const height = Math.max(wrap ? wrap.clientHeight : 448, 320);

    els.svg.attr("viewBox", `0 0 ${width} ${height}`).attr("width", width).attr("height", height);
    els.svg.selectAll("*").remove();

    const [yearMin, yearMax] = yearExtent(people);
    const color = d3
      .scaleSequential()
      .domain([yearMin, yearMax])
      .interpolator(d3.interpolateYlGnBu);

    const maxCount = d3.max(people, (d) => d.count || 1) || 1;
    const radius = d3.scaleSqrt().domain([1, maxCount]).range([6, 22]);
    const maxEdge = d3.max(edges, (d) => d.count || 1) || 1;
    const thickness = d3.scaleLinear().domain([1, maxEdge]).range([1, 5]);

    const nodes = people.map((person) => {
      const node = { ...person };
      if (person.self) {
        node.x = width / 2;
        node.y = height / 2;
      }
      return node;
    });
    const nodeById = new Map(nodes.map((node) => [node.id, node]));
    const links = edges.map((edge) => ({
      ...edge,
      source: nodeById.get(edge.source),
      target: nodeById.get(edge.target),
      workIds: edge.works || [],
    })).filter((edge) => edge.source && edge.target);

    const g = els.svg.append("g").attr("class", "coauthors-zoom");

    const zoom = d3
      .zoom()
      .scaleExtent([0.35, 4])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });
    els.svg.call(zoom);

    const link = g
      .append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke", "var(--global-text-color-light)")
      .attr("stroke-opacity", 0.55)
      .attr("stroke-width", (d) => thickness(d.count || 1))
      .style("cursor", "pointer")
      .on("click", (event, d) => {
        event.stopPropagation();
        showEdge(d);
      });

    const node = g
      .append("g")
      .attr("class", "nodes")
      .selectAll("g")
      .data(nodes)
      .join("g")
      .style("cursor", "pointer")
      .call(
        d3
          .drag()
          .on("start", (event, d) => {
            if (!event.active && state.simulation) state.simulation.alphaTarget(0.2).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active && state.simulation) state.simulation.alphaTarget(0);
            if (!d.self) {
              d.fx = null;
              d.fy = null;
            }
          })
      )
      .on("click", (event, d) => {
        event.stopPropagation();
        showPerson(d);
      });

    node
      .append("circle")
      .attr("r", (d) => radius(d.count || 1))
      .attr("fill", (d) => (d.self ? "var(--global-theme-color)" : color(d.firstYear || yearMin)))
      .attr("stroke", (d) => (d.self ? "var(--global-text-color)" : "var(--global-bg-color)"))
      .attr("stroke-width", (d) => (d.self ? 2.5 : 1));

    node
      .append("title")
      .text((d) => `${d.name} · ${d.count || 0} shared`);

    node
      .filter((d) => d.self || (d.count || 0) >= 3)
      .append("text")
      .text((d) => d.name.split(" ").slice(-1)[0])
      .attr("x", 0)
      .attr("y", (d) => radius(d.count || 1) + 12)
      .attr("text-anchor", "middle")
      .attr("font-size", "11px")
      .attr("fill", "var(--global-text-color)");

    els.svg.on("click", () => {
      clearPanel();
    });

    if (state.simulation) state.simulation.stop();

    state.simulation = d3
      .forceSimulation(nodes)
      .force(
        "link",
        d3
          .forceLink(links)
          .id((d) => d.id)
          .distance((d) => 40 + 80 / Math.sqrt(d.count || 1))
          .strength(0.4)
      )
      .force("charge", d3.forceManyBody().strength(-180))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius((d) => radius(d.count || 1) + 4));

    const selfNode = nodes.find((d) => d.self);
    if (selfNode) {
      selfNode.fx = width / 2;
      selfNode.fy = height / 2;
    }

    state.simulation.on("tick", () => {
      link
        .attr("x1", (d) => d.source.x)
        .attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x)
        .attr("y2", (d) => d.target.y);
      node.attr("transform", (d) => `translate(${d.x},${d.y})`);
    });

    if (state.reduceMotion) {
      state.simulation.stop();
      for (let i = 0; i < 200; i += 1) state.simulation.tick();
      link
        .attr("x1", (d) => d.source.x)
        .attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x)
        .attr("y2", (d) => d.target.y);
      node.attr("transform", (d) => `translate(${d.x},${d.y})`);
    }
  }

  function workListHtml(workIds) {
    const items = (workIds || [])
      .map((id) => state.worksById.get(id))
      .filter(Boolean)
      .sort((a, b) => (b.year || 0) - (a.year || 0) || String(a.title).localeCompare(String(b.title)));

    if (!items.length) return "<p class=\"meta\">No linked library pages.</p>";

    const lis = items
      .map((work) => {
        const year = work.year ? ` (${work.year})` : "";
        const title = escapeHtml(work.title || work.id);
        if (work.path) {
          return `<li><a href="${escapeAttr(work.path)}">${title}</a>${year}</li>`;
        }
        return `<li>${title}${year}</li>`;
      })
      .join("");
    return `<ul>${lis}</ul>`;
  }

  function showPerson(person) {
    state.selected = { type: "person", id: person.id };
    const years =
      person.firstYear && person.lastYear
        ? person.firstYear === person.lastYear
          ? String(person.firstYear)
          : `${person.firstYear}–${person.lastYear}`
        : "";
    const meta = person.self
      ? `${person.count || 0} co-authored works`
      : `${person.count || 0} shared works${years ? ` · ${years}` : ""}`;

    let ids;
    if (person.self) {
      ids = [...state.worksById.keys()];
    } else {
      const withGlen = state.edges.find((edge) => {
        const ends = [edge.source, edge.target];
        return ends.includes(person.id) && ends.includes("glen-wright");
      });
      ids = withGlen ? withGlen.works || [] : [];
    }

    els.panel.innerHTML = `
      <h3>${escapeHtml(person.name)}</h3>
      <p class="meta">${escapeHtml(meta)}</p>
      ${workListHtml(ids)}
    `;
  }

  function showEdge(edge) {
    const source = edge.source;
    const target = edge.target;
    const sourceName = source.name || source.id;
    const targetName = target.name || target.id;
    els.panel.innerHTML = `
      <h3>${escapeHtml(sourceName)} · ${escapeHtml(targetName)}</h3>
      <p class="meta">${edge.count || 0} shared works</p>
      ${workListHtml(edge.workIds || edge.works || [])}
    `;
  }

  function clearPanel() {
    state.selected = null;
    els.panel.innerHTML =
      '<p class="coauthors-panel-empty">Click a person or a link between people to see the shared works.</p>';
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
