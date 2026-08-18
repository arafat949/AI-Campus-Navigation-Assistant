/**
 * "Beat the Campus AI" tab: playable Tic-Tac-Toe. The human plays X, the
 * backend Minimax + Alpha-Beta engine (algorithms/minimax.py) plays O and
 * always responds with the game-theoretically optimal move.
 */

const GameTab = (() => {
  let board = Array(9).fill("");
  let gameOver = false;

  function render() {
    const el = document.getElementById("game-board");
    el.innerHTML = "";
    board.forEach((val, i) => {
      const cell = document.createElement("div");
      cell.className = "game-cell" + (val || gameOver ? " disabled" : "");
      cell.textContent = val;
      cell.addEventListener("click", () => handleHumanMove(i));
      el.appendChild(cell);
    });
  }

  async function handleHumanMove(i) {
    if (board[i] || gameOver) return;
    board[i] = "X";
    render();

    if (checkImmediateEnd()) return;

    document.getElementById("game-status").textContent = "AI thinking...";
    const res = await fetch("/api/game/move", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ board }),
    });
    const result = await res.json();

    board = result.board;
    document.getElementById("game-score").textContent = result.score;
    document.getElementById("game-nodes").textContent = result.nodes_explored;
    render();

    if (result.game_over) {
      gameOver = true;
      document.getElementById("game-status").textContent = result.result;
      render();
    } else {
      document.getElementById("game-status").textContent = "Your move (X)";
    }
  }

  function checkImmediateEnd() {
    const lines = [
      [0,1,2],[3,4,5],[6,7,8],
      [0,3,6],[1,4,7],[2,5,8],
      [0,4,8],[2,4,6],
    ];
    for (const [a,b,c] of lines) {
      if (board[a] && board[a] === board[b] && board[b] === board[c]) {
        gameOver = true;
        document.getElementById("game-status").textContent = `${board[a]} wins`;
        render();
        return true;
      }
    }
    if (board.every((c) => c)) {
      gameOver = true;
      document.getElementById("game-status").textContent = "Draw";
      render();
      return true;
    }
    return false;
  }

  function reset() {
    board = Array(9).fill("");
    gameOver = false;
    document.getElementById("game-status").textContent = "Your move (X)";
    document.getElementById("game-score").textContent = "-";
    document.getElementById("game-nodes").textContent = "-";
    render();
  }

  function init() {
    document.getElementById("game-reset-btn").addEventListener("click", reset);
    render();
  }

  return { init };
})();
