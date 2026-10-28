/* One theme preference, shared by public pages, Studio, and reader controls. */
function savedPreference(key) { try { return localStorage.getItem(key); } catch (_) { return null; } }
function savePreference(key, value) { try { localStorage.setItem(key, value); } catch (_) {} }
function syncThemeControls() {
  const dark = document.documentElement.classList.contains('dark');
  document.querySelectorAll('[data-theme-toggle]').forEach(button => button.setAttribute('aria-pressed', String(dark)));
  updateChartTheme();
}
function toggleDark() {
  document.documentElement.classList.toggle('dark');
  savePreference('theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
  syncThemeControls();
}
function toggleMobileMenu() {
  const menu = document.getElementById('mobile-menu');
  if (!menu) return;
  const open = menu.classList.toggle('hidden') === false;
  document.getElementById('mobile-menu-toggle')?.setAttribute('aria-expanded', String(open));
}
let paywallTrigger;
function showPaywall() {
  const modal = document.getElementById('paywall-modal');
  if (!modal) return;
  paywallTrigger = document.activeElement;
  modal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
  modal.querySelector('a, button')?.focus();
}
function hidePaywall() {
  const modal = document.getElementById('paywall-modal');
  if (!modal) return;
  modal.classList.add('hidden');
  document.body.style.overflow = '';
  paywallTrigger?.focus();
}
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') {
    hidePaywall();
    document.getElementById('mobile-menu')?.classList.add('hidden');
    document.getElementById('mobile-menu-toggle')?.setAttribute('aria-expanded', 'false');
  }
  const modal = document.getElementById('paywall-modal');
  if (event.key !== 'Tab' || !modal || modal.classList.contains('hidden')) return;
  const controls = [...modal.querySelectorAll('a[href], button:not([disabled])')];
  const first = controls[0], last = controls[controls.length - 1];
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
});
function copyPhone(btnId) {
  const button = document.getElementById(btnId || 'phone-btn');
  if (!button || !navigator.clipboard) return;
  navigator.clipboard.writeText(button.dataset.phone || '0621932919').then(() => {
    const original = button.textContent;
    button.textContent = 'Imenakiliwa!';
    setTimeout(() => { button.textContent = original; }, 2000);
  }).catch(() => {});
}
function toggleFaq(button) {
  const content = button.nextElementSibling;
  content.classList.toggle('hidden');
  button.setAttribute('aria-expanded', String(!content.classList.contains('hidden')));
}
function applyReaderSize(size, persist) {
  const value = Math.max(16, Math.min(24, Number(size)));
  if (!Number.isFinite(value)) return;
  document.documentElement.style.setProperty('--reader-font-size', value + 'px');
  document.querySelectorAll('[data-reader-size-output]').forEach(output => { output.textContent = value + 'px'; });
  document.querySelectorAll('[data-reader-size]').forEach(button => {
    button.disabled = Number(button.dataset.readerSize) < 0 ? value <= 16 : value >= 24;
  });
  if (persist) savePreference('reader-font-size', String(value));
}
const readerSize = Number(savedPreference('reader-font-size'));
if (readerSize >= 16 && readerSize <= 24) applyReaderSize(readerSize, false);
else document.querySelectorAll('[data-reader-size-output]').forEach(output => {
  output.textContent = window.matchMedia('(max-width:700px)').matches ? '18px' : '19px';
});
document.querySelectorAll('[data-reader-size]').forEach(button => button.addEventListener('click', () => {
  const content = document.getElementById('reading-content');
  if (content) applyReaderSize(parseFloat(getComputedStyle(content).fontSize) + Number(button.dataset.readerSize), true);
}));
window.QissaPalette = {};
function updateChartTheme() {
  const css = getComputedStyle(document.documentElement);
  Object.assign(window.QissaPalette, {
    accent: css.getPropertyValue('--q-accent').trim(),
    soft: css.getPropertyValue('--q-accent-soft').trim(),
    series: [css.getPropertyValue('--q-accent').trim(), '#8A8578', '#62757A', '#9B8B78', '#7C877D', '#A69788'],
  });
  if (!window.Chart) return;
  Chart.defaults.color = css.getPropertyValue('--q-muted').trim();
  Chart.defaults.borderColor = css.getPropertyValue('--q-border').trim();
  Chart.defaults.font.family = 'DM Sans, sans-serif';
  Object.values(Chart.instances).forEach(chart => {
    chart.options.color = Chart.defaults.color;
    Object.values(chart.options.scales || {}).forEach(scale => {
      if (scale.ticks) scale.ticks.color = Chart.defaults.color;
      if (scale.grid) scale.grid.color = Chart.defaults.borderColor;
    });
    chart.data.datasets.forEach(dataset => {
      dataset.borderColor = QissaPalette.accent;
      dataset.backgroundColor = chart.config.type === 'doughnut' ? QissaPalette.series : (chart.config.type === 'line' ? QissaPalette.soft : QissaPalette.accent);
    });
    chart.update('none');
  });
}
syncThemeControls();
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
  if (['light', 'dark'].includes(savedPreference('theme'))) return;
  document.documentElement.classList.toggle('dark', event.matches);
  syncThemeControls();
});
window.addEventListener('storage', event => {
  if (event.key !== 'theme') return;
  document.documentElement.classList.toggle('dark', event.newValue === 'dark' || (!event.newValue && matchMedia('(prefers-color-scheme: dark)').matches));
  syncThemeControls();
});
