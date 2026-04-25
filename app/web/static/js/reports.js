let selectedReportId = null;
let selectedEvidenceReportId = null;

function fileStatus(fileInfo, label, type, reportId) {
  if (!fileInfo || !fileInfo.path) {
    return `<span class="badge muted-badge">No generado</span>`;
  }
  if (!fileInfo.exists) {
    return `<span class="badge danger" title="${safe(fileInfo.path)}">No encontrado</span>`;
  }
  const downloadUrl = `/api/reports/${reportId}/download/${type}`;
  const viewHtml = type === "html" ? `<a class="link-action" href="/api/reports/${reportId}/view/html" target="_blank">Abrir</a>` : "";
  return `<div class="file-actions-mini">
    <span class="badge success">Disponible</span>
    ${viewHtml}
    <a class="link-action" href="${downloadUrl}">Descargar</a>
  </div>`;
}

function reportActions(item) {
  const htmlBtn = item.files?.html?.exists
    ? `<button class="btn secondary" type="button" onclick="openHtmlViewer(${item.id}, '${safeAttr(item.execution?.test_name || 'Reporte')}')">Ver HTML</button>`
    : "";
  return `<div class="row-actions">
    ${htmlBtn}
    <button class="btn secondary" type="button" onclick="openEvidenceModal(${item.id}, ${item.execution_id})">Evidencias</button>
    <button class="btn secondary" type="button" onclick="openEmailReportModal(${item.id}, ${item.execution_id})">Enviar</button>
  </div>`;
}

async function loadReports() {
  const rows = await apiGet("/api/reports");
  const tbody = document.getElementById("reportsBody");
  tbody.innerHTML = rows.map(item => `
    <tr>
      <td>${item.id}</td>
      <td>${item.execution_id}</td>
      <td>${safe(item.execution?.test_name || '')}</td>
      <td>${statusBadge(item.execution?.status || 'N/A')}</td>
      <td>${fileStatus(item.files?.html, 'HTML', 'html', item.id)}</td>
      <td>${fileStatus(item.files?.excel, 'Excel', 'excel', item.id)}</td>
      <td>${fileStatus(item.files?.pdf, 'PDF', 'pdf', item.id)}</td>
      <td>${safe(item.created_at)}</td>
      <td>${reportActions(item)}</td>
    </tr>`).join("") || `<tr><td colspan="9" class="muted">Aún no hay reportes generados.</td></tr>`;
}

function statusBadge(status) {
  const normalized = String(status || '').toUpperCase();
  if (normalized.includes('PASS') || normalized.includes('SUCCESS')) return `<span class="badge success">${safe(status)}</span>`;
  if (normalized.includes('FAIL') || normalized.includes('ERROR')) return `<span class="badge danger">${safe(status)}</span>`;
  return `<span class="badge info">${safe(status)}</span>`;
}

function openHtmlViewer(reportId, title) {
  document.getElementById("viewerTitle").textContent = `Reporte #${reportId}`;
  document.getElementById("viewerSubtitle").textContent = title || "Vista previa del reporte HTML.";
  const frame = document.getElementById("reportPreviewFrame");
  frame.src = `/api/reports/${reportId}/view/html`;
  document.getElementById("reportViewerModal").classList.remove("hidden");
}

function closeHtmlViewer() {
  document.getElementById("reportPreviewFrame").src = "about:blank";
  document.getElementById("reportViewerModal").classList.add("hidden");
}

async function openEvidenceModal(reportId, executionId) {
  selectedEvidenceReportId = reportId;
  document.getElementById("evidenceSubtitle").textContent = `Reporte #${reportId} · Ejecución #${executionId}`;
  document.getElementById("evidenceModal").classList.remove("hidden");
  await loadEvidences(reportId);
}

function closeEvidenceModal() {
  document.getElementById("evidenceModal").classList.add("hidden");
  document.getElementById("evidenceList").innerHTML = "";
  document.getElementById("evidenceImage").classList.add("hidden");
  document.getElementById("evidenceImage").src = "";
  document.getElementById("evidenceMeta").classList.add("hidden");
  document.getElementById("evidenceEmpty").classList.remove("hidden");
}

