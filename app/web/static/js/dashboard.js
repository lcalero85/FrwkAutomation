let resultChart;
let browserChart;
let trendChart;

function countBy(rows, key) {
  return rows.reduce((acc, item) => {
    const value = item[key] || "UNKNOWN";
    acc[value] = (acc[value] || 0) + 1;
    return acc;
  }, {});
}

function renderChart(canvasId, chartRef, config) {
  const ctx = document.getElementById(canvasId);
  if (!ctx || !window.Chart) return chartRef;
  if (chartRef) chartRef.destroy();
  return new Chart(ctx, config);
}

async function loadMetrics() {
  const data = await apiGet("/api/dashboard/metrics");
  document.getElementById("metricProjects").textContent = data.total_projects;
  document.getElementById("metricActiveProjects").textContent = `Activos: ${data.active_projects || 0}`;
  document.getElementById("metricSuites").textContent = data.total_suites;
  document.getElementById("metricCases").textContent = data.total_test_cases;
  document.getElementById("metricRecordedCases").textContent = `Grabados: ${data.total_recorded_cases || 0}`;
  document.getElementById("metricSuccess").textContent = `${data.success_percentage}%`;
  document.getElementById("metricExecutions").textContent = data.total_executions;
  document.getElementById("metricReports").textContent = data.total_reports || 0;
  document.getElementById("metricJobs").textContent = data.total_scheduler_jobs || 0;
  document.getElementById("metricFailed").textContent = data.failed_executions || 0;
  document.getElementById("metricAvgDuration").textContent = `Promedio: ${seconds(data.avg_duration_seconds || 0)}`;
  document.getElementById("metricLastStatus").textContent = `Última ejecución: ${data.last_execution_status || "-"}`;

  resultChart = renderChart("resultChart", resultChart, {
    type: "doughnut",
    data: { labels: ["Passed", "Failed", "Skipped"], datasets: [{ data: [data.passed_executions, data.failed_executions, data.skipped_executions || 0] }] },
    options: { responsive: true, plugins: { legend: { position: "bottom" } } }
  });
}

async function loadLatestReport() {
  try {
    const reports = await apiGet("/api/reports");
    const btn = document.getElementById("latestReportBtn");
    if (!btn) return;
    if (reports.length > 0) {
      btn.href = `/api/reports/${reports[0].id}/view/html`;
      btn.target = "_blank";
      btn.textContent = `Ver último reporte #${reports[0].id}`;
    } else {
      btn.href = "/ui/reports";
      btn.target = "";
      btn.textContent = "Ver reportes";
    }
  } catch (error) {
    console.warn("No se pudo cargar el último reporte", error);
  }
}

async function loadLatestExecutions() {
  const rows = await apiGet("/api/executions");
  const tbody = document.getElementById("latestExecutionsBody");
  tbody.innerHTML = rows.slice(0, 8).map(item => `
    <tr>
      <td>${item.id}</td>
      <td>${safe(item.test_name)}</td>
      <td>${safe(item.browser)}</td>
      <td>${safe(item.environment)}</td>
      <td>${statusBadge(item.status)}</td>
      <td>${safe(item.success_percentage, 0)}%</td>
      <td>${seconds(item.duration_seconds)}</td>
      <td><a class="btn secondary" href="/ui/executions/${item.id}">Ver</a></td>
    </tr>`).join("") || `<tr><td colspan="8" class="muted">Aún no hay ejecuciones registradas.</td></tr>`;

  const browserCounts = countBy(rows, "browser");
  browserChart = renderChart("browserChart", browserChart, {
    type: "bar",
    data: { labels: Object.keys(browserCounts), datasets: [{ label: "Ejecuciones", data: Object.values(browserCounts) }] },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }
  });

  const recent = rows.slice(0, 10).reverse();
  trendChart = renderChart("trendChart", trendChart, {
    type: "line",
    data: { labels: recent.map(item => `#${item.id}`), datasets: [{ label: "% éxito", data: recent.map(item => Number(item.success_percentage || 0)), tension: .35 }] },
    options: { responsive: true, scales: { y: { beginAtZero: true, max: 100 } } }
  });
}

async function loadOperationalHealth() {
  try {
    const health = await apiGet("/health");
    const api = document.getElementById("healthApi");
    if (api) api.textContent = health.status === "ok" ? "Operativa" : "Revisar";
  } catch (error) {
    const api = document.getElementById("healthApi");
    if (api) api.textContent = "Revisar";
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  await loadOperationalHealth();
  await loadMetrics();
  await loadLatestExecutions();
  await loadLatestReport();
  if (window.applyLanguage) window.applyLanguage();
});
