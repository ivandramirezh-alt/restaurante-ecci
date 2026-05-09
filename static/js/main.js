// main.js — El Buen Sabor

// Agregar fila de plato dinamicamente
function agregarPlato() {
  const lista = document.getElementById('platos-lista');
  const opciones = document.getElementById('plato-template').innerHTML;
  const div = document.createElement('div');
  div.className = 'plato-row';
  div.innerHTML = `
    <select name="id_plato[]" required>${opciones}</select>
    <input type="number" name="cantidad[]" value="1" min="1" required>
    <button type="button" class="btn-remove" onclick="this.parentElement.remove()">✕</button>
  `;
  lista.appendChild(div);
}

// Confirmar acciones importantes
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', e => {
    if (!confirm(el.dataset.confirm)) e.preventDefault();
  });
});

// Auto-hide alerts after 4 seconds
document.querySelectorAll('.alert').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .5s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 500);
  }, 4000);
});
