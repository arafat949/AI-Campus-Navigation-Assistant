"""
Graph Coloring - used here for conflict-free exam / room time-slot allocation.

Idea: two rooms that are physically ADJACENT (share a wall / are right next to
each other) should not be given the same exam time-slot, to avoid noise and
overcrowding in the corridor between them. This is exactly the classic graph
coloring problem: adjacent nodes (rooms) must not share the same color (slot).

Implemented with backtracking (same family of algorithm as N-Queens / CSP):
try assigning the smallest available color to each node in turn, and backtrack
whenever no color is safe.
"""


def build_conflict_graph(nodes, edges):
    """edges here represent 'adjacency = conflict' (can't share a color)."""
    graph = {n: set() for n in nodes}
    for e in edges:
        a, b = e["from"], e["to"]
        graph.setdefault(a, set()).add(b)
        graph.setdefault(b, set()).add(a)
    return graph


def is_safe(graph, node, color, coloring):
    for neighbor in graph[node]:
        if coloring.get(neighbor) == color:
            return False
    return True


def color_graph(nodes, edges, num_colors):
    """Backtracking graph coloring.
    Returns whether a valid coloring exists with `num_colors` colors (time-slots),
    the assignment itself, and a step-by-step trace for visualization."""
    graph = build_conflict_graph(nodes, edges)
    coloring = {}
    steps = []

    def backtrack(index):
        if index == len(nodes):
            return True
        node = nodes[index]
        for color in range(num_colors):
            if is_safe(graph, node, color, coloring):
                coloring[node] = color
                steps.append({"node": node, "color": color, "action": "assign"})
                if backtrack(index + 1):
                    return True
                steps.append({"node": node, "color": color, "action": "backtrack"})
                del coloring[node]
        return False

    success = backtrack(0)
    return {
        "success": success,
        "coloring": coloring,
        "steps": steps,
        "colors_used": num_colors,
        "min_colors_hint": _greedy_lower_bound(graph),
    }


def _greedy_lower_bound(graph):
    """Quick greedy coloring, purely to give the user a hint of how many
    slots are realistically needed (not guaranteed minimal, but a fast estimate)."""
    order = sorted(graph, key=lambda n: -len(graph[n]))
    coloring = {}
    for node in order:
        used = {coloring[n] for n in graph[node] if n in coloring}
        color = 0
        while color in used:
            color += 1
        coloring[node] = color
    return (max(coloring.values()) + 1) if coloring else 0
