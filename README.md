# 🎓 AI Campus Navigation Assistant

### CSE316 — Artificial Intelligence Project

**Green University of Bangladesh**

<p align="center">
  <b>An AI-powered smart campus navigation and utility system built with Python and Flask.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3-blue?logo=python" />
  <img src="https://img.shields.io/badge/Flask-Web%20App-black?logo=flask" />
  <img src="https://img.shields.io/badge/AI-Algorithms-purple" />
  <img src="https://img.shields.io/badge/Course-CSE316-success" />
</p>

---

## 🚀 About the Project

**AI Campus Navigation Assistant** is an interactive web application designed to demonstrate multiple Artificial Intelligence algorithms using a graph-based model of the Green University of Bangladesh campus.

The system can find routes between buildings and rooms, allocate rooms without conflicts, solve the N-Queens problem, play Tic-Tac-Toe against an AI opponent, and estimate campus congestion.

---

## ✨ Key Features

🗺️ **Smart Navigation** — Find routes using BFS, DFS, and IDDFS
🎨 **Graph Coloring** — Conflict-free room and time-slot allocation
🧩 **Constraint Satisfaction** — N-Queens and classroom booking
🎮 **AI Tic-Tac-Toe** — Minimax with Alpha-Beta Pruning
🧠 **Fuzzy Logic** — Estimate classroom and corridor congestion
📊 **Visualization** — Interactive algorithm results and graph visualization

---

## 🤖 AI Algorithms

| Algorithm                | Application                                |
| ------------------------ | ------------------------------------------ |
| **BFS**                  | Finds the shortest route with minimum hops |
| **DFS**                  | Explores alternative routes                |
| **IDDFS**                | Iterative deepening search                 |
| **Graph Coloring**       | Conflict-free exam/room scheduling         |
| **CSP**                  | N-Queens and classroom allocation          |
| **Minimax + Alpha-Beta** | Intelligent Tic-Tac-Toe opponent           |
| **Fuzzy Logic**          | Campus congestion estimation               |

---

## 🛠️ Tech Stack

```text
Backend     → Python + Flask
Frontend    → HTML + CSS + JavaScript
Visualization → SVG Graph
Data        → JSON
```

---

## 📂 Project Structure

```text
AI-Campus-Navigation-Assistant/
│
├── 📄 app.py
├── 📄 requirements.txt
│
├── 📁 algorithms/
│   ├── pathfinding.py
│   ├── graph_coloring.py
│   ├── csp.py
│   ├── minimax.py
│   └── fuzzy.py
│
├── 📁 data/
│   └── campus_graph_data.json
│
├── 📁 templates/
│   └── index.html
│
└── 📁 static/
    ├── css/
    └── js/
```

---

## ⚙️ Installation & Usage

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/arafat949/AI-Campus-Navigation-Assistant.git
```

### 2️⃣ Go to the Project Folder

```bash
cd AI-Campus-Navigation-Assistant
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Application

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

## 🏫 Campus Graph

The campus is represented as a graph where:

* 🏢 Buildings and rooms are **nodes**
* 🚶 Corridors and routes are **edges**
* 📏 Distances are approximated using a unit-based scale
* 🔄 Real measurements can be added later without changing the algorithms

The graph includes the **Main Gate, Admin Building, and Buildings B, E, F, G, H, J, K, and L**.

---

## 🎯 Project Objective

The main objective of this project is to demonstrate how different Artificial Intelligence algorithms can solve practical campus-related problems such as:

> Navigation • Scheduling • Optimization • Decision Making • Congestion Estimation

---

## 🔮 Future Improvements

* 📍 Real GPS-based navigation
* 🗺️ Indoor campus maps
* 🤖 Machine Learning-based crowd prediction
* 🏫 Real-time classroom availability
* 📱 Mobile application version

---

## 👨‍💻 Developer

**Md. Arafat Miah**
CSE Student
**Green University of Bangladesh**

---

<p align="center">
  ⭐ If you like this project, consider giving it a star!
</p>
