const Auth = (() => {
  function initials(name) {
    return name.trim().split(/\s+/).slice(0, 2).map((w) => w[0].toUpperCase()).join("");
  }

  function showAuthScreen() {
    document.getElementById("auth-screen").style.display = "flex";
    document.getElementById("app-shell").style.display = "none";
  }

  function showApp(user) {
    document.getElementById("auth-screen").style.display = "none";
    document.getElementById("app-shell").style.display = "flex";
    document.getElementById("profile-avatar").textContent = initials(user.name);
    document.getElementById("profile-name").textContent = user.name;
  }

  function showError(msg) {
    const el = document.getElementById("auth-error");
    el.textContent = msg;
    el.style.display = "block";
  }
  function clearError() {
    document.getElementById("auth-error").style.display = "none";
  }

  function setMode(mode) {
    clearError();
    document.querySelectorAll(".auth-tab").forEach((t) => t.classList.toggle("active", t.dataset.mode === mode));
    document.getElementById("login-form").style.display = mode === "login" ? "block" : "none";
    document.getElementById("signup-form").style.display = mode === "signup" ? "block" : "none";
    document.getElementById("auth-title").textContent =
      mode === "login" ? "Log in to your account" : "Create your account";
  }

  function validate(fields) {
    for (const [label, value] of fields) {
      if (!value || !value.trim()) {
        showError(label + " is required.");
        return false;
      }
    }
    return true;
  }

  async function postJSON(url, body) {
    let res;
    try {
      res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
    } catch (networkErr) {
      throw new Error("Could not reach the server. Is app.py still running?");
    }

    let data;
    try {
      data = await res.json();
    } catch (parseErr) {
      throw new Error("Server returned an unexpected response (status " + res.status + ").");
    }

    if (!res.ok) {
      throw new Error(data.error || "Request failed (status " + res.status + ").");
    }
    return data;
  }

  async function handleLogin(e) {
    e.preventDefault();
    clearError();
    const email = document.getElementById("login-email-input").value;
    const password = document.getElementById("login-password-input").value;
    if (!validate([["Email", email], ["Password", password]])) return;

    const btn = document.getElementById("login-submit-btn");
    btn.disabled = true;
    btn.textContent = "Logging in...";
    try {
      const data = await postJSON("/api/auth/login", { email: email.trim(), password: password });
      showApp(data);
    } catch (err) {
      showError(err.message);
    } finally {
      btn.disabled = false;
      btn.textContent = "Log In";
    }
  }

  async function handleSignup(e) {
    e.preventDefault();
    clearError();
    const name = document.getElementById("signup-name-input").value;
    const email = document.getElementById("signup-email-input").value;
    const password = document.getElementById("signup-password-input").value;
    if (!validate([["Full name", name], ["Email", email], ["Password", password]])) return;
    if (password.length < 6) { showError("Password must be at least 6 characters."); return; }

    const btn = document.getElementById("signup-submit-btn");
    btn.disabled = true;
    btn.textContent = "Creating account...";
    try {
      const data = await postJSON("/api/auth/signup", { name: name.trim(), email: email.trim(), password: password });
      showApp(data);
    } catch (err) {
      showError(err.message);
    } finally {
      btn.disabled = false;
      btn.textContent = "Create Account";
    }
  }

  function toggleDropdown() { document.getElementById("profile-dropdown").classList.toggle("open"); }
  function closeDropdown() { document.getElementById("profile-dropdown").classList.remove("open"); }

  async function handleLogout() {
    try {
      await fetch("/api/auth/logout", { method: "POST" });
    } catch (err) {
      console.warn("Logout request failed, clearing UI anyway:", err);
    }
    closeDropdown();
    document.getElementById("login-form").reset();
    document.getElementById("signup-form").reset();
    setMode("login");
    showAuthScreen();
  }

  async function init() {
    document.querySelectorAll(".auth-tab").forEach((tab) => {
      tab.addEventListener("click", () => setMode(tab.dataset.mode));
    });
    document.getElementById("login-form").addEventListener("submit", handleLogin);
    document.getElementById("signup-form").addEventListener("submit", handleSignup);
    document.getElementById("profile-btn").addEventListener("click", (e) => {
      e.stopPropagation();
      toggleDropdown();
    });
    document.getElementById("logout-btn").addEventListener("click", handleLogout);
    document.addEventListener("click", closeDropdown);

    try {
      const res = await fetch("/api/auth/me");
      const data = await res.json();
      if (data.user) {
        showApp(data.user);
      } else {
        showAuthScreen();
      }
    } catch (err) {
      console.error("Could not check login status:", err);
      showAuthScreen();
      showError("Could not reach the server to check login status. Is app.py running?");
    }
  }

  return { init: init };
})();