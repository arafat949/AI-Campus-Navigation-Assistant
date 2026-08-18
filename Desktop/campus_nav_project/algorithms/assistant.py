"""
AI Assistant - a rule-based (not ML-trained, but genuinely useful) NLU layer
over the campus graph and the algorithm knowledge base.

Handles four kinds of queries:
  1. LOCATION   - "where is the AI lab", "find K-107"
  2. ROUTE       - "how do I get from Main Gate to Building L", "route to library"
  3. ALGO_COMPARE - "which algorithm is best for shortest path", "compare BFS and A*"
  4. ALGO_INFO    - "what is the time complexity of BFS", "space complexity of IDDFS"

This is intent detection by pattern/keyword matching (not a trained model) -
appropriate and explainable for a CSE316 AI course project, and easy to
extend with more rules/aliases.
"""

import re

from algorithms.pathfinding import build_adjacency, astar, bfs


# ---------------------------------------------------------------------------
# Algorithm knowledge base - used to answer "which is best" / "complexity of X"
# ---------------------------------------------------------------------------

ALGO_KB = {
    "bfs": {
        "aliases": ["bfs", "breadth first search", "breadth-first search"],
        "name": "BFS (Breadth-First Search)",
        "time": "O(V + E)",
        "space": "O(V)  -  stores an entire frontier level in a queue",
        "best_for": "the fewest-hops path on an unweighted graph, or when all edges cost the same",
        "notes": "Explores level by level with a queue (FIFO). Guarantees the path with the "
                 "fewest edges, but NOT the lowest total distance if edge weights differ.",
    },
    "dfs": {
        "aliases": ["dfs", "depth first search", "depth-first search"],
        "name": "DFS (Depth-First Search)",
        "time": "O(V + E)",
        "space": "O(V) worst case  -  recursion / stack depth",
        "best_for": "exploring all reachable paths, checking connectivity, or maze-style "
                    "problems where memory for a queue would be expensive",
        "notes": "Goes as deep as possible before backtracking. Finds *a* path quickly but "
                 "does NOT guarantee it's the shortest one.",
    },
    "iddfs": {
        "aliases": ["iddfs", "iterative deepening", "iterative deepening dfs", "iterative deepening depth first search"],
        "name": "IDDFS (Iterative Deepening DFS)",
        "time": "O(b^d)  -  b = branching factor, d = depth of the solution (re-explores shallow nodes each pass)",
        "space": "O(d)  -  far less memory than BFS",
        "best_for": "large or unknown-depth graphs where BFS's memory use is too high, but you "
                    "still need a fewest-hops guarantee",
        "notes": "Runs depth-limited DFS repeatedly with an increasing limit. Combines DFS's low "
                 "memory with BFS's completeness, at the cost of revisiting nodes across passes.",
    },
    "astar": {
        "aliases": ["a*", "astar", "a star", "a-star"],
        "name": "A* (A-Star)",
        "time": "O(E) best case with a good heuristic, up to O(b^d) worst case",
        "space": "O(V)  -  keeps a priority queue of frontier nodes",
        "best_for": "finding the lowest-COST path efficiently when edge weights differ and a "
                    "reasonable heuristic is available",
        "notes": "Like BFS/Dijkstra but guided by a heuristic estimate of remaining distance, so "
                 "it typically expands far fewer nodes while still finding the optimal-cost path.",
    },
    "graph_coloring": {
        "aliases": ["graph coloring", "graph colouring", "coloring"],
        "name": "Graph Coloring (backtracking)",
        "time": "O(k^V) worst case  -  k = number of colors, V = number of nodes",
        "space": "O(V)",
        "best_for": "assigning conflict-free time-slots/resources where adjacent items can't share a value "
                    "(e.g. exam room scheduling)",
        "notes": "Not a pathfinding algorithm - it's a constraint satisfaction technique: try the "
                 "smallest available color at each node, backtrack when none is safe.",
    },
    "csp": {
        "aliases": ["csp", "constraint satisfaction", "n-queens", "nqueens", "backtracking"],
        "name": "CSP / Backtracking (e.g. N-Queens)",
        "time": "Exponential worst case, e.g. O(N!) for N-Queens without pruning",
        "space": "O(N)  -  depth of the recursion",
        "best_for": "problems defined purely by constraints (no numeric cost to minimize), like "
                    "N-Queens or room/time-slot booking",
        "notes": "Tries values for each variable and backtracks the moment a constraint is violated, "
                 "instead of generating every full combination.",
    },
    "minimax": {
        "aliases": ["minimax", "alpha beta", "alpha-beta", "alpha beta pruning"],
        "name": "Minimax + Alpha-Beta Pruning",
        "time": "O(b^d) plain minimax; O(b^(d/2)) with good alpha-beta pruning",
        "space": "O(d)  -  depth of the game tree being explored",
        "best_for": "two-player, zero-sum games with perfect information (e.g. Tic-Tac-Toe)",
        "notes": "Alpha-beta pruning cuts off branches that can't change the final decision, "
                 "reaching the same optimal move as plain minimax while visiting far fewer nodes.",
    },
    "fuzzy": {
        "aliases": ["fuzzy", "fuzzy logic"],
        "name": "Fuzzy Logic (rule-based)",
        "time": "O(rules)  -  linear in the number of fuzzy rules evaluated",
        "space": "O(rules)",
        "best_for": "modelling gradual, human-like judgements (like 'how crowded does this feel') "
                    "instead of a hard yes/no threshold",
        "notes": "Uses membership functions (e.g. triangular) to turn a crisp number into degrees "
                 "of 'low/medium/high', combines rules, then defuzzifies back to a crisp score.",
    },
}

