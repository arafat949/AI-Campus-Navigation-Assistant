/**
 * App entry point: sidebar tab switching (including algorithm shortcut
 * buttons that jump to the route tab and pre-select an algorithm), and
 * initialisation of every feature module.
 */

function switchView(targetId) {
  document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
  document.getElementById(targetId).classList.add("active");

  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.target === targetId);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.addEventListener("click", () => {
      switchView(btn.dataset.target);
      // sidebar "Algorithms" shortcuts pre-select a radio on the route tab
      if (btn.dataset.algo) {
        const radio = document.querySelector(`input[name="algo"][value="${btn.dataset.algo}"]`);
        if (radio) radio.checked = true;
        document.querySelector('.nav-item[data-target="section-dashboard"]').classList.add("active");
        switchView("section-dashboard");
      }
    });
  });

  Auth.init();
  loadDashboardStats();
  initClock();
  initGlobalSearch();
  initLibraryShortcut();

  RouteTab.init();
  RouteViz.init();
  QuickAccess.init();
  ColoringTab.init();
  NQueensTab.init();
  GameTab.init();
  FuzzyTab.init();
  EmergencyExitTab.init();
  FinderTab.init();
  AssistantTab.init();
});
