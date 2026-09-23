(() => {
  document.addEventListener("DOMContentLoaded", () => {
    const root = document.getElementById("networkApp");
    if (!root) return;

    const tabs = root.querySelectorAll(".network-tab");
    const panels = root.querySelectorAll(".network-panel");

    function showTab(id, { updateHash = true } = {}) {
      tabs.forEach((tab) => {
        const active = tab.dataset.tab === id;
        tab.classList.toggle("is-active", active);
        tab.setAttribute("aria-selected", active ? "true" : "false");
      });
      panels.forEach((panel) => {
        panel.hidden = panel.dataset.tab !== id;
      });

      if (updateHash) {
        const hash = id === "citations" ? "#citations" : "#co-authors";
        if (window.location.hash !== hash) {
          history.replaceState(null, "", hash);
        }
      }

      window.dispatchEvent(new CustomEvent("network:tab", { detail: { tab: id } }));
    }

    tabs.forEach((tab) => {
      tab.addEventListener("click", () => showTab(tab.dataset.tab || "coauthors"));
    });

    window.addEventListener("hashchange", syncFromHash);
    syncFromHash();

    function syncFromHash() {
      const hash = window.location.hash.toLowerCase();
      const id = hash === "#citations" ? "citations" : "coauthors";
      showTab(id, { updateHash: false });
    }
  });
})();
