import random
import streamlit as st
from algorithm.astar import find_best_route, VALID_TYPES

st.set_page_config(page_title="SafeRoute AI", page_icon="🚨", layout="wide")
META = {
    "safe": ("⬜", "#f8fafc", "Safe"),
    "crowd": ("👥", "#fef3c7", "Crowded"),
    "smoke": ("🌫️", "#cbd5e1", "Smoke"),
    "risk": ("⚠️", "#fed7aa", "High risk"),
    "fire": ("🔥", "#fecaca", "Fire"),
    "blocked": ("⬛", "#64748b", "Blocked"),
    "exit": ("🚪", "#bbf7d0", "Exit"),
}
def demo_grid():
    grid = [["safe" for _ in range(10)] for _ in range(10)]
    def put(kind, cells):
        for r, c in cells: grid[r][c] = kind
    put("exit", [(0,4),(9,8)])
    put("fire", [(5,4)])
    put("blocked", [(3,2),(3,3),(3,4),(3,6),(7,5),(7,6),(7,7),(6,8),(8,2)])
    put("smoke", [(4,5),(4,6),(5,6),(2,5),(6,3),(6,2),(1,5),(1,6),(0,5),(0,6),(2,6),(5,2),(4,1)])
    put("risk", [(4,4),(5,3),(6,4),(5,5)])
    put("crowd", [(1,4),(1,3),(8,7)])
    return grid
if "grid" not in st.session_state:
    st.session_state.grid = demo_grid()
    st.session_state.people = [{"id":1,"r":6,"c":1},{"id":2,"r":5,"c":8},{"id":3,"r":2,"c":7}]
    st.session_state.routes = None
    st.session_state.events = ["Demo building loaded."]
    st.session_state.evacuated = []
    st.session_state.trapped = []

st.markdown("""
<style>
.block-container{padding-top:1.5rem;max-width:1400px}
.hero{padding:1.4rem 1.6rem;border-radius:18px;background:linear-gradient(120deg,#111827,#7f1d1d);color:white;margin-bottom:1rem}
.hero h1{color:white;margin:0}.hero p{margin-bottom:0}
div[data-testid="stMetric"]{background:#f8fafc;padding:12px;border:1px solid #e2e8f0;border-radius:12px}
</style>
<div class="hero"><h1>🚨 SafeRoute AI</h1><p>Dynamic Fire Evacuation & Risk-Aware Route Optimization · A* Heuristic Search</p></div>
""", unsafe_allow_html=True)

grid = st.session_state.grid
people = st.session_state.people
with st.sidebar:
    st.header("Building editor")
    rr = st.number_input("Cell row", min_value=0, max_value=9, value=0)
    cc = st.number_input("Cell column", min_value=0, max_value=9, value=0)
    kind = st.selectbox("Cell type", sorted(VALID_TYPES), format_func=lambda x: META[x][2])
    if st.button("Apply cell update", use_container_width=True):
        grid[int(rr)][int(cc)] = kind
        st.session_state.routes = None
        st.session_state.events.insert(0, f"Cell ({rr}, {cc}) changed to {kind}.")
        st.rerun()
    st.divider()
    st.subheader("People")
    pr = st.number_input("New person row", 0, 9, 8)
    pc = st.number_input("New person column", 0, 9, 1)
    if st.button("Add person", use_container_width=True):
        if grid[int(pr)][int(pc)] not in ("fire","blocked","exit"):
            next_id = max([p["id"] for p in people], default=0) + 1
            people.append({"id":next_id,"r":int(pr),"c":int(pc)})
            st.session_state.routes = None
            st.rerun()
        else: st.warning("Choose a traversable cell.")
    if people:
        rid = st.selectbox("Person to remove", [p["id"] for p in people])
        if st.button("Remove person", use_container_width=True):
            st.session_state.people = [p for p in people if p["id"] != rid]
            st.session_state.routes = None
            st.rerun()
    if st.button("Reset demo", use_container_width=True):
        for key in ("grid","people","routes","events","evacuated","trapped"): st.session_state.pop(key, None)
        st.rerun()

flat = [x for row in grid for x in row]
a,b,c,d = st.columns(4)
a.metric("People in building", len(people))
b.metric("Active fire cells", flat.count("fire"))
c.metric("Emergency exits", flat.count("exit"))
d.metric("Smoke / high-risk", flat.count("smoke") + flat.count("risk"))
st.caption("Legend: ⬜ Safe · 👥 Crowded · 🌫️ Smoke · ⚠️ High risk · 🔥 Fire · ⬛ Blocked · 🚪 Exit · 🧍 Person · 🟩 Route")

