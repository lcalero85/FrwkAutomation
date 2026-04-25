const changePasswordForm = document.getElementById('changePasswordForm');

async function secureFetch(url, options = {}) {
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
    throw new Error(data.detail || 'No se pudo completar la solicitud');
  }
  return response.json();
}

changePasswordForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(changePasswordForm);
  const payload = {
    current_password: formData.get('current_password'),
    new_password: formData.get('new_password'),
  };

  try {
    await secureFetch('/api/auth/change-password', { method: 'POST', body: JSON.stringify(payload) });
    toast('Contraseña actualizada correctamente');
    changePasswordForm.reset();
  } catch (error) {
    toast(error.message || 'No se pudo actualizar la contraseña', 'error');
  }
});
