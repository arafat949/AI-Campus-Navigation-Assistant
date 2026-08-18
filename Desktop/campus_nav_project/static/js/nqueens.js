/**
 * "CSP (N-Queens)" tab: classic constraint satisfaction demo solved with
 * backtracking. Renders the resulting board and backtracking-call count.
 */

const NQueensTab = (() => {
  async function run() {
    const n = parseInt(document.getElementById("nqueens-n").value, 10);

    const res = await fetch("/api/nqueens", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ n }),
    });
    const result = await res.json();

    document.getElementById("nqueens-result").style.display = "block";
    document.getElementById("nqueens-found").textContent = result.found ? "Yes" : "No";
    document.getElementById("nqueens-calls").textContent = result.backtrack_calls;

    renderBoard(result.n, result.solution || []);
  }

  function renderBoard(n, solution) {
    const board = document.getElementById("nqueens-board");
    board.style.gridTemplateColumns = `repeat(${n}, 42px)`;
    board.innerHTML = "";
    for (let row = 0; row < n; row++) {
      for (let col = 0; col < n; col++) {
        const cell = document.createElement("div");
        const isLight = (row + col) % 2 === 0;
        cell.className = `nq-cell ${isLight ? "light" : "dark"}`;
        if (solution[row] === col) {
          cell.classList.add("queen");
          cell.textContent = "♛";
        }
        board.appendChild(cell);
      }
    }
  }

  function init() {
    document.getElementById("nqueens-run-btn").addEventListener("click", run);
    run();
  }

  return { init };
})();
