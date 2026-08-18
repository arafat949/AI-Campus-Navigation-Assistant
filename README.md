AI Campus Navigation Assistant
CSE316 — Artificial Intelligence Project

Green University of Bangladesh

An AI-powered campus navigation and utility system built with Python and Flask. The project demonstrates classic Artificial Intelligence algorithms using a graph-based model of the Green University of Bangladesh campus, including buildings, rooms, routes, scheduling, game intelligence, and congestion estimation.

🚀 Features
🗺️ Smart campus navigation between buildings and rooms
🔍 Route finding using BFS, DFS, and IDDFS
🎨 Conflict-free room/time-slot allocation using Graph Coloring
🧩 Classroom booking and N-Queens problem using CSP
🎮 AI-powered Tic-Tac-Toe using Minimax and Alpha-Beta Pruning
🧠 Corridor and classroom congestion estimation using Fuzzy Logic
📊 Algorithm execution traces and visualization
🌐 Interactive web-based user interface
🛠️ Tech Stack
Backend
Python 3
Flask

All AI algorithms are implemented from scratch inside the algorithms/ directory without using external AI or search libraries.

Frontend
HTML
CSS
Vanilla JavaScript
SVG-based graph visualization

The frontend communicates with the Flask backend through a REST API and displays algorithm results interactively.

Data

The campus graph data is stored in:

data/campus_graph_data.json

The system uses a two-level graph structure:

Campus Level: Main Gate, Admin Building, and Buildings B, E, F, G, H, J, K, and L.
Building Level: Individual rooms and their corridor or door connections.

Since exact physical measurements were not available, distances are approximated using a unit-based scale. Approximately:

1 unit ≈ one room width

These values can later be replaced with real measurements without changing the AI algorithm implementations.

🤖 Algorithms Implemented
Algorithm	File	Purpose
BFS	algorithms/pathfinding.py	Finds the shortest route based on the fewest hops
DFS	algorithms/pathfinding.py	Explores alternative routes
IDDFS	algorithms/pathfinding.py	Depth-limited search with iterative deepening
Graph Coloring	algorithms/graph_coloring.py	Conflict-free exam or room time-slot allocation
CSP	algorithms/csp.py	N-Queens and classroom/time-slot booking
Minimax + Alpha-Beta	algorithms/minimax.py	AI opponent for Tic-Tac-Toe
Fuzzy Logic	algorithms/fuzzy.py	Estimates classroom and corridor congestion
📂 Project Structure
campus_nav_project/
│
├── app.py                     # Flask app and REST API routes
├── requirements.txt           # Project dependencies
├── README.md                  # Project documentation
│
├── data/
│   └── campus_graph_data.json # Campus and building room graphs
│
├── algorithms/
│   ├── pathfinding.py         # BFS, DFS, IDDFS
│   ├── graph_coloring.py      # Graph Coloring algorithm
│   ├── csp.py                 # N-Queens and Room Booking CSP
│   ├── minimax.py             # Minimax and Alpha-Beta Pruning
│   └── fuzzy.py               # Fuzzy Logic rule engine
│
├── templates/
│   └── index.html             # Main application interface
│
└── static/
    ├── css/
    │   └── style.css
    │
    └── js/
        ├── main.js            # Dashboard and tab management
        ├── graphviz.js        # SVG graph visualization
        ├── navigation.js      # Navigation algorithms UI
        ├── coloring.js        # Graph Coloring UI
        ├── nqueens.js         # N-Queens UI
        ├── game.js            # Minimax game UI
        └── fuzzy.js           # Fuzzy Logic UI
⚙️ How to Run the Project
1. Clone the repository
git clone https://github.com/arafat949/AI-Campus-Navigation-Assistant.git
2. Go to the project directory
cd AI-Campus-Navigation-Assistant
3. Install the required dependencies
pip install -r requirements.txt
4. Run the application
python app.py
5. Open in your browser
http://127.0.0.1:5000
🏫 Campus Graph Model

The system represents the Green University of Bangladesh campus as a graph.

Buildings and rooms are represented as nodes.
Corridors, doors, and routes are represented as edges.
The campus-level graph connects major buildings.
Building-level graphs represent rooms and their internal connections.

The room adjacency information was created based on campus floor plans and route maps. Distance values are approximated and can easily be updated with real-world measurements in the future.

📊 Algorithm Visualization

The project does not only display the final answer.

Each algorithm also provides information about how it reached the solution, including:

Nodes explored
Visit order
Search path
Backtracking operations
Algorithm decision process
Fuzzy rules triggered

This makes the system useful for both interactive learning and AI algorithm demonstration during project presentations or viva examinations.

🔮 Future Improvements
Add real GPS-based campus navigation
Use actual distance measurements between buildings
Add real-time classroom availability
Integrate indoor maps
Add user authentication
Store booking data in a database
Add machine learning-based crowd prediction
Develop a mobile application version
🎓 Academic Purpose

This project was developed as part of the CSE316 — Artificial Intelligence course at:

Green University of Bangladesh

The main objective of this project is to demonstrate how different Artificial Intelligence algorithms can be applied to solve practical campus-related problems such as navigation, scheduling, optimization,
