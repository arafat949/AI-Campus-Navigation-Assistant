/**
 * "Find Your Route" (Dashboard) logic: BFS / DFS / IDDFS / A*.
 */

const RouteTab = (() => {
  let currentNodes = [];
  let currentEdges = [];
  window.lastRouteResults = {};

  const ALGO_LABELS = { bfs: "BFS", dfs: "DFS", iddfs: "IDDFS", astar: "A*" };

  async function loadBuildingsList() {
    const res = await fetch("/api/buildings");
    const data = await res.json();
    const sel = document.getElementById("route-building");
    sel.innerHTML = data.buildings.map((b) => '<option value="' + b + '">' + b + '</option>').join("");
    return data.buildings;
  }

  async function loadGraph() {
    const level = document.getElementById("route-level").value;
    const building = document.getElementById("route-building").value;
    const url = level === "campus"
      ? "/api/graph?level=campus"
      : "/api/graph?level=building&building=" + encodeURIComponent(building);
    const res = await fetch(url);
    const data = await res.json();
    currentNodes = data.nodes;
    currentEdges = data.edges;

    const startSel = document.getElementById("route-start");
    const goalSel = document.getElementById("route-goal");
    const options = currentNodes.map((n) => '<option value="' + n + '">' + n + '</option>').join("");
    startSel.innerHTML = options;
    goalSel.innerHTML = options;
    if (currentNodes.length > 1) goalSel.selectedIndex = currentNodes.length - 1;

    const svg = document.getElementById("route-svg");
    renderGraphSVG(svg, currentNodes, currentEdges, { width: 600, height: 380 });
  }

  async function findRoute() {
    const level = document.getElementById("route-level").value;
    const building = document.getElementById("route-building").value;
    const start = document.getElementById("route-start").value;
    const goal = document.getElementById("route-goal").value;
    const algorithm = document.querySelector('input[name="algo"]:checked').value;

    const res = await fetch("/api/pathfind", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ level: level, building: building, start: start, goal: goal, algorithm: algorithm }),
    });
    const result = await res.json();
    window.lastRouteResults[algorithm] = result;
    window.lastRouteGraph = { nodes: currentNodes, edges: currentEdges };

    renderRouteResult(result, algorithm);

    const svg = document.getElementById("route-svg");
    animateGraphSVG(svg, currentNodes, currentEdges, result, { width: 600, height: 380, stepDelay: 90 });

    if (window.RouteViz) window.RouteViz.refresh(algorithm);
  }

  function renderRouteResult(result, algorithm) {
    const box = document.getElementById("route-result");
    box.style.display = "block";
    document.getElementById("route-distance").textContent = result.found ? String(result.distance) : "N/A";
    document.getElementById("route-algo-used").textContent = ALGO_LABELS[algorithm] || algorithm;
    document.getElementById("route-explored").textContent = result.nodes_explored;

    const list = document.getElementById("route-path-list");
    if (!result.found) {
      list.innerHTML = "<li><strong>No route found</strong><span>Try a different scope or algorithm</span></li>";
      return;
    }
    list.innerHTML = (result.path || [])
      .map((n, i) => {
        const label = i === 0 ? "Start" : (i === result.path.length - 1 ? "Destination" : "Via");
        return "<li><strong>" + n + "</strong><span>" + label + "</span></li>";
      })
      .join("");
  }

  function init() {
    document.getElementById("route-level").addEventListener("change", (e) => {
      document.getElementById("route-building-wrap").style.display =
        e.target.value === "building" ? "block" : "none";
      loadGraph();
    });
    document.getElementById("route-building").addEventListener("change", loadGraph);
    document.getElementById("route-find-btn").addEventListener("click", findRoute);

    loadBuildingsList().then(loadGraph);
  }

  function setRouteAndFind(startNode, goalNode) {
    document.getElementById("route-level").value = "campus";
    document.getElementById("route-building-wrap").style.display = "none";
    loadGraph().then(() => {
      document.getElementById("route-start").value = startNode;
      document.getElementById("route-goal").value = goalNode;
      findRoute();
    });
  }

  return { init: init, setRouteAndFind: setRouteAndFind, findRoute: findRoute };
})();
