const API = "";

async function apiGet(path) {
  const response = await fetch(API + path);
  if (!response.ok) throw new Error(`GET ${path} failed`);
  return response.json();
}

async function apiPost(path, body) {
  const response = await fetch(API + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `POST ${path} failed`);
  }
  return response.json();
}

async function apiDelete(path) {
  const response = await fetch(API + path, { method: "DELETE" });
  if (!response.ok) throw new Error(`DELETE ${path} failed`);
  return response.json();
}

function statusBadge(status) {
  const value = status || "UNKNOWN";
  return `<span class="badge ${value}">${value}</span>`;
}

function safe(value, fallback = "-") {
  return value === null || value === undefined || value === "" ? fallback : value;
}

function seconds(value) {
  const n = Number(value || 0);
  return `${n.toFixed(2)} s`;
}

function toast(message) {
  const el = document.getElementById("toast");
  if (!el) return;
  el.textContent = message;
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 4200);
}

function initTheme() {
  const stored = localStorage.getItem("autotest_theme") || "light";
  document.body.classList.toggle("dark", stored === "dark");
  const btn = document.getElementById("themeToggle");
  if (btn) {
    btn.addEventListener("click", () => {
      const isDark = document.body.classList.toggle("dark");
      localStorage.setItem("autotest_theme", isDark ? "dark" : "light");
    });
  }
}

document.addEventListener("DOMContentLoaded", initTheme);

function showToast(message, type = 'info') {
  toast(message);
}
