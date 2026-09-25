document.querySelectorAll('.theme-toggle').forEach(button => button.addEventListener('click', () => {
  const dark = document.documentElement.classList.toggle('dark');
  try { localStorage.setItem('gestao-theme', dark ? 'dark' : 'light'); } catch (_) {}
}));
const toggle = document.getElementById('menu-toggle');
if (toggle) toggle.addEventListener('click', () => {
  const opened = document.getElementById('sidebar').classList.toggle('open');
  toggle.setAttribute('aria-expanded', String(opened));
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && toggle) {
    document.getElementById('sidebar').classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
  }
});
