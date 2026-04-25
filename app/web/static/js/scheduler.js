async function loadSchedulerJobs() {
  const tbody = document.getElementById("schedulerJobsTable");
  if (!tbody) return;
  tbody.innerHTML = `<tr><td colspan="7" class="muted">Cargando jobs...</td></tr>`;
  try {
    const jobs = await apiGet("/api/scheduler/jobs");
    if (!jobs.length) {
      tbody.innerHTML = `<tr><td colspan="7" class="muted">No hay jobs programados.</td></tr>`;
      return;
    }
    tbody.innerHTML = jobs.map(job => `
      <tr>
        <td>${job.id}</td>
        <td><strong>${safe(job.name)}</strong><br><span class="muted">${safe(job.description, "Sin descripción")}</span></td>
        <td>${safe(job.schedule_type)}</td>
        <td>${safe(job.browser)}</td>
        <td>${safe(job.next_run)}</td>
        <td>${job.is_active ? statusBadge("ACTIVE") : statusBadge("INACTIVE")}</td>
        <td class="table-actions">
          <button class="btn secondary" onclick="runJobNow(${job.id})">Ejecutar</button>
          <button class="btn ghost" onclick="deleteJob(${job.id})">Eliminar</button>
        </td>
      </tr>
    `).join("");
  } catch (error) {
    tbody.innerHTML = `<tr><td colspan="7" class="muted">Error cargando jobs.</td></tr>`;
    toast(error.message);
  }
}

async function runJobNow(id) {
  try {
    toast("Ejecutando job programado...");
    const result = await apiPost(`/api/scheduler/jobs/${id}/run-now`, {});
    toast(`Ejecución generada: ${result.execution_id} - ${result.status}`);
    await loadSchedulerJobs();
  } catch (error) {
    toast(error.message);
  }
}

async function deleteJob(id) {
  if (!confirm("¿Eliminar este job programado?")) return;
  try {
    await apiDelete(`/api/scheduler/jobs/${id}`);
    toast("Job eliminado");
    await loadSchedulerJobs();
  } catch (error) {
    toast(error.message);
  }
}

function initJobModal() {
  const modal = document.getElementById("jobModal");
  const open = document.getElementById("openJobModal");
  const close = document.getElementById("closeJobModal");
  if (open) open.addEventListener("click", () => modal.classList.remove("hidden"));
  if (close) close.addEventListener("click", () => modal.classList.add("hidden"));

  const form = document.getElementById("jobForm");
  if (form) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const data = Object.fromEntries(new FormData(form).entries());
      data.headless = form.elements.headless.checked;
      data.is_active = true;
      data.execution_type = "DEMO";
      try {
        await apiPost("/api/scheduler/jobs", data);
        modal.classList.add("hidden");
        form.reset();
        toast("Job creado correctamente");
        await loadSchedulerJobs();
      } catch (error) {
        toast(error.message);
      }
    });
  }
}

function initQuickRun() {
  const btn = document.getElementById("quickRunBtn");
  const status = document.getElementById("quickRunStatus");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    btn.disabled = true;
    status.textContent = "Ejecutando prueba demo. Puede tardar unos segundos...";
    try {
      const result = await apiPost("/api/executions/run-demo", {
        browser: document.getElementById("quickBrowser").value,
        headless: document.getElementById("quickHeadless").checked,
        environment: document.getElementById("quickEnvironment").value || "demo",
        test: "login_demo",
        report: document.getElementById("quickReport").value || "html,excel,pdf",
      });
      status.innerHTML = `Ejecución finalizada: ${statusBadge(result.status)} ID ${result.id}`;
      toast("Ejecución completada");
    } catch (error) {
      status.textContent = "Error ejecutando demo.";
      toast(error.message);
    } finally {
      btn.disabled = false;
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initJobModal();
  initQuickRun();
  loadSchedulerJobs();
});
