(() => {
  const MIN_DEFAULT = 2;

  const state = {
    graphUrl: "",
    people: [],
    edges: [],
    worksById: new Map(),
    direction: "both",
    showOccasional: false,
    simulation: null,
    reduceMotion: false,
  };

  const els = {};

  document.addEventListener("DOMContentLoaded", init);

  async function init() {
    const root = document.getElementById("citationsApp");
    if (!root || typeof d3 === "undefined") return;

    els.root = root;
    els.svg = d3.select("#citationsCanvas");
    els.panel = document.getElementById("citationsPanel");
    els.status = document.getElementById("citationsStatus");
    els.toggle = document.getElementById("citationsShowOccasional");
    state.graphUrl = root.dataset.graph || "";
    state.reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    root.querySelectorAll(".citations-filter").forEach((btn) => {
      btn.addEventListener("click", () => {
        root.querySelectorAll(".citations-filter").forEach((other) => {
          other.classList.toggle("is-active", other === btn);
          other.setAttribute("aria-pressed", other === btn ? "true" : "false");
        });
        state.direction = btn.dataset.direction || "both";
        renderGraph();
      });
    });

    if (els.toggle) {
      els.toggle.addEventListener("change", () => {
        state.showOccasional = Boolean(els.toggle.checked);
        renderGraph();
      });
    }

    window.addEventListener("network:tab", (event) => {
      if (event.detail?.tab === "citations" && state.people.length) {
        requestAnimationFrame(() => renderGraph());
      }
    });

    try {
      setStatus("Loading citation map…");
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
      console.error("Citation graph failed to load", error);
      setStatus("Could not load the citation map. Run the citations build script.");
    }
  }

  function setStatus(text) {
    if (els.status) els.status.textContent = text || "";
  }

  function personScore(person) {
    return (person.citedMe || 0) + (person.citedByMe || 0);
  }

  function visiblePeople() {
    return state.people.filter((person) => {
      if (person.self) return true;
      const score = personScore(person);
      if (!state.showOccasional && score < MIN_DEFAULT) return false;
      if (state.direction === "cites_me") return (person.citedMe || 0) > 0;
      if (state.direction === "i_cite") return (person.citedByMe || 0) > 0;
      return score > 0;
    });
  }

  function visibleEdges(ids) {
    return state.edges.filter((edge) => {
      if (!ids.has(edge.source) || !ids.has(edge.target)) return false;
      if (state.direction === "both") return true;
      return edge.direction === state.direction;
    });
  }

  function renderGraph() {
    const people = visiblePeople();
    const ids = new Set(people.map((p) => p.id));
    const edges = visibleEdges(ids);

    if (!people.length) {
      els.svg.selectAll("*").remove();
      setStatus("No citation neighbours to show.");
      return;
    }

    const hidden = state.people.filter((p) => !p.self && personScore(p) < MIN_DEFAULT).length;
    setStatus(
      state.showOccasional
        ? `${people.length} people · ${edges.length} links`
        : `${people.length} people · ${edges.length} links (${hidden} occasional hidden)`
    );

    const wrap = els.root.querySelector(".citations-canvas-wrap");
    if (wrap && wrap.clientWidth === 0) return;
    const width = Math.max(wrap ? wrap.clientWidth : 640, 320);
    const height = Math.max(wrap ? wrap.clientHeight : 448, 320);

    els.svg.attr("viewBox", `0 0 ${width} ${height}`).attr("width", width).attr("height", height);
    els.svg.selectAll("*").remove();

    const defs = els.svg.append("defs");
    defs
      .append("marker")
      .attr("id", "arrow-cites-me")
      .attr("viewBox", "0 -4 8 8")
      .attr("refX", 10)
      .attr("refY", 0)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-4L8,0L0,4")
      .attr("fill", "#2a6f97");
    defs
      .append("marker")
      .attr("id", "arrow-i-cite")
      .attr("viewBox", "0 -4 8 8")
      .attr("refX", 10)
      .attr("refY", 0)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-4L8,0L0,4")
      .attr("fill", "#b5651d");

    const maxCount = d3.max(people, (d) => personScore(d) || 1) || 1;
    const radius = d3.scaleSqrt().domain([1, maxCount]).range([6, 22]);
    const maxEdge = d3.max(edges, (d) => d.count || 1) || 1;
    const thickness = d3.scaleLinear().domain([1, maxEdge]).range([1.2, 4.5]);

    const nodes = people.map((person) => {
      const node = { ...person };
      if (person.self) {
        node.x = width / 2;
        node.y = height / 2;
      }
      return node;
    });
    const nodeById = new Map(nodes.map((node) => [node.id, node]));
    const links = edges
      .map((edge) => ({
        ...edge,
        source: nodeById.get(edge.source),
        target: nodeById.get(edge.target),
        workIds: edge.works || [],
      }))
      .filter((edge) => edge.source && edge.target)
      .sort((a, b) => (a.direction === "co_cite" ? 0 : 1) - (b.direction === "co_cite" ? 0 : 1));

    const g = els.svg.append("g").attr("class", "citations-zoom");
    const zoom = d3
      .zoom()
      .scaleExtent([0.35, 4])
      .on("zoom", (event) => g.attr("transform", event.transform));
    els.svg.call(zoom);

    const link = g
      .append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke", (d) => {
        if (d.direction === "co_cite") return "#8d99a6";
        return d.direction === "cites_me" ? "#2a6f97" : "#b5651d";
      })
      .attr("stroke-opacity", (d) => (d.direction === "co_cite" ? 0.45 : 0.65))
      .attr("stroke-width", (d) => (d.direction === "co_cite" ? 1 : thickness(d.count || 1)))
      .attr("marker-end", (d) => {
        if (d.direction === "co_cite") return null;
        return d.direction === "cites_me" ? "url(#arrow-cites-me)" : "url(#arrow-i-cite)";
      })
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
      .attr("r", (d) => radius(personScore(d) || 1))
      .attr("fill", (d) => {
        if (d.self) return "var(--global-theme-color)";
        if ((d.citedMe || 0) > 0 && (d.citedByMe || 0) > 0) return "#5c6b73";
        if ((d.citedMe || 0) > 0) return "#2a6f97";
        return "#b5651d";
      })
      .attr("stroke", (d) => (d.self ? "var(--global-text-color)" : "var(--global-bg-color)"))
      .attr("stroke-width", (d) => (d.self ? 2.5 : 1));

    node
      .append("title")
      .text(
        (d) =>
          `${d.name} · cites me ${d.citedMe || 0} · I cite ${d.citedByMe || 0}`
      );

    node
      .filter((d) => d.self || personScore(d) >= 3)
      .append("text")
      .text((d) => d.name.split(" ").slice(-1)[0])
      .attr("y", (d) => radius(personScore(d) || 1) + 12)
      .attr("text-anchor", "middle")
      .attr("font-size", "11px")
      .attr("fill", "var(--global-text-color)");

    els.svg.on("click", () => clearPanel());

    if (state.simulation) state.simulation.stop();
    state.simulation = d3
      .forceSimulation(nodes)
      .force(
        "link",
        d3
          .forceLink(links)
          .id((d) => d.id)
          .distance((d) =>
            d.direction === "co_cite" ? 130 : 50 + 70 / Math.sqrt(d.count || 1)
          )
          .strength((d) => (d.direction === "co_cite" ? 0.04 : 0.35))
      )
      .force("charge", d3.forceManyBody().strength(-160))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius((d) => radius(personScore(d) || 1) + 4));

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

    if (!items.length) return '<p class="meta">No linked papers.</p>';

    const lis = items
      .map((work) => {
        const year = work.year ? ` (${work.year})` : "";
        const title = escapeHtml(work.title || work.id);
        if (work.path) {
          return `<li><a href="${escapeAttr(work.path)}">${title}</a>${year}</li>`;
        }
        if (work.doi) {
          return `<li><a href="https://doi.org/${escapeAttr(work.doi)}" rel="noopener">${title}</a>${year}</li>`;
        }
        if (work.url) {
          return `<li><a href="${escapeAttr(work.url)}" rel="noopener">${title}</a>${year}</li>`;
        }
        return `<li>${title}${year}</li>`;
      })
      .join("");
    return `<ul>${lis}</ul>`;
  }

  function showPerson(person) {
    const meta = person.self
      ? `Cited by others across ${person.citedMe || 0} papers · cites others across ${person.citedByMe || 0} papers`
      : `Cites Glen in ${person.citedMe || 0} papers · cited by Glen in ${person.citedByMe || 0} papers`;

    const relevant = state.edges.filter((edge) => {
      const ends = [edge.source, edge.target];
      if (!ends.includes(person.id)) return false;
      if (state.direction === "both") return true;
      return edge.direction === state.direction;
    });
    const ids = [...new Set(relevant.flatMap((edge) => edge.works || []))];

    els.panel.innerHTML = `
      <h3>${escapeHtml(person.name)}</h3>
      <p class="meta">${escapeHtml(meta)}</p>
      ${workListHtml(ids)}
    `;
  }

  function showEdge(edge) {
    const sourceName = edge.source.name || edge.source.id;
    const targetName = edge.target.name || edge.target.id;
    const label =
      edge.direction === "co_cite"
        ? `${sourceName} and ${targetName} co-authored a paper that cites Glen`
        : edge.direction === "cites_me"
          ? `${sourceName} cites Glen`
          : `Glen cites ${targetName}`;
    els.panel.innerHTML = `
      <h3>${escapeHtml(label)}</h3>
      <p class="meta">${edge.count || 0} papers</p>
      ${workListHtml(edge.workIds || edge.works || [])}
    `;
  }

  function clearPanel() {
    els.panel.innerHTML =
      '<p class="citations-panel-empty">Click a person or an arrow to see the papers behind the link.</p>';
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
