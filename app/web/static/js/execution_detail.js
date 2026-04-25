const detailRoot = document.querySelector(".execution-detail");
const executionId = detailRoot?.dataset.executionId;
let traceData = null;

function fileStatus(file, label) {
  if (!file || !file.path) return `<span class="badge UNKNOWN">${label}: no generado</span>`;
  return file.exists
    ? `<span class="badge PASSED">${label}: disponible</span>`
    : `<span class="badge FAILED">${label}: no encontrado</span>`;
}

function renderStats(execution) {
  document.getElementById("traceStats").innerHTML = `
    <article class="stat-card"><span>Estado</span><strong>${safe(execution.status)}</strong><small>${safe(execution.browser)} · ${safe(execution.environment)}</small></article>
    <article class="stat-card"><span>Éxito</span><strong>${safe(execution.success_percentage)}%</strong><small>${safe(execution.passed_steps)} de ${safe(execution.total_steps)} pasos OK</small></article>
    <article class="stat-card"><span>Duración</span><strong>${seconds(execution.duration_seconds)}</strong><small>Inicio: ${safe(execution.started_at)}</small></article>
    <article class="stat-card"><span>Fallos</span><strong>${safe(execution.failed_steps)}</strong><small>Omitidos: ${safe(execution.skipped_steps)}</small></article>`;
}

function renderTimeline(timeline) {
  const el = document.getElementById("timeline");
  el.innerHTML = timeline.map(item => `
    <div class="timeline-item ${safe(item.status)}">
      <div class="timeline-index">${item.order}</div>
      <div>
        <strong>${safe(item.label)}</strong>
        <span>${statusBadge(item.status)} · ${seconds(item.duration_seconds)}</span>
      </div>
    </div>`).join("") || `<p class="muted">Sin pasos para mostrar.</p>`;
}

function renderSummary(data) {
  const execution = data.execution;
  const report = data.report;
  const longest = data.summary.longest_step;
  document.getElementById("technicalSummary").innerHTML = `
    <div class="list-item"><strong>UID</strong><span>${safe(execution.execution_uid)}</span></div>
    <div class="list-item"><strong>Proyecto / suite / caso</strong><span>${safe(execution.project_name)} / ${safe(execution.suite_name)} / ${safe(execution.test_name)}</span></div>
    <div class="list-item"><strong>Mensaje final</strong><span>${safe(execution.message)}</span></div>
    <div class="list-item"><strong>Paso más lento</strong><span>${longest ? `${safe(longest.label || longest.name)} · ${seconds(longest.duration_seconds)}` : "Sin datos"}</span></div>
    <div class="list-item"><strong>Evidencias</strong><span>${data.summary.evidence_count} evidencia(s) disponible(s)</span></div>
    <div class="list-item"><strong>Reportes</strong><span class="report-badges">${fileStatus(report?.html, "HTML")} ${fileStatus(report?.excel, "Excel")} ${fileStatus(report?.pdf, "PDF")}</span></div>
    ${report ? `<div class="table-actions">
      ${report.html_view_url ? `<a class="btn secondary" href="${report.html_view_url}" target="_blank">Abrir HTML</a>` : ""}
      ${report.excel_download_url ? `<a class="btn secondary" href="${report.excel_download_url}">Descargar Excel</a>` : ""}
      ${report.pdf_download_url ? `<a class="btn secondary" href="${report.pdf_download_url}">Descargar PDF</a>` : ""}
    </div>` : ""}`;
}

function renderSteps(steps) {
  document.getElementById("traceStepsBody").innerHTML = steps.map(step => `
    <tr>
      <td>${step.step_order}</td>
      <td><strong>${safe(step.name)}</strong><br><small class="muted">${safe(step.message)}</small>${step.error_detail ? `<pre class="inline-error">${safe(step.error_detail)}</pre>` : ""}</td>
      <td>${safe(step.action)}</td>
      <td class="path-cell">${safe(step.selector)}</td>
      <td>${statusBadge(step.status)}</td>
      <td>${seconds(step.duration_seconds)}</td>
      <td>${step.view_evidence_url ? `<button class="btn secondary" onclick="openEvidence('${step.view_evidence_url}', '${step.step_order} - ${safe(step.name)}')">Ver</button>` : `<span class="muted">No disponible</span>`} ${step.download_evidence_url ? `<a class="btn ghost" href="${step.download_evidence_url}">Descargar</a>` : ""}</td>
    </tr>`).join("") || `<tr><td colspan="7" class="muted">Sin pasos registrados.</td></tr>`;
}

function renderFailures(failures) {
  document.getElementById("failuresList").innerHTML = failures.map(step => `
    <div class="list-item failure-item">
      <strong>Paso ${step.step_order}: ${safe(step.name)}</strong>
      <span>${safe(step.message)}</span>
      ${step.error_detail ? `<pre class="inline-error">${safe(step.error_detail)}</pre>` : ""}
    </div>`).join("") || `<p class="muted">No se registraron fallos en esta ejecución.</p>`;
}

async function renderLogs() {
  const data = await apiGet(`/api/executions/${executionId}/logs`);
  document.getElementById("executionLogs").textContent = data.lines.join("\n") || "No hay logs reconstruidos.";
}

function openEvidence(url, caption) {
  document.getElementById("evidenceCaption").textContent = caption;
  document.getElementById("evidenceImage").src = url;
  document.getElementById("evidenceModal").classList.remove("hidden");
}

function closeEvidence() {
  document.getElementById("evidenceImage").src = "";
  document.getElementById("evidenceModal").classList.add("hidden");
}

async function loadTrace() {
  if (!executionId) return;
  traceData = await apiGet(`/api/executions/${executionId}/trace`);
  const execution = traceData.execution;
  document.getElementById("executionTitle").textContent = `Ejecución #${execution.id} · ${safe(execution.test_name)}`;
  document.getElementById("executionSubtitle").textContent = `${safe(execution.project_name)} · ${safe(execution.suite_name)} · ${safe(execution.started_at)}`;
  renderStats(execution);
  renderTimeline(traceData.timeline);
  renderSummary(traceData);
  renderSteps(traceData.steps);
  renderFailures(traceData.failures);
  await renderLogs();
}

document.addEventListener("DOMContentLoaded", async () => {
  document.getElementById("refreshTrace")?.addEventListener("click", loadTrace);
  document.getElementById("closeEvidenceModal")?.addEventListener("click", closeEvidence);
  await loadTrace();
});
