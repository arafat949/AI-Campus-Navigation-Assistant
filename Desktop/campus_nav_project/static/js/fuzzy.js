/**
 * "Fuzzy Congestion" tab: sliders feed occupancy count / capacity / hour
 * into the backend fuzzy rule engine (algorithms/fuzzy.py), which returns a
 * 0-100 congestion score plus the rules that fired.
 */

const FuzzyTab = (() => {
  function syncLabels() {
    document.getElementById("fuzzy-count-out").textContent = document.getElementById("fuzzy-count").value;
    document.getElementById("fuzzy-capacity-out").textContent = document.getElementById("fuzzy-capacity").value;
    document.getElementById("fuzzy-hour-out").textContent = document.getElementById("fuzzy-hour").value;
  }

  async function run() {
    const count = document.getElementById("fuzzy-count").value;
    const capacity = document.getElementById("fuzzy-capacity").value;
    const hour = document.getElementById("fuzzy-hour").value;

    const res = await fetch("/api/fuzzy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ count, capacity, hour }),
    });
    const result = await res.json();

    document.getElementById("fuzzy-score").textContent = result.congestion_score;
    document.getElementById("fuzzy-label").textContent = result.congestion_label;
    document.getElementById("fuzzy-gauge-fill").style.width = `${result.congestion_score}%`;

    const list = document.getElementById("fuzzy-rules");
    list.innerHTML = result.fired_rules
      .map((r) => `<li>${r.rule} <em>(strength ${r.strength})</em></li>`)
      .join("");
  }

  function init() {
    ["fuzzy-count", "fuzzy-capacity", "fuzzy-hour"].forEach((id) => {
      document.getElementById(id).addEventListener("input", syncLabels);
    });
    document.getElementById("fuzzy-run-btn").addEventListener("click", run);
    syncLabels();
    run();
  }

  return { init };
})();
