const $ = (id) => document.getElementById(id);
let grid = [], people = [], routes = [], stats = {}, tool = "person", focusId = null;
let exitNames = {}, simTimer = null, tick = 0, evacuated = 0, trapped = 0;
let replayTimer = null;

const labels = {safe:"", crowd:"👥", smoke:"💨", risk:"⚠", fire:"🔥", blocked:"", exit:"🚪"};

async function post(url, body) {
  const response = await fetch(url, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}
function msg(text) { $("message").textContent = text; }
function log(text) {
  const li = document.createElement("li"); li.textContent = text; $("log").prepend(li);
  while ($("log").children.length > 35) $("log").lastElementChild.remove();
}
function personAt(r,c) { return people.find(p => p.r === r && p.c === c); }

function renderGrid() {
  const root = $("grid");
  root.style.gridTemplateColumns = \`repeat(\${grid[0]?.length || 10}, minmax(0, 1fr))\`;
  root.replaceChildren();
  const paths = new Set();
  routes.forEach(route => { if (route.found) route.path.forEach(([r,c]) => paths.add(\`\${r},\${c}\`)); });
  grid.forEach((row,r) => row.forEach((kind,c) => {
    const cell = document.createElement("button"); cell.type = "button";
    cell.className = \`cell t-\${kind}\`;
    const p = personAt(r,c);
    if (paths.has(\`\${r},\${c}\`)) cell.classList.add("on-route");
    cell.textContent = p ? \`👤\${p.id}\` : (labels[kind] || "");
    cell.title = \`Row \${r}, Column \${c}: \${kind}\`;
    cell.addEventListener("click", () => editCell(r,c)); root.append(cell);
  }));
}
function renderPanels() {
  $("sPeople").textContent = people.length;
  $("sFire").textContent = grid.flat().filter(x => x === "fire").length;
  $("sExits").textContent = grid.flat().filter(x => x === "exit").length;
  $("sBlocked").textContent = grid.flat().filter(x => x === "blocked").length;
  $("sEvac").textContent = evacuated; $("sTrap").textContent = trapped;
  $("sRisk").textContent = stats.risk_level || "LOW";
  $("sRisk").className = \`badge \${(stats.risk_level || "LOW").toLowerCase()}\`;
  $("routeList").replaceChildren();
  routes.forEach(route => {
    const button = document.createElement("button");
    button.className = "route-item" + (route.person_id === focusId ? " selected" : "");
    button.textContent = route.found ? \`Person \${route.person_id} → Exit \${route.exit_label || "?"} | cost \${route.cost} | \${route.distance} steps\` : \`Person \${route.person_id} — no safe route\`;
    button.addEventListener("click", () => { focusId = route.person_id; renderGrid(); renderPanels(); });
    $("routeList").append(button);
  });
  const focused = routes.find(r => r.person_id === focusId);
  $("routeInfo").replaceChildren();
  if (focused) {
    [["Route cost", focused.found ? focused.cost : "—"],["Distance", focused.found ? focused.distance : "—"],["Risk score", focused.found ? focused.risk : "—"]].forEach(([k,v]) => {
      const wrap = document.createElement("div"), dt = document.createElement("dt"), dd = document.createElement("dd");
      dt.textContent = k; dd.textContent = v; wrap.append(dt,dd); $("routeInfo").append(wrap);
    });
    $("algoInfo").textContent = \`Nodes expanded: \${focused.explored?.length || 0}\`;
  } else $("algoInfo").textContent = "Nodes expanded: –";
  const table = $("exitTable"); table.replaceChildren();
  const header = document.createElement("tr");
  ["Exit","Reachable","Cost","Distance"].forEach(t => { const th=document.createElement("th"); th.textContent=t; header.append(th); });
  table.append(header);
  (focused?.alternatives || []).forEach(alt => {
    const tr=document.createElement("tr");
    [alt.label || "Exit", alt.reachable ? "Yes" : "No", alt.reachable ? alt.cost : "—", alt.reachable ? alt.distance : "—"].forEach(v => { const td=document.createElement("td"); td.textContent=v; tr.append(td); });
    table.append(tr);
  });
}
function render() { renderGrid(); renderPanels(); }
function clearRoutes() { routes = []; focusId = null; }

async function refreshStatus() {
  try { const data = await post("/api/status", {grid, people}); stats = data.stats; renderPanels(); }
  catch (e) { msg("Status update failed: " + e.message); }
}
function editCell(r,c) {
  if (tool === "person") {
    const existing = personAt(r,c);
    if (existing) people = people.filter(p => p.id !== existing.id);
    else if (!["fire","blocked","exit"].includes(grid[r][c])) {
      const id = Math.max(0, ...people.map(p => p.id)) + 1; people.push({id, r, c});
    }
  } else if (tool === "erase") {
    grid[r][c] = "safe"; people = people.filter(p => p.r !== r || p.c !== c); delete exitNames[\`\${r},\${c}\`];
  } else {
    const old = grid[r][c], next = old === tool ? "safe" : tool;
    if (["fire","blocked","exit"].includes(next)) people = people.filter(p => p.r !== r || p.c !== c);
    grid[r][c] = next;
    if (next === "exit" && old !== "exit") {
      const used = Object.values(exitNames);
      exitNames[\`\${r},\${c}\`] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").find(x => !used.includes(x)) || "?";
    } else if (old === "exit" && next !== "exit") delete exitNames[\`\${r},\${c}\`];
  }
  clearRoutes(); render(); refreshStatus();
}
async function findRoutes() {
  if (!people.length) return msg("Add at least one person first.");
  if (!grid.flat().includes("exit")) return msg("Add at least one emergency exit first.");
  try {
    const res = await post("/api/route", {grid, people, exit_names:exitNames});
    routes = res.routes; stats = res.stats; focusId = (routes.find(r => r.found) || routes[0]).person_id;
    msg(\`A* found safe routes for \${routes.filter(r => r.found).length} of \${routes.length} people.\`);
    render();
  } catch (e) { msg("Could not calculate routes: " + e.message); }
}
function stopSim(text) {
  clearInterval(simTimer); simTimer = null; $("btnSim").textContent = "Start Fire Simulation"; $("btnSim").classList.remove("running");
  if (text) { msg(text); log(text); }
}
async function simStep() {
  if (!simTimer) return;
  try {
    const res = await post("/api/step", {grid, people, exit_names:exitNames});
    grid = res.grid; people = res.people; routes = res.routes; stats = res.stats;
    evacuated += res.evacuated.length; trapped += res.trapped.length; tick++;
    log(\`Tick \${tick}: fire spread to \${res.changed.filter(c => c[2] === "fire").length} cell(s).\`);
    res.events.forEach(log);
    focusId = (routes.find(r => r.person_id === focusId && r.found) || routes.find(r => r.found) || {}).person_id || null;
    render();
    if (res.done) stopSim(\`Simulation finished: \${evacuated} evacuated, \${trapped} trapped.\`);
  } catch (e) { stopSim("Simulation stopped: " + e.message); }
}
function toggleSim() {
  if (simTimer) return stopSim("Simulation stopped.");
  if (!grid.flat().includes("fire")) return msg("Place at least one fire before starting the simulation.");
  if (!people.length || !grid.flat().includes("exit")) return msg("Add at least one person and one exit first.");
  clearRoutes(); evacuated = 0; trapped = 0; tick = 0;
  $("btnSim").textContent = "Stop Simulation"; $("btnSim").classList.add("running");
  msg("Simulation running: fire spreads and routes are recalculated.");
  simTimer = setInterval(simStep, 1200); simStep();
}
function replaySearch() {
  clearInterval(replayTimer);
  const route = routes.find(r => r.person_id === focusId);
  if (!route?.found || !route.explored?.length) return msg("Find safe routes first, then replay the search.");
  let i = 0;
  replayTimer = setInterval(() => {
    const n = route.explored[i++];
    $("inspector").textContent = \`Expand (\${n.r},\${n.c}) g=\${n.g} + h=\${n.h} = f=\${n.f}\`;
    if (i >= route.explored.length) { clearInterval(replayTimer); $("inspector").textContent += \` → exit reached, route cost \${route.cost}\`; }
  }, 120);
}
function setState(s) {
  stopSim(); grid = s.grid; people = s.people || []; exitNames = {...(s.exit_names || {})};
  clearRoutes(); evacuated = 0; trapped = 0; tick = 0; stats = {};
  $("log").replaceChildren(); render(); refreshStatus();
}
async function loadDemo() {
  try { setState(await (await fetch("/api/sample")).json()); msg("Demo building loaded. Press Find Safe Routes to run A*."); }
  catch (e) { msg("Could not load demo building: " + e.message); }
}
function resetBuilding() {
  const n = grid.length || 10;
  setState({grid:Array.from({length:n}, () => Array(n).fill("safe")), people:[], exit_names:{}});
  msg("Building reset. Choose a tool and draw your own layout.");
}

document.querySelectorAll(".tool").forEach(button => button.addEventListener("click", () => {
  tool = button.dataset.tool;
  document.querySelectorAll(".tool").forEach(b => b.classList.toggle("active", b === button));
}));
$("btnRoute").addEventListener("click", findRoutes);
$("btnSim").addEventListener("click", toggleSim);
$("btnDemo").addEventListener("click", loadDemo);
$("btnReset").addEventListener("click", resetBuilding);
$("btnReplay").addEventListener("click", replaySearch);
loadDemo();
