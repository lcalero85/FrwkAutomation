let executionRows = [];

async function loadExecutions() {
  executionRows = await apiGet("/api/executions");
  const tbody = document.getElementById("executionsBody");
  tbody.innerHTML = executionRows.map(item => `
    <tr>
      <td>${item.id}</td>
      <td>${safe(item.project_name)}</td>
      <td><strong>${safe(item.test_name)}</strong></td>
      <td>${safe(item.browser)}</td>
      <td>${statusBadge(item.status)}</td>
      <td>${safe(item.success_percentage)}%</td>
      <td>${seconds(item.duration_seconds)}</td>
      <td class="table-actions">
        <a class="btn primary" href="/ui/executions/${item.id}">Visor avanzado</a>
        <button class="btn secondary" onclick="loadSteps(${item.id})">Pasos rápidos</button>
      </td>
    </tr>`).join("") || `<tr><td colspan="8" class="muted">Aún no hay ejecuciones registradas.</td></tr>`;

  fillCompareSelectors();
}

function fillCompareSelectors() {
  const left = document.getElementById("compareLeft");
  const right = document.getElementById("compareRight");
  if (!left || !right) return;
  const options = executionRows.map(item => `<option value="${item.id}">#${item.id} · ${safe(item.test_name)} · ${safe(item.status)} · ${safe(item.success_percentage)}%</option>`).join("");
  left.innerHTML = options;
  right.innerHTML = options;
  document.getElementById("comparePanel")?.classList.toggle("hidden", executionRows.length < 2);
  if (executionRows.length >= 2) {
    left.value = executionRows[1].id;
    right.value = executionRows[0].id;
  }
}

async function loadSteps(id) {
  const steps = await apiGet(`/api/executions/${id}/steps`);
  document.getElementById("stepsPanel").classList.remove("hidden");
  document.getElementById("stepsSubtitle").textContent = `Ejecución #${id}`;
  document.getElementById("stepsBody").innerHTML = steps.map(step => `
    <tr>
      <td>${step.step_order}</td>
      <td>${safe(step.name)}</td>
      <td>${safe(step.action)}</td>
      <td class="path-cell">${safe(step.selector)}</td>
      <td>${statusBadge(step.status)}</td>
      <td>${seconds(step.duration_seconds)}</td>
      <td>${safe(step.message)}</td>
    </tr>`).join("") || `<tr><td colspan="7" class="muted">Sin pasos registrados.</td></tr>`;
}

async function compareExecutions() {
  const left = document.getElementById("compareLeft")?.value;
  const right = document.getElementById("compareRight")?.value;
  if (!left || !right || left === right) {
    toast("Selecciona dos ejecuciones diferentes.");
    return;
  }
  const data = await apiGet(`/api/executions/compare?left_id=${left}&right_id=${right}`);
  const result = document.getElementById("compareResult");
  result.classList.remove("hidden");
  result.innerHTML = `
    <div class="comparison-grid">
      <div><span>Éxito</span><strong>${data.delta.success_percentage > 0 ? "+" : ""}${data.delta.success_percentage}%</strong></div>
      <div><span>Duración</span><strong>${data.delta.duration_seconds > 0 ? "+" : ""}${data.delta.duration_seconds.toFixed(2)} s</strong></div>
      <div><span>Pasos fallidos</span><strong>${data.delta.failed_steps > 0 ? "+" : ""}${data.delta.failed_steps}</strong></div>
      <div><span>Pasos exitosos</span><strong>${data.delta.passed_steps > 0 ? "+" : ""}${data.delta.passed_steps}</strong></div>
    </div>
    <p class="muted">Base: #${data.left.id} · Comparada: #${data.right.id}</p>`;
}

async function runQuickDemo() {
  toast("Ejecutando demo rápida...");
  try {
    await apiPost("/api/executions/run-demo", { browser: "chrome", headless: false, environment: "demo", test: "login_demo", report: "html,excel,pdf" });
    toast("Demo rápida finalizada");
    await loadExecutions();
  } catch (error) {
    toast("No se pudo ejecutar la demo rápida");
    console.error(error);
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  document.getElementById("runDemoQuick")?.addEventListener("click", runQuickDemo);
  document.getElementById("compareBtn")?.addEventListener("click", compareExecutions);
  await loadExecutions();
});