PATHFINDING_ALGOS = ["bfs", "dfs", "iddfs", "astar"]

# Maps a building's internal data key to its display name at the campus level -
# not a simple "strip the word Building" rule, since AdminBuilding -> "Admin Building".
BUILDING_TO_CAMPUS_NODE = {
    "AdminBuilding": "Admin Building",
    "BuildingB": "Building B",
    "BuildingE": "Building E",
    "BuildingF": "Building F",
    "BuildingG": "Building G",
    "BuildingH": "Building H",
    "BuildingJ": "Building J",
    "BuildingK": "Building K",
    "BuildingL": "Building L",
}


def _word_pattern(alias):
    """Builds a regex for `alias` that only requires a word-boundary on a
    side where the alias itself starts/ends with an alphanumeric character.
    This lets aliases like 'a*' match correctly (the trailing '*' isn't a
    word character, so a strict \\b on that side would never match)."""
    prefix = r"(?<![a-z0-9])" if alias[0].isalnum() else ""
    suffix = r"(?![a-z0-9])" if alias[-1].isalnum() else ""
    return prefix + re.escape(alias) + suffix


def _algos_mentioned(text):
    """Returns every algorithm key mentioned in `text`, in the order they
    appear, matching longer aliases first and tracking consumed character
    spans so a short alias (e.g. 'dfs') can't match inside a longer word
    that already matched a different algorithm (e.g. 'iddfs')."""
    text = text.lower()
    candidates = [(key, alias) for key, info in ALGO_KB.items() for alias in info["aliases"]]
    candidates.sort(key=lambda pair: -len(pair[1]))

    found, matched_spans = [], []
    for key, alias in candidates:
        for m in re.finditer(_word_pattern(alias), text):
            span = m.span()
            overlaps = any(not (span[1] <= s[0] or span[0] >= s[1]) for s in matched_spans)
            if overlaps:
                continue
            matched_spans.append(span)
            if key not in found:
                found.append(key)
    return found


def _algo_lookup(text):
    found = _algos_mentioned(text)
    return found[0] if found else None


# ---------------------------------------------------------------------------
# Location resolution - matches free text to a campus-level node or a room
# ---------------------------------------------------------------------------

def _normalize(text):
    return re.sub(r"[^a-z0-9 ]", " ", text.lower()).strip()


