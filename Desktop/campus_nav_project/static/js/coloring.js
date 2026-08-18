/**
 * "Graph Coloring" tab: assigns each room in a chosen building a color
 * (= exam/booking time-slot) such that adjacent rooms never share a color.
 */

const ColoringTab = (() => {
  const PALETTE = ["#1f9d55", "#2a78d6", "#eb6834", "#e0a92e", "#993c1d", "#4a3aa7"];

  async function loadBuildingsList() {
    const res = await fetch("/api/buildings");
    const data = await res.json();
    const sel = document.getElementById("coloring-building");
    sel.innerHTML = data.buildings.map((b) => `<option value="${b}">${b}</option>`).join("");
  }

  async function run() {
    const building = document.getElementById("coloring-building").value;
    const numColors = parseInt(document.getElementById("coloring-num-colors").value, 10);

    const res = await fetch("/api/coloring", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ level: "building", building, num_colors: numColors }),
    });
    const result = await res.json();

    document.getElementById("coloring-result").style.display = "block";
    document.getElementById("coloring-status").textContent = result.success
      ? "Valid conflict-free assignment found"
      : `No valid assignment with ${numColors} slots - try increasing slots`;
    document.getElementById("coloring-hint").textContent = result.min_colors_hint;

    const legend = document.getElementById("coloring-legend");
    legend.innerHTML = Array.from({ length: numColors }, (_, i) =>
      `<div class="legend-chip"><span class="legend-swatch" style="background:${PALETTE[i % PALETTE.length]}"></span>Slot ${i + 1}</div>`
    ).join("");

    const grid = document.getElementById("coloring-grid");
    const entries = Object.entries(result.coloring || {});
    grid.innerHTML = entries
      .map(([room, color]) => `<div class="room-chip" style="background:${PALETTE[color % PALETTE.length]}">${room}</div>`)
      .join("");
  }

  function init() {
    document.getElementById("coloring-run-btn").addEventListener("click", run);
    loadBuildingsList();
  }

  return { init };
})();
