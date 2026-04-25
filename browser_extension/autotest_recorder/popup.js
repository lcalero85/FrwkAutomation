const caseIdInput = document.getElementById('caseId');
const apiBaseInput = document.getElementById('apiBase');
const enabledInput = document.getElementById('enabled');
const captureScrollInput = document.getElementById('captureScroll');
const showBadgeInput = document.getElementById('showBadge');
const statusBox = document.getElementById('status');

async function loadConfig() {
  const config = await chrome.storage.local.get({
    caseId: '',
    apiBase: 'http://127.0.0.1:8000',
    enabled: false,
    captureScroll: false,
    showBadge: true
  });
  caseIdInput.value = config.caseId || '';
  apiBaseInput.value = config.apiBase || 'http://127.0.0.1:8000';
  enabledInput.checked = Boolean(config.enabled);
  captureScrollInput.checked = Boolean(config.captureScroll);
  showBadgeInput.checked = Boolean(config.showBadge);
}

async function saveConfig(forceEnabled = null) {
  const enabled = forceEnabled === null ? enabledInput.checked : forceEnabled;
  enabledInput.checked = enabled;
  await chrome.storage.local.set({
    caseId: caseIdInput.value.trim(),
    apiBase: apiBaseInput.value.trim().replace(/\/$/, ''),
    enabled,
    captureScroll: captureScrollInput.checked,
    showBadge: showBadgeInput.checked
  });
  statusBox.className = '';
  statusBox.textContent = enabled
    ? 'Captura activa. Recarga el sitio bajo prueba y realiza el flujo.'
    : 'Captura pausada.';
}

async function testConnection() {
  await saveConfig(enabledInput.checked);
  const caseId = caseIdInput.value.trim();
  const apiBase = apiBaseInput.value.trim().replace(/\/$/, '');
  if (!caseId) {
    statusBox.className = 'error';
    statusBox.textContent = 'Debes indicar el Case ID.';
    return;
  }
  try {
    const response = await fetch(`${apiBase}/api/recorder/public/cases/${caseId}/browser-events`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({event_type: 'recorder_test', action_type: 'wait', notes: 'Extension connection test', url: 'chrome-extension-popup'})
    });
    if (!response.ok) throw new Error(await response.text());
    statusBox.className = '';
    statusBox.textContent = 'Conexión correcta. Vuelve a AutoTest Pro y presiona Verificar conexión.';
  } catch (error) {
    statusBox.className = 'error';
    statusBox.textContent = `No se pudo conectar con la API local.\n${error.message}`;
  }
}

document.getElementById('saveBtn').addEventListener('click', () => saveConfig(true));
document.getElementById('pauseBtn').addEventListener('click', () => saveConfig(false));
document.getElementById('testBtn').addEventListener('click', testConnection);
loadConfig();