def build_location_index(campus_data, room_info):
    """Builds a flat list of {key, display, kind, building} for every
    campus-level node and every room, used for fuzzy text matching."""
    index = []
    for node in campus_data["campus_level"]["nodes"]:
        index.append({"key": node, "display": node, "kind": "campus", "building": None, "words": set(_normalize(node).split())})

    for building_key, building in campus_data["buildings"].items():
        for room_code in building["nodes"]:
            info = room_info.get(room_code, {"name": room_code, "type": "Location"})
            words = set(_normalize(room_code).split()) | set(_normalize(info["name"]).split())
            index.append({
                "key": room_code, "display": f"{info['name']} ({room_code})",
                "kind": "room", "building": building_key, "words": words,
            })
    return index


STOPWORDS = {"the", "a", "an", "is", "where", "find", "go", "to", "from", "how", "do", "i", "get", "of", "in"}


def resolve_location(text, location_index):
    """Scores every indexed location by word overlap with the query and
    returns the single best match (or None if nothing scores above threshold)."""
    query_words = set(_normalize(text).split()) - STOPWORDS
    if not query_words:
        return None

    # exact room-code match short-circuits (e.g. "K-107")
    code_query = text.strip().upper()
    for entry in location_index:
        if entry["kind"] == "room" and entry["key"].upper() == code_query:
            return entry

    best, best_score = None, 0
    for entry in location_index:
        overlap = len(query_words & entry["words"])
        if overlap > best_score:
            best, best_score = entry, overlap
    return best if best_score > 0 else None


# ---------------------------------------------------------------------------
# Route computation helper (reuses the same BFS/A* used by Find Route)
# ---------------------------------------------------------------------------

def compute_route(start_entry, goal_entry, campus_data):
    if start_entry["kind"] == "room" and goal_entry["kind"] == "room" and start_entry["building"] == goal_entry["building"]:
        building = campus_data["buildings"][start_entry["building"]]
        nodes, edges = building["nodes"], building["edges"]
        scope_note = f"inside {start_entry['building']}"
    else:
        def to_campus_node(entry):
            if entry["kind"] == "campus":
                return entry["key"]
            return BUILDING_TO_CAMPUS_NODE.get(entry["building"], entry["building"])

        start_key, goal_key = to_campus_node(start_entry), to_campus_node(goal_entry)
        nodes, edges = campus_data["campus_level"]["nodes"], campus_data["campus_level"]["edges"]
        start_entry = {**start_entry, "campus_key": start_key}
        goal_entry = {**goal_entry, "campus_key": goal_key}
        scope_note = "at the campus level (building-to-building)"

    adj = build_adjacency(nodes, edges)
    start_key = start_entry.get("campus_key", start_entry["key"])
    goal_key = goal_entry.get("campus_key", goal_entry["key"])
    result = astar(adj, start_key, goal_key, nodes=nodes)
    return result, scope_note


# ---------------------------------------------------------------------------
# Intent detection + top-level entry point
# ---------------------------------------------------------------------------

ROUTE_PATTERNS = [
    r"from\s+(.+?)\s+to\s+(.+)",
    r"(.+?)\s+to\s+(.+)",
]
ROUTE_SINGLE_DEST_PATTERNS = [
    r"how (?:do|can) i (?:get|go) to (.+)",
    r"route to (.+)",
    r"directions to (.+)",
    r"way to (.+)",
]

COMPARE_KEYWORDS = ["best algorithm", "which algorithm", "compare", "vs", "versus", "difference between"]
COMPLEXITY_KEYWORDS = ["complexity", "big o", "big-o", "time complexity", "space complexity", "how fast", "how efficient"]


