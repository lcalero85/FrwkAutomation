const API = "";

const THEME_OPTIONS = {
  "Corporate Light": { bg: "#eef3f8", surface: "#ffffff", surface2: "#f7f9fc", text: "#172033", muted: "#64748b", primary: "#2463eb", sidebar: "#0e1930", border: "#d9e2ef" },
  "Corporate Dark": { bg: "#0d1320", surface: "#121a2b", surface2: "#182235", text: "#edf4ff", muted: "#9aacc7", primary: "#68a2ff", sidebar: "#08101f", border: "#26344c" },
  "QA Blue": { bg: "#eaf2ff", surface: "#ffffff", surface2: "#f2f7ff", text: "#10203d", muted: "#55708f", primary: "#1769e0", sidebar: "#0b2b54", border: "#cfe0f5" },
  "Automation Green": { bg: "#eefaf2", surface: "#ffffff", surface2: "#f4fbf6", text: "#10291c", muted: "#597365", primary: "#15803d", sidebar: "#0d2c1a", border: "#cfe8d7" },
  "Minimal Gray": { bg: "#f3f4f6", surface: "#ffffff", surface2: "#f8fafc", text: "#1f2937", muted: "#6b7280", primary: "#475569", sidebar: "#111827", border: "#e5e7eb" },
  "Neon Tech": { bg: "#080b16", surface: "#10162a", surface2: "#141d35", text: "#eaf6ff", muted: "#91a4c1", primary: "#22d3ee", sidebar: "#050816", border: "#24304d" },
  "Purple Pro": { bg: "#f4efff", surface: "#ffffff", surface2: "#faf7ff", text: "#26143f", muted: "#6d5a84", primary: "#7c3aed", sidebar: "#24103f", border: "#ded2f4" },
  "Ocean Clean": { bg: "#edf9fb", surface: "#ffffff", surface2: "#f5fcfd", text: "#102a33", muted: "#56747d", primary: "#0891b2", sidebar: "#073344", border: "#ccebef" },
  "Black Gold": { bg: "#111111", surface: "#1c1c1c", surface2: "#252525", text: "#fff7e6", muted: "#c8b98a", primary: "#d4af37", sidebar: "#050505", border: "#3a3320" },
  "White Label Neutral": { bg: "#f7f7f8", surface: "#ffffff", surface2: "#fbfbfc", text: "#202124", muted: "#6f7378", primary: "#3f5f7f", sidebar: "#2d3748", border: "#e6e8eb" }
};

const I18N = {
  es: {
    "menu.dashboard": "Dashboard", "menu.projects": "Proyectos", "menu.recorder": "Grabador", "menu.scheduler": "Scheduler", "menu.executions": "Ejecuciones", "menu.reports": "Reportes", "menu.templates": "Plantillas", "menu.profile": "Perfil", "menu.users": "Usuarios", "menu.audit": "Auditoría", "menu.settings": "Configuración", "menu.faq": "Preguntas frecuentes", "menu.about": "Acerca de",
    "topbar.theme": "Tema", "topbar.language": "Idioma", "topbar.logout": "Salir", "topbar.apiDocs": "API Docs"
  },
  en: {
    "menu.dashboard": "Dashboard", "menu.projects": "Projects", "menu.recorder": "Recorder", "menu.scheduler": "Scheduler", "menu.executions": "Executions", "menu.reports": "Reports", "menu.templates": "Templates", "menu.profile": "Profile", "menu.users": "Users", "menu.audit": "Audit", "menu.settings": "Settings", "menu.faq": "FAQ", "menu.about": "About",
    "topbar.theme": "Theme", "topbar.language": "Language", "topbar.logout": "Logout", "topbar.apiDocs": "API Docs"
  }
};

