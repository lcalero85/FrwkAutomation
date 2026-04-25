function getProjectIdFromPath() { const parts = window.location.pathname.split("/").filter(Boolean); return parts[parts.length - 1]; }
function emptyRow(cols, text) { return `<tr><td colspan="${cols}" class="muted">${text}</td></tr>`; }
async function loadProjectDetail() {
  const data = await apiGet(`/api/projects/${getProjectIdFromPath()}/details`);
  const project = data.project;
  document.getElementById("projectName").textContent = project.name;
  document.getElementById("projectDescription").textContent = project.description || "Sin descripción registrada.";
  document.getElementById("projectMeta").innerHTML = `<span>${statusBadge(project.status)}</span><span>URL base: ${safe(project.base_url)}</span><span>Navegador: ${safe(project.default_browser)}</span>`;
  document.getElementById("summarySuites").textContent = data.summary.total_suites;
  document.getElementById("summaryCases").textContent = data.summary.total_test_cases;
  document.getElementById("summaryRecorded").textContent = data.summary.total_recorded_cases;
  document.getElementById("summaryExecutions").textContent = data.summary.total_executions;
  document.getElementById("suitesBody").innerHTML = data.suites.map(item => `<tr><td>${item.id}</td><td><strong>${safe(item.name)}</strong><br><span class="muted">${safe(item.description, "Sin descripción")}</span></td><td>${safe(item.priority)}</td><td>${statusBadge(item.status)}</td></tr>`).join("") || emptyRow(4, "Este proyecto aún no tiene suites asociadas.");
  document.getElementById("recordedBody").innerHTML = data.recorded_cases.map(item => `<tr><td>${item.id}</td><td><strong>${safe(item.name)}</strong><br><span class="muted">${safe(item.base_url)}</span></td><td>${safe(item.browser)}</td><td>${statusBadge(item.status)}</td></tr>`).join("") || emptyRow(4, "Este proyecto aún no tiene casos grabados.");
  document.getElementById("executionsBody").innerHTML = data.executions.map(item => `<tr><td>${item.id}</td><td>${safe(item.test_name)}</td><td>${safe(item.browser)}</td><td>${safe(item.environment)}</td><td>${statusBadge(item.status)}</td><td>${safe(item.success_percentage, 0)}%</td><td><a class="btn secondary" href="/ui/executions/${item.id}">Visor</a></td></tr>`).join("") || emptyRow(7, "Este proyecto aún no tiene ejecuciones registradas.");
}
document.addEventListener("DOMContentLoaded", () => loadProjectDetail().catch(error => { toast("No se pudo cargar el detalle del proyecto"); console.error(error); }));
