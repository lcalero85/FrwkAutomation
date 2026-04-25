const auditTableBody = document.getElementById('auditTableBody');
const refreshAudit = document.getElementById('refreshAudit');

function auditBadge(status) {
  const cls = status === 'SUCCESS' ? 'success' : status === 'FAILED' ? 'danger' : 'info';
  return `<span class="badge ${cls}">${status || 'UNKNOWN'}</span>`;
}

async function loadAuditLogs() {
  const response = await fetch('/api/audit-logs?limit=150');
  if (response.status === 401) {
    window.location.href = '/login';
    return;
  }
  if (response.status === 403) {
    auditTableBody.innerHTML = '<tr><td colspan="8">No tienes permiso para ver auditoría.</td></tr>';
    return;
  }
  if (!response.ok) throw new Error('No se pudo cargar la auditoría');
  const logs = await response.json();
  auditTableBody.innerHTML = logs.map((log) => `
    <tr>
      <td>${log.id}</td>
      <td>${log.created_at ? new Date(log.created_at).toLocaleString() : '-'}</td>
      <td>${log.username || '-'}</td>
      <td>${log.module}</td>
      <td>${log.action}</td>
      <td>${auditBadge(log.status)}</td>
      <td>${log.ip_address || '-'}</td>
      <td>${log.description || '-'}</td>
    </tr>
  `).join('') || '<tr><td colspan="8">No hay eventos de auditoría.</td></tr>';
}

refreshAudit?.addEventListener('click', () => loadAuditLogs().catch((error) => toast(error.message, 'error')));
loadAuditLogs().catch((error) => toast(error.message, 'error'));