const PHRASE_TRANSLATIONS = {
  en: {
    "Plataforma de Automatización QA": "QA Automation Platform",
    "Centro de control": "Control center",
    "Resumen ejecutivo de automatización": "Automation executive summary",
    "Visualiza salud general, actividad reciente, reportes, casos grabados y rendimiento de ejecución.": "View overall health, recent activity, reports, recorded cases, and execution performance.",
    "Ver último reporte generado": "View latest generated report",
    "Ver ejecuciones": "View executions",
    "Ver reportes": "View reports",
    "Proyectos": "Projects",
    "Suites": "Suites",
    "Casos": "Cases",
    "Éxito global": "Global success",
    "Ejecuciones": "Executions",
    "Reportes": "Reports",
    "Jobs": "Jobs",
    "Fallidas": "Failed",
    "Distribución de resultados": "Result distribution",
    "Ejecuciones por navegador": "Executions by browser",
    "Tendencia reciente": "Recent trend",
    "Últimas ejecuciones": "Latest executions",
    "Historial reciente almacenado en SQLite.": "Recent history stored in SQLite.",
    "Estado operativo": "Operational status",
    "Validaciones rápidas del entorno local.": "Quick checks of the local environment.",
    "Accesos rápidos": "Quick access",
    "Atajos para operación diaria del framework.": "Shortcuts for daily framework operation.",
    "Gestionar proyectos": "Manage projects",
    "Abrir grabador": "Open recorder",
    "Programar ejecución": "Schedule execution",
    "Usar plantillas": "Use templates",
    "Proyectos de automatización": "Automation projects",
    "Administra proyectos, URL base, navegador y estado.": "Manage projects, base URL, browser, and status.",
    "Nuevo proyecto": "New project",
    "Nombre": "Name", "URL base": "Base URL", "Navegador": "Browser", "Estado": "Status", "Acciones": "Actions", "Eliminar": "Delete", "Ver detalle": "View details",
    "Programador de ejecuciones": "Execution scheduler",
    "Agenda ejecuciones demo y administra trabajos recurrentes.": "Schedule demo executions and manage recurring jobs.",
    "Nuevo job": "New job",
    "Frecuencia": "Frequency", "Próxima ejecución": "Next execution",
    "Orquestador rápido": "Quick orchestrator",
    "Ejecuta el caso demo desde esta pantalla y valida la integración API + Selenium + reportes.": "Run the demo case from this screen and validate the API + Selenium + reports integration.",
    "Ambiente": "Environment", "Reportes": "Reports", "Ejecutar headless": "Run headless", "Ejecutar ahora": "Run now", "Listo para ejecutar.": "Ready to run.",
    "Marca blanca": "White label", "Personaliza nombre, logo, colores y datos comerciales de la plataforma.": "Customize name, logo, colors, and business information.",
    "Restaurar valores": "Restore defaults", "Nombre de la aplicación": "Application name", "Nombre comercial / empresa": "Business name / company", "Texto del logo": "Logo text", "Texto superior": "Top text", "Color principal": "Primary color", "Color sidebar": "Sidebar color", "Correo de soporte": "Support email", "Sitio web": "Website", "Tema visual": "Visual theme", "Idioma": "Language", "Zona horaria": "Time zone", "Navegador por defecto": "Default browser", "Ambiente por defecto": "Default environment", "Guardar configuración": "Save settings",
    "Preguntas frecuentes": "Frequently asked questions", "Acerca de": "About", "Usuarios": "Users", "Auditoría": "Audit", "Configuración": "Settings", "Perfil": "Profile", "Grabador": "Recorder", "Plantillas": "Templates"
  },
  es: {
    "Projects": "Proyectos", "Recorder": "Grabador", "Scheduler": "Scheduler", "Executions": "Ejecuciones", "Reports": "Reportes", "Templates": "Plantillas", "Profile": "Perfil", "Users": "Usuarios", "Audit": "Auditoría", "Settings": "Configuración", "FAQ": "Preguntas frecuentes", "About": "Acerca de",
    "Theme": "Tema", "Language": "Idioma", "Logout": "Salir", "View latest generated report": "Ver último reporte generado", "View executions": "Ver ejecuciones", "View details": "Ver detalle", "Delete": "Eliminar", "New project": "Nuevo proyecto", "Quick orchestrator": "Orquestador rápido", "Run now": "Ejecutar ahora"
  }
};

async function apiGet(path) {
  const response = await fetch(API + path);
  if (!response.ok) throw new Error(`GET ${path} failed`);
  return response.json();
}
async function apiPost(path, body) {
  const response = await fetch(API + path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!response.ok) { const text = await response.text(); throw new Error(text || `POST ${path} failed`); }
  return response.json();
}
async function apiPut(path, body) {
  const response = await fetch(API + path, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!response.ok) { const text = await response.text(); throw new Error(text || `PUT ${path} failed`); }
  return response.json();
}
async function apiDelete(path) {
  const response = await fetch(API + path, { method: "DELETE" });
  if (!response.ok) throw new Error(`DELETE ${path} failed`);
  return response.json();
}
function statusBadge(status) { const value = status || "UNKNOWN"; return `<span class="badge ${value}">${value}</span>`; }
function safe(value, fallback = "-") { return value === null || value === undefined || value === "" ? fallback : value; }
function seconds(value) { const n = Number(value || 0); return `${n.toFixed(2)} s`; }
function toast(message) { const el = document.getElementById("toast"); if (!el) return; el.textContent = message; el.classList.remove("hidden"); setTimeout(() => el.classList.add("hidden"), 4200); }
function showToast(message, type = 'info') { toast(message); }

