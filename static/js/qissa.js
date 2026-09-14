function toggleDark() {
  document.documentElement.classList.toggle("dark");
  localStorage.setItem(
    "theme",
    document.documentElement.classList.contains("dark") ? "dark" : "light"
  );
}

function toggleMobileMenu() {
  const menu = document.getElementById("mobile-menu");
  if (menu) menu.classList.toggle("hidden");
}

function showPaywall() {
  const modal = document.getElementById("paywall-modal");
  if (!modal) return;
  modal.classList.remove("hidden");
  document.body.style.overflow = "hidden";
}

function hidePaywall() {
  const modal = document.getElementById("paywall-modal");
  if (!modal) return;
  modal.classList.add("hidden");
  document.body.style.overflow = "";
}

function copyPhone(btnId) {
  const btn = document.getElementById(btnId || "phone-btn");
  if (!btn) return;
  const value = btn.dataset.phone || "0621932919";
  const original = btn.textContent;
  navigator.clipboard.writeText(value).catch(() => {});
  btn.textContent = "Imenakiliwa!";
  setTimeout(() => {
    btn.textContent = original;
  }, 2000);
}

function toggleFaq(btn) {
  const content = btn.nextElementSibling;
  const icon = btn.querySelector("svg");
  content.classList.toggle("hidden");
  if (icon) icon.style.transform = content.classList.contains("hidden") ? "" : "rotate(180deg)";
}

(function () {
  const saved = localStorage.getItem("theme");
  if (saved === "dark" || (!saved && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
    document.documentElement.classList.add("dark");
  }
})();
