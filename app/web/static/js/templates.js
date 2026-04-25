async function apiFetch(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    let message = `${options.method || 'GET'} ${path} failed`;
    try {
      const data = await response.json();
      message = data.detail || JSON.stringify(data);
    } catch (_) {
      message = await response.text() || message;
    }
    throw new Error(message);
  }
  return response.json();
}

let selectedTemplateId = null;
let selectedTemplate = null;

const caseSample = {
  name: "flujo_basico_desde_plantilla",
  description: "Caso base creado desde una plantilla personalizada.",
  suite_name: "Suite personalizada",
  steps: [
    { action_type: "open", url: "{{BASE_URL}}", expected_result: "Abrir el sistema" },
    { action_type: "click", selector_type: "css", selector_value: "{{BUTTON_SELECTOR}}", expected_result: "Click en botón principal" },
    { action_type: "assert_visible", selector_type: "css", selector_value: "{{SUCCESS_SELECTOR}}", expected_result: "Validar resultado esperado" }
  ]
};

function typeBadge(type) {
  const label = type === "PROJECT" ? "Proyecto" : type === "SUITE" ? "Suite" : "Caso";
  return `<span class="badge info">${label}</span>`;
}

function templateCard(template) {
  return `
    <article class="template-card" data-id="${template.id}">
      <div class="template-card-header">
        ${typeBadge(template.template_type)}
        <span class="badge ${template.priority === 'HIGH' || template.priority === 'CRITICAL' ? 'danger' : 'success'}">${template.priority}</span>
      </div>
      <h3>${template.name}</h3>
      <p>${template.description || 'Sin descripción.'}</p>
      <div class="template-meta">
        <span>${template.category}</span>
        <span>${template.is_system ? 'Sistema' : 'Personalizada'}</span>
      </div>
      <div class="row-actions">
        <button class="btn secondary" onclick="selectTemplate(${template.id})" type="button">Seleccionar</button>
        ${template.is_system ? '' : `<button class="btn danger-soft" onclick="deleteTemplate(${template.id})" type="button">Eliminar</button>`}
      </div>
    </article>`;
}

async function loadTemplates() {
  const type = document.getElementById('templateTypeFilter').value;
  const url = type ? `/api/templates?template_type=${encodeURIComponent(type)}` : '/api/templates';
  const data = await apiFetch(url);
  const container = document.getElementById('templateCards');
  if (!data.length) {
    container.innerHTML = '<p class="muted">No hay plantillas para mostrar.</p>';
    return;
  }
  container.innerHTML = data.map(templateCard).join('');
}

async function selectTemplate(id) {
  selectedTemplateId = id;
  selectedTemplate = await apiFetch(`/api/templates/${id}`);
  document.getElementById('applyTemplateBtn').disabled = false;
  const payload = JSON.stringify(selectedTemplate.payload, null, 2);
  document.getElementById('selectedTemplateInfo').innerHTML = `
    <h3>${selectedTemplate.name}</h3>
    <p>${selectedTemplate.description || ''}</p>
    <div class="template-meta"><span>${selectedTemplate.template_type}</span><span>${selectedTemplate.category}</span><span>${selectedTemplate.priority}</span></div>
    <pre class="code-block small-code">${escapeHtml(payload)}</pre>
  `;
}

async function applySelectedTemplate(event) {
  event.preventDefault();
  if (!selectedTemplateId) return;
  const projectIdRaw = document.getElementById('applyProjectId').value;
  const payload = {
    project_name: document.getElementById('applyProjectName').value || null,
    project_id: projectIdRaw ? Number(projectIdRaw) : null,
    suite_name: document.getElementById('applySuiteName').value || null,
    base_url: document.getElementById('applyBaseUrl').value || null,
    default_browser: document.getElementById('applyBrowser').value || 'chrome'
  };
  const resultBox = document.getElementById('applyResult');
  resultBox.classList.remove('hidden');
  resultBox.textContent = 'Aplicando plantilla...';
  try {
    const result = await apiFetch(`/api/templates/${selectedTemplateId}/apply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    resultBox.innerHTML = `<strong>${result.message}</strong><br>${result.created_items.map(x => `• ${x}`).join('<br>')}`;
    showToast('Plantilla aplicada correctamente.');
  } catch (error) {
    resultBox.textContent = error.message;
    showToast(error.message);
  }
}

async function createTemplate(event) {
  event.preventDefault();
  let payload;
  try {
    payload = JSON.parse(document.getElementById('templatePayload').value);
  } catch (error) {
    showToast('El payload JSON no es válido.');
    return;
  }
  const body = {
    name: document.getElementById('templateName').value,
    template_type: document.getElementById('templateType').value,
    category: document.getElementById('templateCategory').value || 'Personalizada',
    description: document.getElementById('templateDescription').value || null,
    priority: document.getElementById('templatePriority').value,
    tags: document.getElementById('templateTags').value || null,
    payload,
    is_system: false
  };
  await apiFetch('/api/templates', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  showToast('Plantilla personalizada creada.');
  event.target.reset();
  document.getElementById('templatePayload').value = JSON.stringify(caseSample, null, 2);
  await loadTemplates();
}

async function deleteTemplate(id) {
  if (!confirm('¿Eliminar esta plantilla personalizada?')) return;
  await apiFetch(`/api/templates/${id}`, { method: 'DELETE' });
  showToast('Plantilla eliminada.');
  await loadTemplates();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('templatePayload').value = JSON.stringify(caseSample, null, 2);
  document.getElementById('templateTypeFilter').addEventListener('change', loadTemplates);
  document.getElementById('reloadTemplatesBtn').addEventListener('click', loadTemplates);
  document.getElementById('applyTemplateForm').addEventListener('submit', applySelectedTemplate);
  document.getElementById('createTemplateForm').addEventListener('submit', createTemplate);
  document.getElementById('loadCaseSampleBtn').addEventListener('click', () => {
    document.getElementById('templatePayload').value = JSON.stringify(caseSample, null, 2);
  });
  loadTemplates();
});
