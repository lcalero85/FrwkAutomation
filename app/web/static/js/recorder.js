let recordedCases = [];
let selectedCase = null;
let isRecording = false;
let autoStatusTimer = null;
let currentAutoIngestUrl = '';
let currentApiBase = 'http://127.0.0.1:8000';

const casesTable = document.getElementById('recordedCasesTable');
const stepsTable = document.getElementById('recordedStepsTable');
const caseModal = document.getElementById('recordedCaseModal');
const codeModal = document.getElementById('codeModal');
const caseForm = document.getElementById('recordedCaseForm');
const stepForm = document.getElementById('stepForm');
const recorderControls = document.getElementById('recorderControls');
const selectedCaseTitle = document.getElementById('selectedCaseTitle');
const selectedCaseSubtitle = document.getElementById('selectedCaseSubtitle');
const recordingStatus = document.getElementById('recordingStatus');
const generateCodeBtn = document.getElementById('generateCodeBtn');
const runRecordedBtn = document.getElementById('runRecordedBtn');
const exportCodeBtn = document.getElementById('exportCodeBtn');
const downloadExportBtn = document.getElementById('downloadExportBtn');
const exportModal = document.getElementById('exportModal');
const autoRecorderBtn = document.getElementById('autoRecorderBtn');
const autoRecorderPanel = document.getElementById('autoRecorderPanel');
const copyRecorderUrlBtn = document.getElementById('copyRecorderUrlBtn');
const refreshRecordedStepsBtn = document.getElementById('refreshRecordedStepsBtn');
const emptyRecorderState = document.getElementById('emptyRecorderState');
const stepsSummary = document.getElementById('stepsSummary');

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }
  return response.status === 204 ? null : response.json();
}

function showMessage(message) {
  if (typeof showToast === 'function') showToast(message);
  else alert(message);
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
}

function statusBadge(status) {
  return `<span class="badge ${escapeHtml(status || 'UNKNOWN')}">${escapeHtml(status || 'UNKNOWN')}</span>`;
}

function actionLabel(action) {
  const labels = {
    open: 'Abrir URL', click: 'Click', double_click: 'Doble click', right_click: 'Click derecho',
    type: 'Escribir', assert_visible: 'Validar visible', assert_text: 'Validar texto', scroll: 'Scroll', wait: 'Esperar'
  };
  return labels[action] || action;
}

function stepTarget(step) {
  if (step.action_type === 'open') return step.url || step.input_value || '';
  return `${step.selector_type || ''}${step.selector_type ? ': ' : ''}${step.selector_value || ''}`;
}

function renderCases() {
  if (!recordedCases.length) {
    casesTable.innerHTML = '<tr><td colspan="6" class="muted">No hay casos grabados todavía. Presiona Nuevo caso para comenzar.</td></tr>';
    return;
  }
  casesTable.innerHTML = recordedCases.map(item => `
    <tr class="${selectedCase && selectedCase.id === item.id ? 'selected-row' : ''}">
      <td>${item.id}</td>
      <td><strong>${escapeHtml(item.name)}</strong><br><span class="muted">${escapeHtml(item.description || 'Sin descripción')}</span></td>
      <td>${escapeHtml(item.browser)}</td>
      <td>${statusBadge(item.status)}</td>
      <td>${item.steps ? item.steps.length : 0}</td>
      <td class="table-actions wrap">
        <button class="btn secondary" onclick="selectRecordedCase(${item.id})">Abrir</button>
        <button class="btn primary" onclick="runRecordedCase(${item.id})">Ejecutar</button>
        <button class="btn ghost" onclick="deleteRecordedCase(${item.id})">Eliminar</button>
      </td>
    </tr>
  `).join('');
}

function renderSteps() {
  if (!selectedCase) {
    stepsTable.innerHTML = '<tr><td colspan="5" class="muted">Selecciona un caso.</td></tr>';
    if (stepsSummary) stepsSummary.textContent = 'Selecciona un caso para ver los pasos.';
    return;
  }
  const steps = selectedCase.steps || [];
  document.getElementById('stepOrder').value = steps.length + 1;
  if (stepsSummary) stepsSummary.textContent = `${steps.length} paso(s) registrados. Puedes limpiar duplicados antes de ejecutar.`;
  if (!steps.length) {
    stepsTable.innerHTML = '<tr><td colspan="5" class="muted">Este caso todavía no tiene pasos. Abre el asistente automático o agrega pasos manuales.</td></tr>';
    return;
  }
  stepsTable.innerHTML = steps.map(step => `
    <tr>
      <td><span class="step-number">${step.step_order}</span></td>
      <td><strong>${escapeHtml(actionLabel(step.action_type))}</strong><br><span class="muted">${escapeHtml(step.expected_result || step.notes || '')}</span></td>
      <td class="path-cell">${escapeHtml(stepTarget(step))}</td>
      <td>${escapeHtml(step.input_value || '')}</td>
      <td><button class="btn ghost" onclick="deleteStep(${step.id})">Eliminar</button></td>
    </tr>
  `).join('');
}

