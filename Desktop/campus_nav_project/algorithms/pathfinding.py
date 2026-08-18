"""
Pathfinding algorithms used by the AI Campus Navigation Assistant.

Implements:
  - BFS   (Breadth-First Search)  -> guarantees shortest path in terms of edge COUNT
  - DFS   (Depth-First Search)    -> explores deep first, not guaranteed shortest
  - IDDFS (Iterative Deepening DFS) -> combines DFS's low memory use with BFS-like
                                       completeness, by re-running DFS with an
                                       increasing depth limit until the goal is found.

The campus is modelled as an undirected weighted graph:
    nodes = rooms / buildings / landmarks
    edges = direct walkable connections (corridor, door, pathway) with a distance

All three functions return a common result shape so the frontend can render
them interchangeably:
    {
        "path": [...],          # ordered list of node names, empty if not found
        "distance": <number>,   # total path distance (sum of edge weights)
        "nodes_explored": int,  # how many nodes the algorithm visited/expanded
        "visit_order": [...],   # order nodes were visited, used for step-by-step animation
        "found": bool
    }
"""

import heapq
import math
from collections import deque


def build_adjacency(nodes, edges):
    """Turn a node list + edge list into an adjacency list: {node: [(neighbor, weight), ...]}"""
    adj = {n: [] for n in nodes}
    for e in edges:
        a, b, w = e["from"], e["to"], e.get("distance", 1)
        adj.setdefault(a, []).append((b, w))
        adj.setdefault(b, []).append((a, w))
    return adj


def bfs(adj, start, goal):
    """Breadth-First Search - explores level by level using a queue (FIFO).
    Guarantees the path with the fewest number of edges (hops)."""
    if start not in adj or goal not in adj:
        return {"path": [], "distance": None, "nodes_explored": 0, "visit_order": [], "found": False}

    visited = {start}
    queue = deque([(start, [start], 0)])
    order = []

    while queue:
        node, path, dist = queue.popleft()
        order.append(node)
        if node == goal:
            return {"path": path, "distance": dist, "nodes_explored": len(order),
                     "visit_order": order, "found": True}
        for neighbor, w in adj.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor], dist + w))

    return {"path": [], "distance": None, "nodes_explored": len(order),
             "visit_order": order, "found": False}


def dfs(adj, start, goal):
    """Depth-First Search - explores as far as possible along each branch (recursive,
    uses a stack implicitly via recursion). Finds *a* path, not necessarily the shortest."""
    if start not in adj or goal not in adj:
        return {"path": [], "distance": None, "nodes_explored": 0, "visit_order": [], "found": False}

    visited = set()
    order = []
    best = {"path": [], "distance": None, "found": False}

    def _dfs(node, path, dist):
        visited.add(node)
        order.append(node)
        if node == goal:
            best["path"] = list(path)
            best["distance"] = dist
            best["found"] = True
            return True
        for neighbor, w in adj.get(node, []):
            if neighbor not in visited:
                path.append(neighbor)
                if _dfs(neighbor, path, dist + w):
                    return True
                path.pop()
        return False

    _dfs(start, [start], 0)
    return {"path": best["path"], "distance": best["distance"], "nodes_explored": len(order),
             "visit_order": order, "found": best["found"]}


def _circular_layout(nodes):
    """Assigns each node a point on a circle, in the same way the frontend's
    SVG visualizer lays nodes out. Used only to give A* a heuristic distance
    to work with, since real GPS/indoor coordinates weren't available.
    NOTE: because this layout is arbitrary (not true physical distance), the
    heuristic is a reasonable teaching approximation rather than a strictly
    admissible one - swap in real coordinates for production use."""
    n = len(nodes)
    coords = {}
    radius = 200
    for i, node in enumerate(nodes):
        angle = (2 * math.pi * i) / max(n, 1) - math.pi / 2
        coords[node] = (radius * math.cos(angle), radius * math.sin(angle))
    return coords


def astar(adj, start, goal, nodes=None):
    """A* search - like BFS/Dijkstra but guided by a heuristic estimate of
    remaining distance to the goal, so it expands fewer nodes in practice.
    f(n) = g(n) [cost so far] + h(n) [heuristic estimate to goal]."""
    if start not in adj or goal not in adj:
        return {"path": [], "distance": None, "nodes_explored": 0, "visit_order": [], "found": False}

    all_nodes = nodes if nodes is not None else list(adj.keys())
    coords = _circular_layout(all_nodes)

    def h(node):
        if node not in coords or goal not in coords:
            return 0
        (x1, y1), (x2, y2) = coords[node], coords[goal]
        return math.hypot(x1 - x2, y1 - y2) / 40  # scaled down to stay in the same range as edge weights

    counter = 0
    open_set = [(h(start), counter, start, [start], 0)]
    best_g = {start: 0}
    order = []

    while open_set:
        f, _, node, path, g = heapq.heappop(open_set)
        order.append(node)
        if node == goal:
            return {"path": path, "distance": g, "nodes_explored": len(order),
                     "visit_order": order, "found": True}
        for neighbor, w in adj.get(node, []):
            new_g = g + w
            if new_g < best_g.get(neighbor, math.inf):
                best_g[neighbor] = new_g
                counter += 1
                heapq.heappush(open_set, (new_g + h(neighbor), counter, neighbor, path + [neighbor], new_g))

    return {"path": [], "distance": None, "nodes_explored": len(order),
             "visit_order": order, "found": False}


def iddfs(adj, start, goal, max_depth=20):
    """Iterative Deepening DFS - runs a depth-limited DFS repeatedly, increasing the
    depth limit by 1 each time, until the goal is found or max_depth is exhausted.
    Useful when the graph is large/unknown-depth and memory needs to stay low,
    while still finding the shortest path in terms of hop-count (like BFS)."""
    if start not in adj or goal not in adj:
        return {"path": [], "distance": None, "nodes_explored": 0, "visit_order": [],
                 "found": False, "depth_reached": 0}

    total_order = []

    def dls(node, depth, path, dist, visited):
        total_order.append(node)
        if node == goal:
            return path, dist
        if depth <= 0:
            return None
        visited.add(node)
        for neighbor, w in adj.get(node, []):
            if neighbor not in visited:
                result = dls(neighbor, depth - 1, path + [neighbor], dist + w, visited)
                if result:
                    return result
        visited.discard(node)
        return None

    for depth in range(max_depth + 1):
        visited = set()
        result = dls(start, depth, [start], 0, visited)
        if result:
            path, dist = result
            return {"path": path, "distance": dist, "nodes_explored": len(total_order),
                     "visit_order": total_order, "found": True, "depth_reached": depth}

    return {"path": [], "distance": None, "nodes_explored": len(total_order),
             "visit_order": total_order, "found": False, "depth_reached": max_depth}
