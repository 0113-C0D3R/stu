document.addEventListener("DOMContentLoaded", () => {
  const html      = document.documentElement;
  const btn       = document.getElementById("themeToggle");
  const icon      = document.getElementById("themeIcon");
  const saved     = localStorage.getItem("theme") || "light";

  applyTheme(saved);

  btn.addEventListener("click", () => {
    const next = html.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
    applyTheme(next);
    localStorage.setItem("theme", next);
  });

  function applyTheme(theme) {
    html.setAttribute("data-bs-theme", theme);
    icon.className = theme === "dark" ? "fas fa-sun fa-lg" : "fas fa-moon fa-lg";
  }
});