async function loadCases() {
  try {
    recordedCases = await api('/api/recorder/cases');
    if (selectedCase) {
      const refreshed = recordedCases.find(item => item.id === selectedCase.id);
      selectedCase = refreshed ? await api(`/api/recorder/cases/${refreshed.id}`) : null;
    }
    renderCases();
    renderSelectedCase();
  } catch (error) {
    showMessage('Error cargando casos grabados');
    console.error(error);
  }
}

function renderSelectedCase() {
  if (!selectedCase) {
    selectedCaseTitle.textContent = 'Detalle del caso';
    selectedCaseSubtitle.textContent = 'Selecciona un caso para ver o agregar pasos.';
    stepForm.classList.add('hidden');
    recorderControls.classList.add('hidden');
    autoRecorderPanel.classList.add('hidden');
    emptyRecorderState.classList.remove('hidden');
    generateCodeBtn.disabled = true;
    runRecordedBtn.disabled = true;
    if (exportCodeBtn) exportCodeBtn.disabled = true;
    if (downloadExportBtn) downloadExportBtn.disabled = true;
    stopAutoStatusPolling();
    renderSteps();
    return;
  }
  selectedCaseTitle.textContent = selectedCase.name;
  selectedCaseSubtitle.textContent = selectedCase.base_url || 'Caso sin URL base configurada.';
  emptyRecorderState.classList.add('hidden');
  recorderControls.classList.remove('hidden');
  generateCodeBtn.disabled = false;
  runRecordedBtn.disabled = false;
  if (exportCodeBtn) exportCodeBtn.disabled = false;
  if (downloadExportBtn) downloadExportBtn.disabled = false;
  renderSteps();
}

async function selectRecordedCase(id) {
  selectedCase = await api(`/api/recorder/cases/${id}`);
  renderSelectedCase();
  renderCases();
}

async function deleteRecordedCase(id) {
  if (!confirm('¿Eliminar este caso grabado?')) return;
  await api(`/api/recorder/cases/${id}`, { method: 'DELETE' });
  if (selectedCase && selectedCase.id === id) selectedCase = null;
  await loadCases();
  showMessage('Caso eliminado');
}

async function deleteStep(id) {
  if (!selectedCase || !confirm('¿Eliminar este paso?')) return;
  await api(`/api/recorder/steps/${id}`, { method: 'DELETE' });
  await selectRecordedCase(selectedCase.id);
  await loadCases();
  showMessage('Paso eliminado');
}

function setRecordingState(state) {
  isRecording = state === 'recording';
  recordingStatus.textContent = state;
  recordingStatus.className = `recording-status ${state}`;
}

async function copyText(value, message) {
  try {
    await navigator.clipboard.writeText(value);
    showMessage(message);
  } catch {
    prompt('Copia este valor:', value);
  }
}

function stopAutoStatusPolling() {
  if (autoStatusTimer) clearInterval(autoStatusTimer);
  autoStatusTimer = null;
}

async function updateRecorderStatus() {
  if (!selectedCase) return;
  try {
    const status = await api(`/api/recorder/cases/${selectedCase.id}/browser-recorder-status`);
    document.getElementById('autoTotalSteps').textContent = status.total_steps;
    document.getElementById('autoLastEvent').textContent = status.last_step_summary || 'Sin eventos';
    setRecordingState(status.total_steps > 0 ? 'automatic-capturing' : 'automatic-ready');
  } catch (error) {
    console.error(error);
  }
}

async function openAutoRecorderPanel() {
  if (!selectedCase) return;
  try {
    const info = await api(`/api/recorder/cases/${selectedCase.id}/browser-recorder-instructions`);
    currentAutoIngestUrl = info.ingest_url;
    currentApiBase = new URL(info.ingest_url).origin;
    document.getElementById('autoCaseId').textContent = info.recorded_case_id;
    document.getElementById('autoApiBase').textContent = currentApiBase;
    document.getElementById('autoIngestUrl').textContent = info.ingest_url;
    document.getElementById('autoExtensionPath').textContent = info.extension_path;
    document.getElementById('autoRecorderInstructions').innerHTML = info.instructions.map(item => `<li>${escapeHtml(item)}</li>`).join('');
    autoRecorderPanel.classList.remove('hidden');
    setRecordingState('automatic-ready');
    await updateRecorderStatus();
    stopAutoStatusPolling();
    autoStatusTimer = setInterval(updateRecorderStatus, 3000);
    showMessage('Asistente automático listo. Copia los datos en la extensión.');
  } catch (error) {
    showMessage('No se pudo abrir el grabador automático');
    console.error(error);
  }
}