def answer_query(query, campus_data, room_info):
    q = query.strip()
    if not q:
        return "Ask me where something is, how to get somewhere, or which algorithm is best for a task."

    lower = q.lower()

    # ---- Intent: algorithm comparison ----
    if any(kw in lower for kw in COMPARE_KEYWORDS):
        return _answer_comparison(lower)

    # ---- Intent: algorithm complexity/info ----
    algo_key = _algo_lookup(lower)
    if algo_key and any(kw in lower for kw in COMPLEXITY_KEYWORDS):
        return _answer_complexity(algo_key)
    if algo_key and ("what is" in lower or "explain" in lower or "tell me about" in lower):
        return _answer_complexity(algo_key)

    # ---- Intent: route between two places ----
    route_answer = _try_answer_route(lower, campus_data, room_info)
    if route_answer:
        return route_answer

    # ---- Intent: plain location lookup ----
    index = build_location_index(campus_data, room_info)
    match = resolve_location(lower, index)
    if match:
        if match["kind"] == "campus":
            return f"{match['display']} is a campus-level location. Use Find Route to get directions there."
        return f"{match['display']} is in {match['building']}. Use Find Route to get step-by-step directions there."

    return ("I couldn't match that to a known location or question. Try: a room number (e.g. K-107), "
            "a facility name (e.g. 'AI lab'), a route ('from Main Gate to Building L'), or an algorithm "
            "question ('time complexity of A*', 'which algorithm is best for shortest path').")


def _try_answer_route(lower, campus_data, room_info):
    index = build_location_index(campus_data, room_info)

    for pattern in ROUTE_PATTERNS:
        m = re.search(pattern, lower)
        if m and ("to" in lower):
            start_text, goal_text = m.group(1), m.group(2)
            start_entry = resolve_location(start_text, index)
            goal_entry = resolve_location(goal_text, index)
            if start_entry and goal_entry and start_entry["key"] != goal_entry["key"]:
                return _format_route_answer(start_entry, goal_entry, campus_data)

    for pattern in ROUTE_SINGLE_DEST_PATTERNS:
        m = re.search(pattern, lower)
        if m:
            goal_text = m.group(1)
            goal_entry = resolve_location(goal_text, index)
            start_entry = next((e for e in index if e["key"] == "Main Gate"), None)
            if goal_entry and start_entry:
                return _format_route_answer(start_entry, goal_entry, campus_data)

    return None


def _format_route_answer(start_entry, goal_entry, campus_data):
    result, scope_note = compute_route(start_entry, goal_entry, campus_data)
    if not result["found"]:
        return f"I couldn't find a route from {start_entry['display']} to {goal_entry['display']}."

    path_str = " \u2192 ".join(result["path"])
    return (
        f"Route from {start_entry['display']} to {goal_entry['display']} ({scope_note}), found using A*: "
        f"{path_str}. Total distance: {result['distance']} units, exploring {result['nodes_explored']} nodes. "
        f"A* is used here because it finds the lowest-total-distance path efficiently by combining actual "
        f"distance so far with a heuristic estimate of what's left."
    )


def _answer_complexity(algo_key):
    info = ALGO_KB[algo_key]
    return (
        f"{info['name']}: time complexity {info['time']}; space complexity {info['space']}. "
        f"Best for: {info['best_for']}. {info['notes']}"
    )


def _answer_comparison(lower):
    mentioned = _algos_mentioned(lower)
    keys = mentioned if len(mentioned) >= 2 else PATHFINDING_ALGOS

    lines = []
    for k in keys:
        info = ALGO_KB[k]
        lines.append(f"- {info['name']}: time {info['time']}, space {info['space']}. Best for: {info['best_for']}.")

    recommendation = (
        "For this project's route finding, A* is generally the best default when edge distances "
        "vary, because it finds the lowest-cost path while exploring fewer nodes than BFS. "
        "BFS is the simplest choice if every edge has equal weight and you only care about hop-count. "
        "DFS is useful for exploring alternative paths, not for guaranteeing the shortest one. "
        "IDDFS is the right pick when memory is limited but you still need BFS-like optimality."
        if set(keys) == set(PATHFINDING_ALGOS) else ""
    )

    return "Comparison:\n" + "\n".join(lines) + ("\n\n" + recommendation if recommendation else "")