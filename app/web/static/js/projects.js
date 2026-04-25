async function loadProjects() {
  const rows = await apiGet("/api/projects");
  const tbody = document.getElementById("projectsBody");
  tbody.innerHTML = rows.map(item => `
    <tr>
      <td>${item.id}</td>
      <td><strong>${safe(item.name)}</strong><br><span class="muted">${safe(item.description, "Sin descripción")}</span></td>
      <td class="path-cell">${safe(item.base_url)}</td>
      <td>${safe(item.default_browser)}</td>
      <td>${statusBadge(item.status)}</td>
      <td class="row-actions project-actions"><a class="btn primary" href="/ui/projects/${item.id}">Ver detalle</a><button class="btn secondary" onclick="deleteProject(${item.id})">Eliminar</button></td>
    </tr>`).join("") || `<tr><td colspan="6" class="muted">No hay proyectos registrados.</td></tr>`;
}
async function deleteProject(id) {
  if (!confirm("¿Eliminar este proyecto?")) return;
  try { await apiDelete(`/api/projects/${id}`); toast("Proyecto eliminado"); await loadProjects(); }
  catch (error) { toast("No se pudo eliminar el proyecto"); console.error(error); }
}
function setupModal() {
  const modal = document.getElementById("projectModal");
  document.getElementById("openProjectModal")?.addEventListener("click", () => modal.classList.remove("hidden"));
  document.getElementById("closeProjectModal")?.addEventListener("click", () => modal.classList.add("hidden"));
}
async function saveProject(event) {
  event.preventDefault();
  const form = new FormData(event.target);
  try {
    await apiPost("/api/projects", { name: form.get("name"), description: form.get("description"), base_url: form.get("base_url"), default_browser: form.get("default_browser"), status: form.get("status") });
    document.getElementById("projectModal").classList.add("hidden"); event.target.reset(); toast("Proyecto creado correctamente"); await loadProjects();
  } catch (error) { toast("No se pudo crear el proyecto"); console.error(error); }
}
document.addEventListener("DOMContentLoaded", async () => { setupModal(); document.getElementById("projectForm")?.addEventListener("submit", saveProject); await loadProjects(); if (window.applyLanguage) window.applyLanguage(); });