async function cleanupSteps() {
  if (!selectedCase) return;
  try {
    const result = await api(`/api/recorder/cases/${selectedCase.id}/cleanup`, { method: 'POST', body: '{}' });
    await selectRecordedCase(selectedCase.id);
    await loadCases();
    showMessage(`Limpieza completada. Eliminados: ${result.removed_steps}`);
  } catch (error) {
    showMessage('No se pudo limpiar el caso');
    console.error(error);
  }
}

async function clearAllSteps() {
  if (!selectedCase || !confirm('¿Borrar todos los pasos de este caso?')) return;
  try {
    const result = await api(`/api/recorder/cases/${selectedCase.id}/steps`, { method: 'DELETE' });
    await selectRecordedCase(selectedCase.id);
    await loadCases();
    showMessage(`Pasos eliminados: ${result.removed_steps}`);
  } catch (error) {
    showMessage('No se pudieron borrar los pasos');
    console.error(error);
  }
}

document.getElementById('newRecordedCaseBtn').addEventListener('click', () => caseModal.classList.remove('hidden'));
document.getElementById('closeRecordedCaseModal').addEventListener('click', () => caseModal.classList.add('hidden'));
document.getElementById('closeCodeModal').addEventListener('click', () => codeModal.classList.add('hidden'));
document.getElementById('recordBtn').addEventListener('click', () => { stepForm.classList.toggle('hidden'); setRecordingState('manual'); showMessage('Modo manual listo'); });
document.getElementById('cleanupStepsBtn')?.addEventListener('click', cleanupSteps);
document.getElementById('cleanupStepsBtnAlt')?.addEventListener('click', cleanupSteps);
document.getElementById('clearAllStepsBtn')?.addEventListener('click', clearAllSteps);
document.getElementById('hideAutoRecorderBtn')?.addEventListener('click', () => { autoRecorderPanel.classList.add('hidden'); stopAutoStatusPolling(); setRecordingState('idle'); });
document.getElementById('checkRecorderStatusBtn')?.addEventListener('click', async () => { await updateRecorderStatus(); await selectRecordedCase(selectedCase.id); showMessage('Estado actualizado'); });
document.getElementById('copyCaseIdBtn')?.addEventListener('click', () => selectedCase && copyText(String(selectedCase.id), 'Case ID copiado'));
document.getElementById('copyApiBaseBtn')?.addEventListener('click', () => copyText(currentApiBase, 'API base copiada'));
document.getElementById('clearVisualBtn')?.addEventListener('click', () => { stepForm.reset(); if (selectedCase) document.getElementById('stepOrder').value = (selectedCase.steps || []).length + 1; });

caseForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = {
    name: document.getElementById('caseName').value,
    browser: document.getElementById('caseBrowser').value,
    base_url: document.getElementById('caseBaseUrl').value || null,
    description: document.getElementById('caseDescription').value || null,
    status: 'DRAFT'
  };
  try {
    const created = await api('/api/recorder/cases', { method: 'POST', body: JSON.stringify(payload) });
    caseModal.classList.add('hidden');
    caseForm.reset();
    await loadCases();
    await selectRecordedCase(created.id);
    showMessage('Caso grabado creado');
  } catch (error) {
    showMessage('No se pudo crear el caso');
    console.error(error);
  }
});

stepForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!selectedCase) return;
  const payload = {
    step_order: Number(document.getElementById('stepOrder').value),
    action_type: document.getElementById('actionType').value,
    selector_type: document.getElementById('selectorType').value,
    selector_value: document.getElementById('selectorValue').value || null,
    input_value: document.getElementById('inputValue').value || null,
    url: document.getElementById('stepUrl').value || null,
    expected_result: document.getElementById('expectedResult').value || null,
    notes: document.getElementById('stepNotes').value || null
  };
  try {
    await api(`/api/recorder/cases/${selectedCase.id}/steps`, { method: 'POST', body: JSON.stringify(payload) });
    await selectRecordedCase(selectedCase.id);
    await loadCases();
    stepForm.reset();
    document.getElementById('stepOrder').value = (selectedCase.steps || []).length + 1;
    showMessage('Paso guardado');
  } catch (error) {
    showMessage('No se pudo guardar el paso');
    console.error(error);
  }
});

