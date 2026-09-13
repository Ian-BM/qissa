(function () {
  // Mobile nav drawer
  const hamburger = document.getElementById("hamburger");
  const drawer = document.getElementById("navDrawer");
  const overlay = document.getElementById("navDrawerOverlay");
  const drawerClose = document.getElementById("navDrawerClose");

  function openDrawer() {
    if (drawer) drawer.classList.add("open");
    if (overlay) overlay.classList.add("open");
  }
  function closeDrawer() {
    if (drawer) drawer.classList.remove("open");
    if (overlay) overlay.classList.remove("open");
  }
  if (hamburger) hamburger.addEventListener("click", openDrawer);
  if (drawerClose) drawerClose.addEventListener("click", closeDrawer);
  if (overlay) overlay.addEventListener("click", closeDrawer);

  // Copy-to-clipboard (phone numbers, share links)
  document.querySelectorAll("[data-copy]").forEach((el) => {
    el.addEventListener("click", async () => {
      const value = el.dataset.copy;
      const originalText = el.textContent;
      try {
        await navigator.clipboard.writeText(value);
        el.textContent = "Imenakiliwa!";
      } catch (e) {
        window.prompt("Nakili namba hii:", value);
      }
      setTimeout(() => { el.textContent = originalText; }, 1800);
    });
  });

  // FAQ accordion
  document.querySelectorAll(".faq-question").forEach((btn) => {
    btn.addEventListener("click", () => {
      const item = btn.closest(".faq-item");
      if (item) item.classList.toggle("open");
    });
  });
})();
