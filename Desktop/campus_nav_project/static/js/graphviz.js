/**
 * Reusable helper to draw a node/edge graph inside an <svg>, using an
 * elliptical layout, plus an animated step-by-step version that reveals
 * each explored node one at a time (so you can actually see how BFS/DFS/
 * IDDFS/A* search differently) before finally highlighting the path.
 */

function renderGraphSVG(svgEl, nodes, edges, opts = {}) {
  const { highlightPath = [], visitOrder = [], width = 600, height = 380 } = opts;
  const cx = width / 2, cy = height / 2;

  const marginX = Math.max(30, width * 0.14);
  const marginY = Math.max(24, height * 0.18);
  const rx = width / 2 - marginX;
  const ry = height / 2 - marginY;
  const isSmall = width < 400;
  const fontSize = isSmall ? 7 : 9;
  const nodeR = isSmall ? 4 : 5;
  const nodeRHighlight = isSmall ? 6 : 8;

  const positions = {};
  nodes.forEach((n, i) => {
    const angle = (2 * Math.PI * i) / nodes.length - Math.PI / 2;
    positions[n] = {
      x: cx + rx * Math.cos(angle),
      y: cy + ry * Math.sin(angle),
    };
  });

  const pathEdgeSet = new Set();
  for (let i = 0; i < highlightPath.length - 1; i++) {
    pathEdgeSet.add(highlightPath[i] + "|" + highlightPath[i + 1]);
    pathEdgeSet.add(highlightPath[i + 1] + "|" + highlightPath[i]);
  }
  const visitedSet = new Set(visitOrder);
  const pathSet = new Set(highlightPath);
  const mostRecent = visitOrder.length ? visitOrder[visitOrder.length - 1] : null;

  let svg = "";

  edges.forEach((e) => {
    const a = positions[e.from], b = positions[e.to];
    if (!a || !b) return;
    const onPath = pathEdgeSet.has(e.from + "|" + e.to);
    svg += '<line x1="' + a.x + '" y1="' + a.y + '" x2="' + b.x + '" y2="' + b.y + '"' +
      ' stroke="' + (onPath ? "#2a78d6" : "#d8dde5") + '"' +
      ' stroke-width="' + (onPath ? 3.5 : 1.4) + '" stroke-linecap="round" />';
  });

  nodes.forEach((n) => {
    const p = positions[n];
    if (!p) return;
    let fill = "#c7ccd6";
    if (visitedSet.has(n)) fill = "#9fd6b6";
    if (n === mostRecent && pathSet.size === 0) fill = "#e0a92e";
    if (pathSet.has(n)) fill = "#1f9d55";
    const isEndpoint = highlightPath[0] === n || highlightPath[highlightPath.length - 1] === n;
    if (isEndpoint && pathSet.has(n)) fill = (n === highlightPath[0]) ? "#1f9d55" : "#d84c4c";
    const r = (pathSet.has(n) || n === mostRecent) ? nodeRHighlight : nodeR;
    svg += '<circle cx="' + p.x + '" cy="' + p.y + '" r="' + r + '" fill="' + fill + '" stroke="#0f2418" stroke-width="1" />';

    let shouldLabel = true;
    if (isSmall && pathSet.size === 0) {
      shouldLabel = (n === mostRecent);
    } else if (isSmall) {
      shouldLabel = pathSet.has(n);
    }
    if (shouldLabel) {
      svg += '<text x="' + p.x + '" y="' + (p.y - (r + 5)) + '" font-size="' + fontSize + '" text-anchor="middle" fill="#1c2333">' + escapeXml(n) + '</text>';
    }
  });

  svgEl.setAttribute("viewBox", "0 0 " + width + " " + height);
  svgEl.innerHTML = svg;
}

function animateGraphSVG(svgEl, nodes, edges, result, opts = {}) {
  const width = opts.width || 300;
  const height = opts.height || 160;
  const stepDelay = opts.stepDelay || 160;
  const order = result.visit_order || [];

  if (svgEl._animTimer) clearTimeout(svgEl._animTimer);

  if (order.length === 0) {
    renderGraphSVG(svgEl, nodes, edges, { width: width, height: height });
    return;
  }

  let i = 0;
  function step() {
    i++;
    const partial = order.slice(0, i);
    const isLastStep = i >= order.length;
    renderGraphSVG(svgEl, nodes, edges, {
      visitOrder: partial,
      highlightPath: isLastStep ? (result.path || []) : [],
      width: width,
      height: height,
    });
    if (!isLastStep) {
      svgEl._animTimer = setTimeout(step, stepDelay);
    }
  }
  step();
}

function escapeXml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