async function loadEvidences(reportId) {
  const evidences = await apiGet(`/api/reports/${reportId}/evidences`);
  const list = document.getElementById("evidenceList");
  list.innerHTML = evidences.map(item => evidenceItemHtml(item)).join("") || `<div class="empty-state">Esta ejecución no tiene screenshots registrados.</div>`;
}

function evidenceItemHtml(item) {
  const disabled = item.exists && item.is_image ? "" : "disabled";
  const download = item.download_url ? `<a class="link-action" href="${item.download_url}">Descargar</a>` : `<span class="muted">Sin archivo</span>`;
  return `<div class="evidence-item">
    <div>
      <strong>Paso ${item.step_order}: ${safe(item.name)}</strong>
      <span>${safe(item.status)} · ${safe(item.action)}</span>
      <small>${safe(item.filename || item.screenshot_path || 'Sin screenshot')}</small>
    </div>
    <div class="evidence-actions">
      <button class="btn secondary" ${disabled} type="button" onclick='previewEvidence(${JSON.stringify(item).replace(/'/g, "&#39;")})'>Ver</button>
      ${download}
    </div>
  </div>`;
}

function previewEvidence(item) {
  const empty = document.getElementById("evidenceEmpty");
  const img = document.getElementById("evidenceImage");
  const meta = document.getElementById("evidenceMeta");
  empty.classList.add("hidden");
  img.classList.remove("hidden");
  meta.classList.remove("hidden");
  img.src = item.view_url;
  meta.innerHTML = `
    <strong>Paso ${safe(item.step_order)}: ${safe(item.name)}</strong>
    <span>Estado: ${safe(item.status)}</span>
    <span>Acción: ${safe(item.action)}</span>
    <span>Archivo: ${safe(item.filename || '')}</span>
    <span>Mensaje: ${safe(item.message || '')}</span>`;
}

async function loadDefaultRecipients() {
  try {
    const settings = await apiGet("/api/settings/public");
    const recipients = document.getElementById("email_recipients");
    if (recipients && !recipients.value) recipients.value = settings.smtp_default_recipients || "";
  } catch (error) {}
}

function openEmailReportModal(reportId, executionId) {
  selectedReportId = reportId;
  document.getElementById("email_report_id").value = reportId;
  document.getElementById("email_subject").value = `Reporte de ejecución #${executionId} - AutoTest Pro`;
  document.getElementById("email_message").value = "Hola,\n\nSe adjunta el reporte de ejecución generado por AutoTest Pro Framework.\n\nSaludos.";
  document.getElementById("emailReportModal").classList.remove("hidden");
  loadDefaultRecipients();
}

function closeEmailReportModal() {
  document.getElementById("emailReportModal").classList.add("hidden");
}

async function sendReportEmail(event) {
  event.preventDefault();
  const reportId = document.getElementById("email_report_id").value;
  const payload = {
    recipients: document.getElementById("email_recipients").value,
    subject: document.getElementById("email_subject").value || null,
    message: document.getElementById("email_message").value || null,
    include_html: document.getElementById("email_include_html").checked,
    include_excel: document.getElementById("email_include_excel").checked,
    include_pdf: document.getElementById("email_include_pdf").checked,
  };
  try {
    await apiPost(`/api/email/reports/${reportId}/send`, payload);
    toast("Reporte enviado correctamente");
    closeEmailReportModal();
  } catch (error) {
    toast("No se pudo enviar el reporte. Revisa SMTP y archivos adjuntos.");
  }
}

function safeAttr(value) {
  return String(value ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
}

document.addEventListener("DOMContentLoaded", () => {
  loadReports();
  const closeBtn = document.getElementById("closeEmailReportModal");
  if (closeBtn) closeBtn.addEventListener("click", closeEmailReportModal);
  const form = document.getElementById("emailReportForm");
  if (form) form.addEventListener("submit", sendReportEmail);
  const closeViewer = document.getElementById("closeReportViewerModal");
  if (closeViewer) closeViewer.addEventListener("click", closeHtmlViewer);
  const closeEvidence = document.getElementById("closeEvidenceModal");
  if (closeEvidence) closeEvidence.addEventListener("click", closeEvidenceModal);
});
