# AI-Based Dynamic Fire Evacuation and Safe Route Optimization Using A* Heuristic Search

An educational evacuation-planning project that represents a building as a weighted grid and uses **A* heuristic search** to recommend routes that account for movement distance and danger.

## Features

- Interactive building grid with multiple people and emergency exits.
- Editable safe, crowded, smoke, high-risk, fire, and blocked cells.
- A* pathfinding implemented from scratch with a priority queue and Manhattan-distance heuristic.
- Risk-aware costs: safe = 1, crowded = 3, smoke = 5, high-risk = 10; fire and blocked cells are impassable.
- Route summaries, dashboard statistics, and comparisons between reachable exits.
- Fire-spread simulation, route recalculation, and event log.

## Technology stack

Python, Flask, Streamlit, HTML, CSS, JavaScript, and JSON. The repository contains a Flask web application and a Streamlit version.

## Run the Flask web app

```bash
python3 -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows PowerShell: .\\venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Run the Streamlit app

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Streamlit usually opens at http://localhost:8501.

## A* cost model

`f(n) = g(n) + h(n)`

- **g(n):** accumulated movement cost from the person's starting cell.
- **h(n):** Manhattan-distance estimate to an exit: `|r1-r2| + |c1-c2|`.
- **f(n):** estimated total route cost through the current cell.

A* evaluates reachable exits and chooses the route with the lowest total movement cost. With four-directional movement and a minimum traversable-cell cost of 1, Manhattan distance is an admissible heuristic for this model.

## Project structure

```text
fire-evacuation-aisc/
├── app.py
├── streamlit_app.py
├── requirements.txt
├── algorithm/
│   ├── __init__.py
│   └── astar.py
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/script.js
```

## Limitations

This is an educational simulation, not a real emergency response tool. Fire spread is simplified, the grid does not model multi-floor buildings or realistic crowd movement, and individual routes may overlap.
