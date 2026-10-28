# AI-Based Dynamic Fire Evacuation and Safe Route Optimization Using A* Heuristic Search

A Flask web application that models a building as a weighted grid and uses A* heuristic search to recommend low-cost evacuation routes based on distance and danger.

## Features
- Interactive 10×10 building grid with people, exits, fire, smoke, crowded cells, high-risk cells, and blocked paths.
- A* search implemented from scratch using a priority queue and Manhattan-distance heuristic.
- Risk-aware costs: safe = 1, crowded = 3, smoke = 5, high-risk = 10; fire and blocked cells are impassable.
- Multiple people and exits; route alternatives and cost comparisons.
- Fire-spread simulation, one-cell-per-tick movement, route recalculation, event log, route animation, and search replay.
- Dashboard showing evacuation status and overall risk level.

## Technology stack
Python 3, Flask, HTML, CSS, JavaScript, and JSON. No external pathfinding library or external API is required.

## Run locally
```bash
python -m venv venv
# macOS/Linux: source venv/bin/activate
# Windows: venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```
Then open http://127.0.0.1:5000 and click **Find Safe Routes**.

## A* cost model
`f(n) = g(n) + h(n)`

- `g(n)`: accumulated movement cost from the person's start cell.
- `h(n)`: Manhattan distance to the exit, `|r1-r2| + |c1-c2|`.
- `f(n)`: estimated total route cost through the current cell.

A* evaluates reachable exits and selects the route with the lowest total movement cost. The heuristic is admissible for four-directional movement because each traversable cell costs at least 1.

## Project structure
```text
fire-evacuation-aisc/
├── app.py
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

## API endpoints
- `GET /` — render the dashboard.
- `GET /api/sample` — return the sample building.
- `POST /api/status` — return building statistics.
- `POST /api/route` — calculate routes for each person.
- `POST /api/step` — advance fire simulation, move people, and recalculate routes.

## Limitations
This is an educational simulation, not a real emergency response tool. Fire spread is randomized and simplified; the model uses a single grid, does not model realistic crowd interactions, and plans each person's route independently.
