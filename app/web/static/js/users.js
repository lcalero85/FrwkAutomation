const usersTableBody = document.getElementById('usersTableBody');
const rolesList = document.getElementById('rolesList');
const userModal = document.getElementById('userModal');
const openUserModal = document.getElementById('openUserModal');
const userForm = document.getElementById('userForm');
const roleSelect = document.getElementById('roleSelect');

function openModal() { userModal.classList.remove('hidden'); }
function closeModal() { userModal.classList.add('hidden'); userForm.reset(); }

document.querySelectorAll('[data-close-modal]').forEach((el) => el.addEventListener('click', closeModal));
openUserModal?.addEventListener('click', openModal);

async function apiFetch(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (response.status === 401) {
    window.location.href = '/login';
    return null;
  }
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || 'Error en la solicitud');
  }
  return response.json();
}

async function loadRoles() {
  const roles = await apiFetch('/api/roles');
  if (!roles) return;
  rolesList.innerHTML = roles.map((role) => `
    <div class="list-item">
      <strong>${role.name}</strong>
      <span>${role.description || 'Sin descripción'}</span>
    </div>
  `).join('');

  roleSelect.innerHTML = roles.map((role) => `<option value="${role.id}">${role.name}</option>`).join('');
}

async function loadUsers() {
  const users = await apiFetch('/api/users');
  if (!users) return;
  usersTableBody.innerHTML = users.map((user) => `
    <tr>
      <td>${user.id}</td>
      <td>${user.full_name}</td>
      <td>${user.username}</td>
      <td>${user.email}</td>
      <td><span class="badge info">${user.role || 'Sin rol'}</span></td>
      <td><span class="badge ${user.is_active ? 'success' : 'danger'}">${user.is_active ? 'Activo' : 'Inactivo'}</span></td>
    </tr>
  `).join('') || '<tr><td colspan="6">No hay usuarios registrados.</td></tr>';
}

userForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(userForm);
  const payload = {
    full_name: formData.get('full_name'),
    username: formData.get('username'),
    email: formData.get('email'),
    password: formData.get('password'),
    role_id: Number(formData.get('role_id')) || null,
    is_active: formData.get('is_active') === 'on',
  };

  try {
    await apiFetch('/api/users', { method: 'POST', body: JSON.stringify(payload) });
    toast('Usuario creado correctamente');
    closeModal();
    await loadUsers();
  } catch (error) {
    toast(error.message || 'No se pudo crear el usuario', 'error');
  }
});

loadRoles().then(loadUsers).catch((error) => toast(error.message || 'Error cargando usuarios', 'error'));
