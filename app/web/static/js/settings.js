const settingFields = [
  "app_name", "company_name", "support_email", "website_url", "logo_text", "tagline",
  "primary_color", "secondary_color", "theme", "language", "timezone", "reports_path",
  "logs_path", "screenshots_path", "videos_path", "default_browser", "default_environment",
  "execution_timeout", "screenshot_on_failure", "screenshot_each_step", "smtp_server",
  "smtp_port", "smtp_user", "smtp_password", "smtp_sender", "smtp_use_tls", "smtp_use_ssl", "smtp_default_recipients"
];

async function apiPut(path, body) {
  const response = await fetch(API + path, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `PUT ${path} failed`);
  }
  return response.json();
}

function readSettingsForm() {
  const data = {};
  for (const field of settingFields) {
    const el = document.getElementById(field);
    if (el) data[field] = el.value;
  }
  return data;
}

function fillSettingsForm(data) {
  for (const field of settingFields) {
    const el = document.getElementById(field);
    if (el && data[field] !== undefined && data[field] !== null) {
      el.value = data[field];
    }
  }
  updatePreview();
}

function updatePreview() {
  const logo = document.getElementById("logo_text")?.value || "AT";
  const company = document.getElementById("company_name")?.value || "AutoTest Pro";
  const app = document.getElementById("app_name")?.value || "AutoTest Pro Framework";
  const tagline = document.getElementById("tagline")?.value || "Plataforma de Automatización QA";
  const primary = document.getElementById("primary_color")?.value || "#2463eb";
  const secondary = document.getElementById("secondary_color")?.value || "#0e1930";

  document.documentElement.style.setProperty("--primary", primary);
  document.documentElement.style.setProperty("--primary-dark", primary);
  document.documentElement.style.setProperty("--sidebar-bg", secondary);
  const previewLogo = document.getElementById("previewLogo");
  if (previewLogo) previewLogo.textContent = logo;
  const previewCompany = document.getElementById("previewCompany");
  if (previewCompany) previewCompany.textContent = company;
  const previewApp = document.getElementById("previewApp");
  if (previewApp) previewApp.textContent = app;
  const previewTagline = document.getElementById("previewTagline");
  if (previewTagline) previewTagline.textContent = tagline;
}

async function loadSettings() {
  try {
    const data = await apiGet("/api/settings");
    fillSettingsForm(data);
  } catch (error) {
    toast("No se pudo cargar la configuración");
  }
}

async function saveSettings(event) {
  event.preventDefault();
  try {
    const payload = readSettingsForm();
    const data = await apiPut("/api/settings", payload);
    fillSettingsForm(data);
    toast("Configuración guardada correctamente. Recarga la página para ver todos los cambios.");
  } catch (error) {
    toast("No se pudo guardar la configuración");
  }
}

async function resetSettings() {
  if (!confirm("¿Restaurar la configuración por defecto?")) return;
  try {
    const data = await apiPost("/api/settings/reset", {});
    fillSettingsForm(data);
    toast("Configuración restaurada");
  } catch (error) {
    toast("No se pudo restaurar la configuración");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadSettings();
  const form = document.getElementById("settingsForm");
  if (form) form.addEventListener("submit", saveSettings);
  const resetBtn = document.getElementById("resetSettingsBtn");
  if (resetBtn) resetBtn.addEventListener("click", resetSettings);
  for (const field of settingFields) {
    const el = document.getElementById(field);
    if (el) el.addEventListener("input", updatePreview);
  }
});


async function sendSmtpTest() {
  const recipient = document.getElementById("smtp_test_recipient")?.value?.trim();
  if (!recipient) {
    toast("Ingresa un correo destino para la prueba SMTP");
    return;
  }
  const btn = document.getElementById("testSmtpBtn");
  const original = btn ? btn.textContent : "Enviar correo de prueba";
  try {
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Enviando...";
    }
    await apiPost("/api/email/test", { recipient });
    toast("Correo de prueba enviado correctamente");
  } catch (error) {
    toast("No se pudo enviar el correo de prueba. Revisa SMTP, usuario y contraseña.");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = original;
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const testBtn = document.getElementById("testSmtpBtn");
  if (testBtn) testBtn.addEventListener("click", sendSmtpTest);
});
