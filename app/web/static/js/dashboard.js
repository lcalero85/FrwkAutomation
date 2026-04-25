let resultChart;

async function loadMetrics() {
  const data = await apiGet("/api/dashboard/metrics");
  document.getElementById("metricProjects").textContent = data.total_projects;
  document.getElementById("metricSuites").textContent = data.total_suites;
  document.getElementById("metricCases").textContent = data.total_test_cases;
  document.getElementById("metricSuccess").textContent = `${data.success_percentage}%`;

  const ctx = document.getElementById("resultChart");
  if (ctx && window.Chart) {
    if (resultChart) resultChart.destroy();
    resultChart = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Passed", "Failed"],
        datasets: [{ data: [data.passed_executions, data.failed_executions] }]
      },
      options: { plugins: { legend: { position: "bottom" } } }
    });
  }
}

async function loadLatestExecutions() {
  const rows = await apiGet("/api/executions");
  const tbody = document.getElementById("latestExecutionsBody");
  tbody.innerHTML = rows.slice(0, 6).map(item => `
    <tr>
      <td>${item.id}</td>
      <td>${safe(item.test_name)}</td>
      <td>${safe(item.browser)}</td>
      <td>${safe(item.environment)}</td>
      <td>${statusBadge(item.status)}</td>
      <td>${seconds(item.duration_seconds)}</td>
    </tr>`).join("") || `<tr><td colspan="6" class="muted">Aún no hay ejecuciones registradas.</td></tr>`;
}

async function runDemoFromForm(event) {
  event.preventDefault();
  const form = new FormData(event.target);
  const status = document.getElementById("runStatus");
  status.classList.remove("hidden");
  status.textContent = "Ejecutando prueba demo. Mantén esta ventana abierta...";
  try {
    const result = await apiPost("/api/executions/run-demo", {
      browser: form.get("browser"),
      environment: form.get("environment"),
      report: form.get("report"),
      test: "login_demo",
      headless: form.get("headless") === "on",
    });
    status.textContent = `Ejecución finalizada: ${result.status}. Duración: ${seconds(result.duration_seconds)}.`;
    toast("Ejecución demo finalizada correctamente");
    await loadMetrics();
    await loadLatestExecutions();
  } catch (error) {
    status.textContent = "Error al ejecutar la demo. Revisa la consola del servidor.";
    toast("Error al ejecutar la demo");
    console.error(error);
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  document.getElementById("runDemoForm")?.addEventListener("submit", runDemoFromForm);
  await loadMetrics();
  await loadLatestExecutions();
});