function applyTheme(themeName) {
  const theme = THEME_OPTIONS[themeName] || THEME_OPTIONS["Corporate Light"];
  const root = document.documentElement;
  root.style.setProperty("--bg", theme.bg);
  root.style.setProperty("--surface", theme.surface);
  root.style.setProperty("--surface-2", theme.surface2);
  root.style.setProperty("--text", theme.text);
  root.style.setProperty("--muted", theme.muted);
  root.style.setProperty("--primary", theme.primary);
  root.style.setProperty("--primary-dark", theme.primary);
  root.style.setProperty("--sidebar-bg", theme.sidebar);
  root.style.setProperty("--border", theme.border);
  document.body.classList.toggle("dark", ["Corporate Dark", "Neon Tech", "Black Gold"].includes(themeName));
  localStorage.setItem("autotest_theme", themeName);
  const selector = document.getElementById("themeSelector");
  if (selector && selector.value !== themeName) selector.value = themeName;
}

function translateTextNodes(lang) {
  const map = PHRASE_TRANSLATIONS[lang] || {};
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      const parent = node.parentElement;
      if (!parent || ["SCRIPT", "STYLE", "TEXTAREA", "INPUT", "OPTION"].includes(parent.tagName)) return NodeFilter.FILTER_REJECT;
      const text = node.nodeValue.trim();
      return map[text] ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP;
    }
  });
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  nodes.forEach(node => { const original = node.nodeValue; const trimmed = original.trim(); node.nodeValue = original.replace(trimmed, map[trimmed]); });
}

function applyLanguage(langInput) {
  const lang = langInput || localStorage.getItem("autotest_language") || document.body.dataset.appLanguage || "es";
  const dict = I18N[lang] || I18N.es;
  document.documentElement.lang = lang;
  document.body.dataset.appLanguage = lang;
  localStorage.setItem("autotest_language", lang);
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) el.textContent = dict[key];
  });
  const selector = document.getElementById("languageSelector");
  if (selector && selector.value !== lang) selector.value = lang;
  translateTextNodes(lang);
}

async function persistUiPreference(partial) {
  try {
    const current = await apiGet("/api/settings");
    await apiPut("/api/settings", { ...current, ...partial, smtp_password: "" });
  } catch (error) {
    console.warn("No se pudo persistir preferencia global, se aplicó localmente.", error);
  }
}

function initThemeSelector() {
  const selector = document.getElementById("themeSelector");
  const serverTheme = document.body.dataset.currentTheme || "Corporate Light";
  const selected = localStorage.getItem("autotest_theme") || serverTheme;
  if (selector) {
    selector.innerHTML = Object.keys(THEME_OPTIONS).map(name => `<option value="${name}">${name}</option>`).join("");
    selector.value = selected;
    selector.addEventListener("change", async () => {
      applyTheme(selector.value);
      await persistUiPreference({ theme: selector.value });
      toast(`Tema aplicado: ${selector.value}`);
    });
  }
  applyTheme(selected);
}

function initLanguageSelector() {
  const selector = document.getElementById("languageSelector");
  const serverLang = document.body.dataset.appLanguage || "es";
  const selected = localStorage.getItem("autotest_language") || serverLang;
  if (selector) {
    selector.value = selected;
    selector.addEventListener("change", async () => {
      applyLanguage(selector.value);
      await persistUiPreference({ language: selector.value });
      toast(selector.value === "es" ? "Idioma aplicado: Español" : "Language applied: English");
    });
  }
  applyLanguage(selected);
}

window.applyTheme = applyTheme;
window.applyLanguage = applyLanguage;
window.THEME_OPTIONS = THEME_OPTIONS;

document.addEventListener("DOMContentLoaded", () => { initThemeSelector(); initLanguageSelector(); });
