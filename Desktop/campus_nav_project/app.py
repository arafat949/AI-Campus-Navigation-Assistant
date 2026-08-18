"""
AI Campus Navigation Assistant - Flask backend.
Green University of Bangladesh | CSE316 Project

Exposes REST endpoints that the HTML/CSS/JS frontend calls to run each
algorithm. All algorithm logic lives in the `algorithms/` package -
this file is purely routing + request/response glue.
"""

import json
import os
import re
from algorithms.pathfinding import build_adjacency, bfs, dfs, iddfs, astar
from algorithms.assistant import answer_query

from flask import Flask, jsonify, request, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, jsonify, request, render_template

from algorithms.pathfinding import build_adjacency, bfs, dfs, iddfs, astar
from algorithms.graph_coloring import color_graph
from algorithms.csp import solve_nqueens, solve_room_booking
from algorithms.minimax import best_move, EMPTY
from algorithms.fuzzy import estimate_congestion

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "campus_graph_data.json")
ROOM_INFO_PATH = os.path.join(BASE_DIR, "data", "room_info.json")

app = Flask(__name__)
app.secret_key = "cse316-green-university-campus-nav-demo"  # fine for a class project; use env var in real deployment

USERS_PATH = os.path.join(BASE_DIR, "data", "users.json")


