# AI-Based Dynamic Fire Evacuation and Safe Route Optimization Using A* Heuristic Search

An interactive **Streamlit** dashboard that models a building as a weighted grid and uses A* heuristic search to recommend routes that account for distance and danger.

## Features
- Interactive 10×10 building grid with editable cells.
- Multiple people and emergency exits.
- Fire, smoke, crowded cells, high-risk zones, and blocked paths.
- A* implemented from scratch using a priority queue and Manhattan-distance heuristic.
- Risk-aware costs: safe = 1, crowded = 3, smoke = 5, high-risk = 10; fire and blocked cells are impassable.
- Route summaries with distance, total movement cost, risk score, and reachable-exit comparisons.
- Fire-spread simulation, dashboard metrics, and event log.

## Run locally
Use Python 3.10–3.13 for good package compatibility.

```bash
git clone https://github.com/tannishka07/fire-evacuation-aisc.git
cd fire-evacuation-aisc
python3 -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows PowerShell: .\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Streamlit opens the app in your browser, usually at http://localhost:8501.

## Deploy free with Streamlit Community Cloud
1. Visit https://share.streamlit.io/ and sign in with GitHub.
2. Choose **Create app** and select repository `tannishka07/fire-evacuation-aisc`.
3. Choose branch `main`.
4. Set **Main file path** to `streamlit_app.py`.
5. Click **Deploy**. Streamlit installs packages from `requirements.txt`.

## A* cost model
`f(n) = g(n) + h(n)`

- `g(n)`: accumulated movement cost from the person's start cell.
- `h(n)`: Manhattan distance to an exit, `|r1-r2| + |c1-c2|`.
- `f(n)`: estimated total route cost through the current cell.

The planner evaluates reachable exits and selects the route with the lowest movement cost. No external pathfinding library or external API is required.

## Project structure
```text
fire-evacuation-aisc/
├── streamlit_app.py
├── requirements.txt
├── README.md
└── algorithm/
    ├── __init__.py
    └── astar.py
```

## Limitations
This is an educational simulation, not a real emergency response tool. Fire spread is randomized and simplified, crowd interactions are not physically modelled, and each person's route is planned independently.
