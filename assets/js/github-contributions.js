(() => {
  const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const WEEKDAY_LABELS = ["", "Mon", "", "Wed", "", "Fri", ""];
  const API = "https://github-contributions-api.jogruber.de/v4";

  document.addEventListener("DOMContentLoaded", init);

  async function init() {
    const root = document.querySelector("[data-github-contributions]");
    if (!root) return;

    const username = root.dataset.username;
    if (!username) return;

    try {
      const response = await fetch(`${API}/${encodeURIComponent(username)}?y=last`);
      if (!response.ok) return;
      const data = await response.json();
      if (!Array.isArray(data.contributions) || data.contributions.length === 0) return;
      render(root, username, data);
      root.hidden = false;
    } catch (_error) {
      // Leave the graph hidden if the contributions API is unavailable.
    }
  }

  function render(root, username, data) {
    const days = data.contributions;
    const total = data.total && data.total.lastYear != null ? data.total.lastYear : days.reduce((sum, day) => sum + (day.count || 0), 0);
    const weeks = chunkWeeks(days);

    root.replaceChildren();

    const heading = document.createElement("p");
    heading.className = "github-contributions-total";
    const count = document.createElement("a");
    count.href = `https://github.com/${username}`;
    count.textContent = `${formatCount(total)} contribution${total === 1 ? "" : "s"}`;
    heading.append(count, document.createTextNode(" in the last year"));
    root.append(heading);

    const scroller = document.createElement("div");
    scroller.className = "github-contributions-scroll";

    const graph = document.createElement("div");
    graph.className = "github-contributions-graph";
    graph.style.setProperty("--weeks", String(weeks.length));
    graph.setAttribute("role", "img");
    graph.setAttribute("aria-label", `${formatCount(total)} GitHub contributions in the last year`);

    WEEKDAY_LABELS.forEach((label, index) => {
      const weekday = document.createElement("span");
      weekday.className = "github-contributions-weekday";
      weekday.textContent = label;
      weekday.style.gridColumn = "1";
      weekday.style.gridRow = String(index + 2);
      graph.append(weekday);
    });

    let lastLabeledWeek = -10;
    weeks.forEach((week, weekIndex) => {
      const monthStart = week.find((day) => parseLocalDate(day.date).getDate() === 1);
      if (monthStart && weekIndex - lastLabeledWeek >= 2) {
        const monthLabel = document.createElement("span");
        monthLabel.className = "github-contributions-month";
        monthLabel.textContent = MONTHS[parseLocalDate(monthStart.date).getMonth()];
        monthLabel.style.gridColumn = String(weekIndex + 2);
        monthLabel.style.gridRow = "1";
        graph.append(monthLabel);
        lastLabeledWeek = weekIndex;
      }

      week.forEach((day, dayIndex) => {
        const cell = document.createElement("span");
        const level = Math.max(0, Math.min(4, Number(day.level) || 0));
        cell.className = `github-contributions-day github-contributions-day-${level}`;
        cell.title = contributionTitle(day);
        cell.style.gridColumn = String(weekIndex + 2);
        cell.style.gridRow = String(dayIndex + 2);
        graph.append(cell);
      });
    });

    scroller.append(graph);
    root.append(scroller);

    const footer = document.createElement("div");
    footer.className = "github-contributions-footer";

    const help = document.createElement("a");
    help.className = "github-contributions-help";
    help.href = "https://docs.github.com/account-and-profile/getting-started-with-your-github-profile/why-are-my-contributions-not-showing-on-my-profile";
    help.textContent = "Learn how we count contributions";
    footer.append(help);

    const legend = document.createElement("div");
    legend.className = "github-contributions-legend";
    legend.setAttribute("aria-hidden", "true");
    legend.append(document.createTextNode("Less"));
    for (let level = 0; level <= 4; level += 1) {
      const swatch = document.createElement("span");
      swatch.className = `github-contributions-day github-contributions-day-${level}`;
      legend.append(swatch);
    }
    legend.append(document.createTextNode("More"));
    footer.append(legend);

    root.append(footer);
  }

  function chunkWeeks(days) {
    const weeks = [];
    for (let i = 0; i < days.length; i += 7) {
      weeks.push(days.slice(i, i + 7));
    }
    return weeks;
  }

  function parseLocalDate(value) {
    const [year, month, day] = value.split("-").map(Number);
    return new Date(year, month - 1, day);
  }

  function formatCount(value) {
    return new Intl.NumberFormat("en-US").format(value);
  }

  function contributionTitle(day) {
    const date = parseLocalDate(day.date);
    const when = new Intl.DateTimeFormat("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    }).format(date);
    const count = day.count || 0;
    if (count === 0) return `No contributions on ${when}`;
    if (count === 1) return `1 contribution on ${when}`;
    return `${formatCount(count)} contributions on ${when}`;
  }
})();
