const settingFields = [
  "app_name", "company_name", "support_email", "website_url", "logo_text", "tagline",
  "primary_color", "secondary_color", "theme", "language", "font_family", "font_size", "timezone", "reports_path",
  "logs_path", "screenshots_path", "videos_path", "default_browser", "default_environment",
  "execution_timeout", "screenshot_on_failure", "screenshot_each_step", "date_format", "session_timeout_minutes",
  "default_parallel_workers", "retry_failed_tests", "max_retry_count", "auto_open_latest_report", "mask_sensitive_data",
  "audit_retention_days", "reports_retention_days", "default_report_formats", "smtp_server",
  "smtp_port", "smtp_user", "smtp_password", "smtp_sender", "smtp_use_tls", "smtp_use_ssl", "smtp_default_recipients"
];

function effectiveLanguage(dataLanguage) {
  const top = document.getElementById("languageSelector")?.value;
  const saved = localStorage.getItem("autotest_language");
  const value = top || saved || dataLanguage || "es";
  return ["en", "english"].includes(String(value).toLowerCase()) ? "en" : "es";
}

function readSettingsForm() {
  const data = {};
  for (const field of settingFields) {
    const el = document.getElementById(field);
    if (el) data[field] = el.value;
  }
  data.language = effectiveLanguage(data.language);
  return data;
}

function fillSettingsForm(data) {
  const lang = effectiveLanguage(data?.language);
  for (const field of settingFields) {
    const el = document.getElementById(field);
    if (!el || data[field] === undefined || data[field] === null) continue;
    el.value = field === "language" ? lang : data[field];
  }
  const topTheme = document.getElementById("themeSelector");
  if (topTheme && data.theme) topTheme.value = data.theme;
  const topLang = document.getElementById("languageSelector");
  if (topLang) topLang.value = lang;
  localStorage.setItem("autotest_language", lang);
  if (data.theme && window.applyTheme) window.applyTheme(data.theme);
  if (window.applyFontSettings) window.applyFontSettings(data.font_family, data.font_size);
  if (window.applyLanguage) window.applyLanguage(lang);
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
  const previewLogo = document.getElementById("previewLogo"); if (previewLogo) previewLogo.textContent = logo;
  const previewCompany = document.getElementById("previewCompany"); if (previewCompany) previewCompany.textContent = company;
  const previewApp = document.getElementById("previewApp"); if (previewApp) previewApp.textContent = app;
  const previewTagline = document.getElementById("previewTagline"); if (previewTagline) previewTagline.textContent = tagline;
}

async function loadSettings() {
  try {
    const data = await apiGet("/api/settings");
    const lang = effectiveLanguage(data.language);
    fillSettingsForm({ ...data, language: lang });
  } catch (error) {
    toast(effectiveLanguage() === "en" ? "Settings could not be loaded" : "No se pudo cargar la configuración");
  }
}

async function saveSettings(event) {
  event.preventDefault();
  try {
    const payload = readSettingsForm();
    const data = await apiPut("/api/settings", payload);
    localStorage.setItem("autotest_language", payload.language);
    localStorage.setItem("autotest_theme", payload.theme || "Corporate Light");
    localStorage.setItem("autotest_font_family", payload.font_family || "Inter / Segoe UI");
    localStorage.setItem("autotest_font_size", String(payload.font_size || "15").replace("px", ""));
    fillSettingsForm({ ...data, language: payload.language, font_family: payload.font_family, font_size: payload.font_size, theme: payload.theme });
    toast(payload.language === "en" ? "Settings saved and applied successfully." : "Configuración guardada y aplicada correctamente.");
  } catch (error) {
    toast(effectiveLanguage() === "en" ? "Settings could not be saved" : "No se pudo guardar la configuración");
  }
}

async function resetSettings() {
  const lang = effectiveLanguage();
  if (!confirm(lang === "en" ? "Restore default settings?" : "¿Restaurar la configuración por defecto?")) return;
  try {
    const data = await apiPost("/api/settings/reset", {});
    fillSettingsForm({ ...data, language: lang });
    toast(lang === "en" ? "Settings restored" : "Configuración restaurada");
  } catch (error) {
    toast(lang === "en" ? "Settings could not be restored" : "No se pudo restaurar la configuración");
  }
}

async function sendSmtpTest() {
  const lang = effectiveLanguage();
  const recipient = document.getElementById("smtp_test_recipient")?.value?.trim();
  if (!recipient) { toast(lang === "en" ? "Enter a recipient email for the SMTP test" : "Ingresa un correo destino para la prueba SMTP"); return; }
  const btn = document.getElementById("testSmtpBtn");
  const original = btn ? btn.textContent : "Send test email";
  try {
    if (btn) { btn.disabled = true; btn.textContent = lang === "en" ? "Sending..." : "Enviando..."; }
    await apiPost("/api/email/test", { recipient });
    toast(lang === "en" ? "Test email sent successfully" : "Correo de prueba enviado correctamente");
  } catch (error) {
    toast(lang === "en" ? "The test email could not be sent. Check SMTP, user, and password." : "No se pudo enviar el correo de prueba. Revisa SMTP, usuario y contraseña.");
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = original; if (window.applyLanguage) window.applyLanguage(lang); }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadSettings();
  const form = document.getElementById("settingsForm");
  if (form) form.addEventListener("submit", saveSettings);
  const resetBtn = document.getElementById("resetSettingsBtn");
  if (resetBtn) resetBtn.addEventListener("click", resetSettings);
  const testBtn = document.getElementById("testSmtpBtn");
  if (testBtn) testBtn.addEventListener("click", sendSmtpTest);
  for (const field of settingFields) {
    const el = document.getElementById(field);
    if (!el) continue;
    el.addEventListener("input", () => {
      updatePreview();
      if (field === "theme" && window.applyTheme) window.applyTheme(el.value);
      if ((field === "font_family" || field === "font_size") && window.applyFontSettings) window.applyFontSettings(document.getElementById("font_family")?.value, document.getElementById("font_size")?.value);
      if (field === "language" && window.applyLanguage) window.applyLanguage(el.value);
    });
    el.addEventListener("change", () => {
      if ((field === "font_family" || field === "font_size") && window.applyFontSettings) window.applyFontSettings(document.getElementById("font_family")?.value, document.getElementById("font_size")?.value);
      if (field === "language" && window.applyLanguage) window.applyLanguage(el.value);
    });
  }
});
