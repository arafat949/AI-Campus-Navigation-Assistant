AI Campus Navigation Assistant
CSE316 (Artificial Intelligence) Project — Green University of Bangladesh
An AI-powered campus navigation and utility system that demonstrates seven classic AI search / decision algorithms on a real graph of Green University's buildings and rooms.

1. Tech stack
Backend: Python 3 + Flask — every algorithm is implemented from scratch in algorithms/ (no external AI/search libraries used).
Frontend: HTML, CSS, vanilla JavaScript — calls the backend through a small REST API and renders results (including a live SVG graph visualization) in the browser.
Data: data/campus_graph_data.json — a two-level graph:
Campus level: Main Gate, Admin Building, and Buildings B/E/F/G/H/J/K/L
Building level: rooms inside each building, built from the floor-plan photos, with door/corridor connections mapped as graph edges.
Distances are approximated (unit-based: 1 unit ≈ one room-width, larger values between buildings) since exact measurements weren't available — this is documented directly inside the JSON file's _readme field and is a reasonable, common approach for this kind of student project.

2. How to run
pip install -r requirements.txt
python app.py
Then open http://127.0.0.1:5000 in your browser.

3. Algorithms implemented, and where
Algorithm	File	Used for
BFS	algorithms/pathfinding.py	Shortest route (fewest hops) between two rooms/buildings
DFS	algorithms/pathfinding.py	Alternative route discovery
IDDFS	algorithms/pathfinding.py	Depth-limited search that still finds the shortest hop-count path
Graph Coloring	algorithms/graph_coloring.py	Conflict-free exam/room time-slot allocation (adjacent rooms can't share a slot)
CSP (backtracking)	algorithms/csp.py	N-Queens demo + classroom/time-slot booking allocation
Minimax + Alpha-Beta	algorithms/minimax.py	"Beat the Campus AI" Tic-Tac-Toe opponent
Fuzzy Logic	algorithms/fuzzy.py	Corridor/classroom congestion estimation from occupancy % and time of day
4. Project structure
campus_nav_project/
├── app.py                     # Flask app + REST API routes
├── requirements.txt
├── data/
│   └── campus_graph_data.json # campus + building room graphs
├── algorithms/
│   ├── pathfinding.py         # BFS, DFS, IDDFS
│   ├── graph_coloring.py      # backtracking graph coloring
│   ├── csp.py                 # N-Queens + room booking CSP
│   ├── minimax.py             # Minimax + alpha-beta (Tic-Tac-Toe)
│   └── fuzzy.py                # fuzzy rule engine
├── templates/
│   └── index.html             # single-page app shell
└── static/
    ├── css/style.css
    └── js/
        ├── main.js             # tab switching, dashboard stats
        ├── graphviz.js         # shared SVG graph renderer
        ├── navigation.js       # BFS/DFS/IDDFS route finder
        ├── coloring.js         # graph coloring UI
        ├── nqueens.js          # N-Queens UI
        ├── game.js             # Minimax game UI
        └── fuzzy.js            # fuzzy logic UI
5. Notes for the report / viva
The campus-level graph models buildings as nodes; the building-level graphs model individual rooms, built directly from the official floor plan boards photographed on campus (Buildings E, F, G, H, J, K, L) and the Admin Building's fire-exit route map.
Room-adjacency (which rooms are directly connected by a corridor/door) was read off each floor plan; distances were then approximated on a unit scale, which is called out explicitly in the data file and can be swapped for real measurements later without changing any algorithm code.
Every algorithm returns not just the answer but also a trace (nodes explored, visit order, backtracking calls, fired fuzzy rules, etc.) so the frontend — and a viva examiner — can see how the algorithm reached its answer, not just the final result.
