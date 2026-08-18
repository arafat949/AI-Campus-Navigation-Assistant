/**
 * Quick Access, Algorithm Viz tabs, Donut chart, Emergency Exit,
 * Classroom Finder, AI Assistant, Reports.
 */

const QuickAccess = (() => {
  const ITEMS = [
    { icon: "\u{1F4D6}", label: "Library", node: "Admin Building" },
    { icon: "\u2615", label: "Cafeteria", node: "Green Cafeteria" },
    { icon: "\u{1F3DB}", label: "Admin Building", node: "Admin Building" },
    { icon: "\u{1F3EB}", label: "Building K", node: "Building K" },
    { icon: "\u{1F3C3}", label: "Cricket Ground", node: "Cricket Ground" },
    { icon: "\u{1F54C}", label: "Mosque", node: "Mosque" },
  ];

  function init() {
    const grid = document.getElementById("quick-access");
    grid.innerHTML = ITEMS.map((item) =>
      '<div class="quick-access-item" data-node="' + item.node + '">' +
      '<span class="qa-icon">' + item.icon + '</span>' + item.label +
      '</div>'
    ).join("");

    grid.querySelectorAll(".quick-access-item").forEach((el) => {
      el.addEventListener("click", () => {
        RouteTab.setRouteAndFind("Main Gate", el.dataset.node);
      });
    });
  }

  return { init: init };
})();

const RouteViz = (() => {
  let activeAlgo = "astar";

  function refresh(algo) {
    if (algo) activeAlgo = algo;
    const svg = document.getElementById("viz-svg");
    const result = window.lastRouteResults ? window.lastRouteResults[activeAlgo] : null;
    const graph = window.lastRouteGraph;
    if (!result || !graph) {
      svg.innerHTML = "";
      return;
    }
    animateGraphSVG(svg, graph.nodes, graph.edges, result, { width: 300, height: 160, stepDelay: 160 });
  }

  function init() {
    document.querySelectorAll("#viz-tabs .tab-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll("#viz-tabs .tab-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        refresh(btn.dataset.algo);
      });
    });
  }

  return { init: init, refresh: refresh };
})();

const SystemOverview = (() => {
  const COLORS = { Lab: "#1f9d55", Classroom: "#2a78d6", Office: "#e0a92e", Facility: "#993c1d", Utility: "#9aa3b5" };

  function polar(cx, cy, r, angleDeg) {
    const rad = (angleDeg * Math.PI) / 180;
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
  }

  function drawDonut(svg, categories, total) {
    const cx = 60, cy = 60, r = 50, stroke = 16;
    let angle = -90;
    let paths = "";
    Object.keys(categories).forEach((label) => {
      const count = categories[label];
      if (!count) return;
      const fraction = count / total;
      const sweep = fraction * 360;
      const large = sweep > 180 ? 1 : 0;
      const start = polar(cx, cy, r, angle);
      const end = polar(cx, cy, r, angle + sweep);
      paths += '<path d="M ' + start.x + ' ' + start.y + ' A ' + r + ' ' + r + ' 0 ' + large + ' 1 ' + end.x + ' ' + end.y + '"' +
        ' stroke="' + (COLORS[label] || "#ccc") + '" stroke-width="' + stroke + '" fill="none" stroke-linecap="butt" />';
      angle += sweep;
    });
    svg.innerHTML = paths +
      '<text x="60" y="56" text-anchor="middle" font-size="16" font-weight="600" fill="#1c2333">' + total + '</text>' +
      '<text x="60" y="72" text-anchor="middle" font-size="9" fill="#6b7488">Total Rooms</text>';
  }

  async function init() {
    const res = await fetch("/api/stats");
    const stats = await res.json();
    const svg = document.getElementById("donut-svg");
    drawDonut(svg, stats.categories, stats.total_rooms);

    const legend = document.getElementById("donut-legend");
    legend.innerHTML = Object.keys(stats.categories)
      .filter((label) => stats.categories[label] > 0)
      .map((label) => {
        const count = stats.categories[label];
        const pct = Math.round((count / stats.total_rooms) * 100);
        return '<div class="donut-legend-item"><span class="sw" style="background:' + (COLORS[label] || "#ccc") + '"></span>' +
          label + ' <span class="count">' + count + ' (' + pct + '%)</span></div>';
      }).join("");

    return stats;
  }

  return { init: init };
})();

async function loadDashboardStats() {
  const buildingsRes = await fetch("/api/buildings");
  const buildingsData = await buildingsRes.json();
  document.getElementById("stat-buildings").textContent = buildingsData.buildings.length;
  document.getElementById("stat-exits").textContent = buildingsData.buildings.length;

  const campusRes = await fetch("/api/graph?level=campus");
  const campusData = await campusRes.json();
  document.getElementById("stat-links").textContent = campusData.edges.length;

  const stats = await SystemOverview.init();
  document.getElementById("stat-rooms").textContent = stats.total_rooms;
  document.getElementById("stat-labs").textContent = stats.categories.Lab || 0;

  renderReportsTable(stats);
}