def load_users():
    if not os.path.exists(USERS_PATH):
        return {}
    with open(USERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

with open(DATA_PATH, "r", encoding="utf-8") as f:
    CAMPUS_DATA = json.load(f)

with open(ROOM_INFO_PATH, "r", encoding="utf-8") as f:
    ROOM_INFO = json.load(f)


def get_room_info(code):
    """Looks up a room's descriptive name + type; falls back gracefully for
    building/campus-level nodes (e.g. 'Main Gate') that aren't in room_info.json."""
    return ROOM_INFO.get(code, {"name": code, "type": "Location"})


def get_graph_level(level, building=None):
    """Returns (nodes, edges) for either the campus-level graph or a specific building's graph."""
    if level == "campus":
        data = CAMPUS_DATA["campus_level"]
        return data["nodes"], data["edges"]
    building_data = CAMPUS_DATA["buildings"].get(building)
    if not building_data:
        return [], []
    return building_data["nodes"], building_data["edges"]


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/auth/signup", methods=["POST"])
def auth_signup():
    payload = request.get_json()
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are all required."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    users = load_users()
    if email in users:
        return jsonify({"error": "An account with this email already exists."}), 400

    users[email] = {"name": name, "password_hash": generate_password_hash(password)}
    save_users(users)
    session["user_email"] = email
    return jsonify({"name": name, "email": email})


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    payload = request.get_json()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    users = load_users()
    user = users.get(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password."}), 401

    session["user_email"] = email
    return jsonify({"name": user["name"], "email": email})


@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    session.pop("user_email", None)
    return jsonify({"ok": True})


@app.route("/api/auth/me")
def auth_me():
    email = session.get("user_email")
    if not email:
        return jsonify({"user": None})
    users = load_users()
    user = users.get(email)
    if not user:
        session.pop("user_email", None)
        return jsonify({"user": None})
    return jsonify({"user": {"name": user["name"], "email": email}})


# ---------------------------------------------------------------------------
# Graph data
# ---------------------------------------------------------------------------

@app.route("/api/graph")
def api_graph():
    level = request.args.get("level", "campus")
    building = request.args.get("building")
    nodes, edges = get_graph_level(level, building)
    entry_node = None
    if level != "campus":
        entry_node = CAMPUS_DATA["buildings"].get(building, {}).get("entry_node")
    return jsonify({"nodes": nodes, "edges": edges, "entry_node": entry_node})


@app.route("/api/buildings")
def api_buildings():
    return jsonify({"buildings": list(CAMPUS_DATA["buildings"].keys())})


@app.route("/api/room-info/<code>")
def api_room_info(code):
    return jsonify(get_room_info(code))


@app.route("/api/stats")
def api_stats():
    """Computed (real, not fabricated) facility-type breakdown across all
    mapped buildings, using room_info.json, for the dashboard's donut chart."""
    categories = {"Lab": 0, "Classroom": 0, "Office": 0, "Facility": 0, "Utility": 0}
    total_rooms = 0
    for building in CAMPUS_DATA["buildings"].values():
        for node in building["nodes"]:
            total_rooms += 1
            info = get_room_info(node)
            categories[info["type"]] = categories.get(info["type"], 0) + 1

    campus_edges = len(CAMPUS_DATA["campus_level"]["edges"])
    return jsonify({
        "total_buildings": len(CAMPUS_DATA["buildings"]),
        "total_rooms": total_rooms,
        "total_campus_links": campus_edges,
        "categories": categories,
    })


# ---------------------------------------------------------------------------
# BFS / DFS / IDDFS pathfinding
# ---------------------------------------------------------------------------

@app.route("/api/pathfind", methods=["POST"])
def api_pathfind():
    payload = request.get_json()
    level = payload.get("level", "campus")
    building = payload.get("building")
    algorithm = payload.get("algorithm", "bfs")
    start = payload["start"]
    goal = payload["goal"]

    nodes, edges = get_graph_level(level, building)
    adj = build_adjacency(nodes, edges)

    if algorithm == "bfs":
        result = bfs(adj, start, goal)
    elif algorithm == "dfs":
        result = dfs(adj, start, goal)
    elif algorithm == "iddfs":
        result = iddfs(adj, start, goal, max_depth=len(nodes))
    elif algorithm == "astar":
        result = astar(adj, start, goal, nodes=nodes)
    else:
        return jsonify({"error": "unknown algorithm"}), 400

    return jsonify(result)


# ---------------------------------------------------------------------------
# Graph coloring (exam / room slot allocation)
# ---------------------------------------------------------------------------

@app.route("/api/coloring", methods=["POST"])
def api_coloring():
    payload = request.get_json()
    level = payload.get("level", "building")
    building = payload.get("building")
    num_colors = int(payload.get("num_colors", 3))

    nodes, edges = get_graph_level(level, building)
    result = color_graph(nodes, edges, num_colors)
    return jsonify(result)


# ---------------------------------------------------------------------------
# CSP: N-Queens + room booking
# ---------------------------------------------------------------------------

@app.route("/api/nqueens", methods=["POST"])
def api_nqueens():
    payload = request.get_json()
    n = int(payload.get("n", 8))
    n = max(4, min(n, 12))
    result = solve_nqueens(n)
    return jsonify(result)


@app.route("/api/roombooking", methods=["POST"])
def api_roombooking():
    payload = request.get_json()
    result = solve_room_booking(payload["bookings"], payload["rooms"], payload["slots"])
    return jsonify(result)


# ---------------------------------------------------------------------------
# Minimax + Alpha-Beta game
# ---------------------------------------------------------------------------

@app.route("/api/game/move", methods=["POST"])
def api_game_move():
    payload = request.get_json()
    board = payload.get("board", [EMPTY] * 9)
    result = best_move(board)
    return jsonify(result)


# ---------------------------------------------------------------------------
# Classroom / Facility Finder - simple keyword search across all room data
# ---------------------------------------------------------------------------

@app.route("/api/search")
def api_search():
    """Search rooms by code (e.g. 'K-107') OR by descriptive name/type
    (e.g. 'AI lab', 'toilet', 'library') using room_info.json."""
    query = request.args.get("q", "").strip().lower()
    if not query:
        return jsonify({"results": []})

    results = []
    query_pattern = re.compile(r"\b" + re.escape(query), re.IGNORECASE)
    for building_name, building in CAMPUS_DATA["buildings"].items():
        for node in building["nodes"]:
            info = get_room_info(node)
            code_match = query in node.lower() and (len(query) >= 2 and (any(ch.isdigit() for ch in query) or "-" in query))
            name_match = bool(query_pattern.search(info["name"])) or bool(query_pattern.search(info["type"]))
            if code_match or name_match:
                results.append({
                    "building": building_name,
                    "room": node,
                    "name": info["name"],
                    "type": info["type"],
                })

    return jsonify({"results": results[:25]})


# ---------------------------------------------------------------------------
# Emergency Exit - BFS from a room to its building's mapped exit/entry point
# ---------------------------------------------------------------------------

@app.route("/api/emergency-exit", methods=["POST"])
def api_emergency_exit():
    payload = request.get_json()
    building = payload["building"]
    start = payload["start"]

    building_data = CAMPUS_DATA["buildings"].get(building)
    if not building_data:
        return jsonify({"error": "unknown building"}), 400

    exit_node = building_data.get("entry_node")
    adj = build_adjacency(building_data["nodes"], building_data["edges"])
    result = bfs(adj, start, exit_node)
    result["exit_node"] = exit_node
    result["exit_node_name"] = get_room_info(exit_node)["name"]
    return jsonify(result)


# ---------------------------------------------------------------------------
# AI Assistant - lightweight rule-based Q&A over the campus graph
# (keyword matching, not a trained NLP model - documented as such in README)
# ---------------------------------------------------------------------------

@app.route("/api/assistant", methods=["POST"])
def api_assistant():
    payload = request.get_json()
    query = payload.get("query", "").strip()

    if not query:
        return jsonify({"reply": "Ask me where something is, how to get somewhere, or which algorithm is best for a task."})

    reply = answer_query(query, CAMPUS_DATA, ROOM_INFO)
    return jsonify({"reply": reply})
# ---------------------------------------------------------------------------
# Fuzzy logic congestion estimator
# ---------------------------------------------------------------------------

@app.route("/api/fuzzy", methods=["POST"])
def api_fuzzy():
    payload = request.get_json()
    result = estimate_congestion(
        current_count=float(payload.get("count", 0)),
        capacity=float(payload.get("capacity", 1)),
        hour=float(payload.get("hour", 10)),
    )
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