document.getElementById('suggestSelectorBtn').addEventListener('click', async () => {
  const selectorValue = document.getElementById('selectorValue').value;
  const payload = { css: selectorValue || null };
  try {
    const suggestions = await api('/api/recorder/selector-suggestions', { method: 'POST', body: JSON.stringify(payload) });
    if (!suggestions.length) {
      showMessage('Agrega ID, name, data-testid, aria-label o CSS para sugerir');
      return;
    }
    const best = suggestions[0];
    document.getElementById('selectorType').value = best.selector_type;
    document.getElementById('selectorValue').value = best.selector_value;
    showMessage(`Selector sugerido: ${best.selector_value}`);
  } catch (error) {
    showMessage('No se pudo sugerir selector');
    console.error(error);
  }
});

generateCodeBtn.addEventListener('click', async () => {
  if (!selectedCase) return;
  try {
    const result = await api(`/api/recorder/cases/${selectedCase.id}/code`);
    document.getElementById('generatedCode').textContent = result.code;
    codeModal.classList.remove('hidden');
  } catch (error) {
    showMessage('No se pudo generar código');
    console.error(error);
  }
});

async function runRecordedCase(id) {
  const caseToRun = selectedCase && selectedCase.id === id ? selectedCase : recordedCases.find(item => item.id === id);
  if (!caseToRun) return;
  if (!confirm(`¿Ejecutar el caso grabado "${caseToRun.name}"?`)) return;
  try {
    showMessage('Ejecutando caso grabado. El navegador se abrirá en breve...');
    const payload = {
      browser: caseToRun.browser || 'chrome',
      headless: false,
      environment: 'recorded',
      base_url: caseToRun.base_url || null,
      report: 'html,excel,pdf',
      timeout: 15,
      stop_on_failure: true
    };
    const execution = await api(`/api/recorder/cases/${id}/run`, { method: 'POST', body: JSON.stringify(payload) });
    showMessage(`Ejecución finalizada: ${execution.status}`);
    window.location.href = `/ui/executions/${execution.id}`;
  } catch (error) {
    showMessage('No se pudo ejecutar el caso grabado');
    console.error(error);
  }
}

runRecordedBtn.addEventListener('click', () => {
  if (selectedCase) runRecordedCase(selectedCase.id);
});

if (autoRecorderBtn) autoRecorderBtn.addEventListener('click', openAutoRecorderPanel);
if (copyRecorderUrlBtn) copyRecorderUrlBtn.addEventListener('click', () => currentAutoIngestUrl && copyText(currentAutoIngestUrl, 'Endpoint técnico copiado'));
if (refreshRecordedStepsBtn) refreshRecordedStepsBtn.addEventListener('click', async () => {
  if (!selectedCase) return;
  await selectRecordedCase(selectedCase.id);
  await loadCases();
  await updateRecorderStatus();
  showMessage('Pasos actualizados desde el grabador automático');
});

loadCases();

async function openExportPreview() {
  if (!selectedCase) return;
  try {
    const result = await api(`/api/recorder/cases/${selectedCase.id}/export/preview`);
    document.getElementById('exportPageObjectCode').textContent = result.page_object_code;
    document.getElementById('exportTestCode').textContent = result.test_code;
    document.getElementById('exportReadme').textContent = result.readme;
    exportModal.classList.remove('hidden');
  } catch (error) {
    showMessage('No se pudo preparar la exportación');
    console.error(error);
  }
}

async function createExportZip() {
  if (!selectedCase) return;
  try {
    const result = await api(`/api/recorder/cases/${selectedCase.id}/export`, { method: 'POST', body: '{}' });
    showMessage(`ZIP generado: ${result.zip_filename}`);
  } catch (error) {
    showMessage('No se pudo generar el ZIP exportable');
    console.error(error);
  }
}

function downloadExportZip() {
  if (!selectedCase) return;
  window.open(`/api/recorder/cases/${selectedCase.id}/export/download`, '_blank');
}

if (exportCodeBtn) exportCodeBtn.addEventListener('click', openExportPreview);
if (downloadExportBtn) downloadExportBtn.addEventListener('click', downloadExportZip);
document.getElementById('closeExportModal')?.addEventListener('click', () => exportModal.classList.add('hidden'));
document.getElementById('createExportZipBtn')?.addEventListener('click', createExportZip);
document.getElementById('downloadExportZipBtn')?.addEventListener('click', downloadExportZip);
