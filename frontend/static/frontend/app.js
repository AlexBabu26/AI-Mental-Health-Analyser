const API_BASE = "/api/v1";

/**
 * Remember-me strategy:
 * - If remember_me=1 => tokens stored in localStorage
 * - Else => tokens stored in sessionStorage
 */
function tokenStore() {
  const remember = localStorage.getItem("remember_me") === "1";
  return remember ? localStorage : sessionStorage;
}

function setRememberMe(enabled) {
  localStorage.setItem("remember_me", enabled ? "1" : "0");
}

function getAccess() {
  return tokenStore().getItem("access_token");
}
function getRefresh() {
  return tokenStore().getItem("refresh_token");
}
function setTokens(access, refresh) {
  tokenStore().setItem("access_token", access);
  tokenStore().setItem("refresh_token", refresh);
}
function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  sessionStorage.removeItem("access_token");
  sessionStorage.removeItem("refresh_token");
}

function showToast(title, message, kind = "warn", timeoutMs = 3500) {
  const wrap = document.getElementById("toastWrap");
  if (!wrap) return;

  const div = document.createElement("div");
  div.className = `toast ${kind}`;
  div.innerHTML = `<div class="title">${escapeHtml(title)}</div><div class="muted">${escapeHtml(message)}</div>`;
  wrap.appendChild(div);

  setTimeout(() => {
    try { wrap.removeChild(div); } catch {}
  }, timeoutMs);
}

function setBanner(text, show = true) {
  const banner = document.getElementById("globalBanner");
  if (!banner) return;
  banner.textContent = text || "";
  banner.classList.toggle("hidden", !show);
}

function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function apiFetch(path, options = {}) {
  const headers = options.headers || {};
  const token = getAccess();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  headers["Content-Type"] = headers["Content-Type"] || "application/json";
  options.headers = headers;

  try {
    let res = await fetch(`${API_BASE}${path}`, options);

    // Refresh once on 401
    if (res.status === 401 && getRefresh()) {
      const refreshed = await refreshToken();
      if (refreshed) {
        headers["Authorization"] = `Bearer ${getAccess()}`;
        res = await fetch(`${API_BASE}${path}`, options);
      } else {
        clearTokens();
        showToast("Session expired", "Please login again.", "warn");
        window.location.href = "/";
        return res;
      }
    }
    return res;
  } catch (e) {
    showToast("Network error", "Unable to reach server. Check connection.", "error", 5000);
    throw e;
  }
}

async function refreshToken() {
  const refresh = getRefresh();
  if (!refresh) return false;

  const res = await fetch(`${API_BASE}/auth/jwt/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh })
  });

  if (!res.ok) return false;
  const data = await res.json();
  tokenStore().setItem("access_token", data.access);
  return true;
}

function requireAuthOrRedirect() {
  if (!getAccess()) window.location.href = "/";
}

function bindLogout() {
  const btn = document.getElementById("logoutBtn");
  if (!btn) return;
  btn.addEventListener("click", () => {
    clearTokens();
    showToast("Logged out", "You have been logged out.", "ok");
    window.location.href = "/";
  });
}

function validateEmail(email) {
  if (!email) return false;
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

function setBtnLoading(btn, isLoading, labelWhenNotLoading) {
  if (!btn) return;
  btn.disabled = isLoading;
  btn.innerHTML = isLoading
    ? `<span class="spinner"></span>Loading...`
    : labelWhenNotLoading;
}

document.addEventListener("DOMContentLoaded", bindLogout);