routes = st.session_state.routes
path_cells = set()
if routes:
    for route in routes:
        if route.get("found"): path_cells.update(tuple(p) for p in route["path"])
people_map = {(p["r"],p["c"]):p["id"] for p in people}
html_rows = []
for r, row in enumerate(grid):
    cells = []
    for c, cell in enumerate(row):
        emoji, color, label = META[cell]
        if (r,c) in people_map:
            emoji, color = f"🧍{people_map[(r,c)]}", "#bfdbfe"
        elif (r,c) in path_cells and cell != "exit":
            color = "#86efac"
        cells.append(f'<td title="{label} ({r},{c})" style="background:{color};border:1px solid #cbd5e1;border-radius:5px;text-align:center;min-width:36px;height:36px;font-size:18px">{emoji}</td>')
    html_rows.append("<tr>" + "".join(cells) + "</tr>")
grid_html = '<div style="overflow-x:auto"><table style="border-collapse:separate;border-spacing:3px;margin:auto">' + "".join(html_rows) + "</table></div>"

left, right = st.columns([1.25,1])
with left:
    st.subheader("Interactive building grid · 10 × 10")
    st.markdown(grid_html, unsafe_allow_html=True)
    st.caption("Green cells show the recommended route. Edit hazards and exits from the sidebar.")
with right:
    st.subheader("Route planner")
    if st.button("🧭 Find safe routes", type="primary", use_container_width=True):
        exits = [(r,c) for r,row in enumerate(grid) for c,cell in enumerate(row) if cell == "exit"]
        st.session_state.routes = [dict(find_best_route(grid,(p["r"],p["c"]),exits),person_id=p["id"]) for p in people]
        st.session_state.events.insert(0, "Routes recalculated using A*.")
        st.rerun()
    if st.button("🔥 Advance fire simulation", use_container_width=True):
        new_grid = [row[:] for row in grid]
        for r,row in enumerate(grid):
            for c,cell in enumerate(row):
                if cell != "fire": continue
                for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)):
                    nr,nc=r+dr,c+dc
                    if 0 <= nr < 10 and 0 <= nc < 10 and new_grid[nr][nc] not in ("fire","blocked","exit") and random.random() < .35:
                        new_grid[nr][nc] = "fire"
        for p in people:
            if new_grid[p["r"]][p["c"]] == "fire":
                st.session_state.trapped.append(p["id"])
        st.session_state.grid = new_grid
        st.session_state.routes = None
        st.session_state.events.insert(0, "Fire spread simulated; routes need recalculation.")
        st.rerun()
    if routes:
        for route in routes:
            with st.container(border=True):
                st.markdown(f"**Person {route['person_id']}**")
                if route.get("found"):
                    st.success(f"Best exit: row {route['exit'][0]}, column {route['exit'][1]}")
                    m1,m2,m3=st.columns(3)
                    m1.metric("Steps",route["distance"])
                    m2.metric("Movement cost",route["cost"])
                    m3.metric("Risk score",route["risk"])
                    with st.expander("Compare exits"):
                        for alt in route["alternatives"]:
                            st.write(alt)
                else: st.error("No safe route found. Try editing hazards or adding an exit.")
    else:
        st.info("Click Find safe routes to calculate a route for each person.")

st.divider()
x,y=st.columns(2)
with x:
    st.subheader("A* heuristic search")
    st.latex(r"f(n) = g(n) + h(n)")
    st.markdown("**g(n):** accumulated movement cost.  \n**h(n):** Manhattan-distance estimate.  \n**Heuristic:** |r₁ − r₂| + |c₁ − c₂|.  \n**Costs:** safe 1 · crowded 3 · smoke 5 · high-risk 10 · fire/blocked impassable.")
with y:
    st.subheader("Simulation event log")
    if st.session_state.evacuated: st.success("Evacuated: " + ", ".join(map(str,sorted(set(st.session_state.evacuated)))))
    if st.session_state.trapped: st.warning("Affected by fire: " + ", ".join(map(str,sorted(set(st.session_state.trapped)))))
    for event in st.session_state.events[:8]: st.write("• " + event)
st.warning("Educational simulation only. Fire spread and hazard costs are simplified; do not use this app for real emergency decisions.")
