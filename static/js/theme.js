/* Runs in <head> before styles and paint; shares the existing `theme` preference. */
(function () {
  let saved;
  try { saved = localStorage.getItem('theme'); } catch (_) {}
  const dark = saved === 'dark' || (saved !== 'light' && window.matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.classList.toggle('dark', dark);
})();