function renderReportsTable(stats) {
  const table = document.getElementById("reports-table");
  if (!table) return;
  const rows = Object.keys(stats.categories)
    .map((type) => {
      const count = stats.categories[type];
      const pct = Math.round((count / stats.total_rooms) * 100);
      return "<tr><td>" + type + "</td><td>" + count + "</td><td>" + pct + "%</td></tr>";
    })
    .join("");
  table.innerHTML = "<thead><tr><th>Room type</th><th>Count</th><th>% of total</th></tr></thead><tbody>" + rows + "</tbody>";
}

const EmergencyExitTab = (() => {
  async function loadBuildings() {
    const res = await fetch("/api/buildings");
    const data = await res.json();
    const sel = document.getElementById("exit-building");
    sel.innerHTML = data.buildings.map((b) => '<option value="' + b + '">' + b + '</option>').join("");
    await loadRooms();
  }

  async function loadRooms() {
    const building = document.getElementById("exit-building").value;
    const res = await fetch("/api/graph?level=building&building=" + encodeURIComponent(building));
    const data = await res.json();
    const sel = document.getElementById("exit-room");
    sel.innerHTML = data.nodes.map((n) => '<option value="' + n + '">' + n + '</option>').join("");
  }

  async function findExit() {
    const building = document.getElementById("exit-building").value;
    const start = document.getElementById("exit-room").value;
    const res = await fetch("/api/emergency-exit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ building: building, start: start }),
    });
    const result = await res.json();
    const box = document.getElementById("exit-result");
    box.style.display = "block";
    if (!result.found) {
      box.innerHTML = "<p class=\"result-line\">No exit route found.</p>";
      return;
    }
    box.innerHTML =
      '<p class="result-line">Nearest mapped exit: <strong>' + result.exit_node_name + ' (' + result.exit_node + ')</strong></p>' +
      '<p class="result-line">Distance: <strong>' + result.distance + '</strong> units</p>' +
      '<ol class="path-timeline">' + result.path.map((n) => "<li><strong>" + n + "</strong></li>").join("") + '</ol>';
  }

  function init() {
    document.getElementById("exit-building").addEventListener("change", loadRooms);
    document.getElementById("exit-find-btn").addEventListener("click", findExit);
    loadBuildings();
  }

  return { init: init };
})();

const FinderTab = (() => {
  let debounceTimer;

  async function search(query) {
    const box = document.getElementById("finder-results");
    if (!query) { box.innerHTML = ""; return; }
    const res = await fetch("/api/search?q=" + encodeURIComponent(query));
    const data = await res.json();
    box.innerHTML = data.results.length
      ? data.results.map((r) =>
          '<div class="finder-row"><div><strong>' + r.name + '</strong> (' + r.room + ') &middot; ' + r.building + '</div>' +
          '<span class="tag">' + r.type + '</span></div>').join("")
      : '<p class="muted">No matches.</p>';
  }

  function init() {
    const input = document.getElementById("finder-input");
    input.addEventListener("input", () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => search(input.value.trim()), 200);
    });
  }

  return { init: init, search: search };
})();

const AssistantTab = (() => {
  function addBubble(text, who) {
    const log = document.getElementById("assistant-log");
    const bubble = document.createElement("div");
    bubble.className = "chat-bubble " + who;
    bubble.textContent = text;
    log.appendChild(bubble);
    log.scrollTop = log.scrollHeight;
  }

  async function send() {
    const input = document.getElementById("assistant-input");
    const query = input.value.trim();
    if (!query) return;
    addBubble(query, "user");
    input.value = "";

    const res = await fetch("/api/assistant", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query }),
    });
    const data = await res.json();
    addBubble(data.reply, "bot");
  }

  function init() {
    document.getElementById("assistant-send-btn").addEventListener("click", send);
    document.getElementById("assistant-input").addEventListener("keydown", (e) => {
      if (e.key === "Enter") send();
    });
    addBubble("Hi! Ask me where something is - e.g. 'where is the AI lab'.", "bot");
  }

  return { init: init };
})();

function initLibraryShortcut() {
  const btn = document.getElementById("library-route-btn");
  if (!btn) return;
  btn.addEventListener("click", () => {
    document.querySelector('.nav-item[data-target="section-dashboard"]').click();
    RouteTab.setRouteAndFind("Main Gate", "Admin Building");
  });
}

function initGlobalSearch() {
  const input = document.getElementById("global-search");
  if (!input) return;
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && input.value.trim()) {
      document.querySelector('.nav-item[data-target="section-finder"]').click();
      document.getElementById("finder-input").value = input.value;
      FinderTab.search(input.value.trim());
    }
  });
}

function initClock() {
  const el = document.getElementById("weather-time");
  if (!el) return;
  function update() {
    el.textContent = new Date().toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
  }
  update();
  setInterval(update, 30000);
}
