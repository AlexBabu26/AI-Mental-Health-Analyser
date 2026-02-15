const API_BASE = "/api/v1";

/* ─── Token Storage ─── */
function tokenStore() {
  return localStorage.getItem("remember_me") === "1" ? localStorage : sessionStorage;
}
function setRememberMe(enabled) {
  localStorage.setItem("remember_me", enabled ? "1" : "0");
}
function getAccess()  { return tokenStore().getItem("access_token"); }
function getRefresh() { return tokenStore().getItem("refresh_token"); }
function setTokens(access, refresh) {
  tokenStore().setItem("access_token", access);
  tokenStore().setItem("refresh_token", refresh);
}
function clearTokens() {
  localStorage.removeItem("access_token");  localStorage.removeItem("refresh_token");
  sessionStorage.removeItem("access_token"); sessionStorage.removeItem("refresh_token");
}

/* ─── Toast ─── */
function showToast(title, message, kind, timeoutMs) {
  kind = kind || "warn"; timeoutMs = timeoutMs || 3500;
  var wrap = document.getElementById("toastWrap"); if (!wrap) return;
  var div = document.createElement("div"); div.className = "toast";
  div.innerHTML = '<div class="title">' + esc(title) + '</div><div class="muted text-sm">' + esc(message) + '</div>';
  wrap.appendChild(div);
  setTimeout(function(){ try { wrap.removeChild(div); } catch(e){} }, timeoutMs);
}

/* ─── Banner ─── */
function setBanner(text, show) {
  var banner = document.getElementById("globalBanner"); if (!banner) return;
  banner.textContent = text || "";
  if (show) banner.classList.remove("hidden"); else banner.classList.add("hidden");
}

/* ─── Escape HTML ─── */
function esc(str) {
  return String(str).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#039;");
}
var escapeHtml = esc;

/* ─── API Fetch with auto-refresh ─── */
async function apiFetch(path, options) {
  options = options || {};
  var headers = options.headers || {};
  var token = getAccess();
  if (token) headers["Authorization"] = "Bearer " + token;
  if (!headers["Content-Type"]) headers["Content-Type"] = "application/json";
  options.headers = headers;
  try {
    var res = await fetch(API_BASE + path, options);
    if (res.status === 401 && getRefresh()) {
      var ok = await refreshToken();
      if (ok) { headers["Authorization"] = "Bearer " + getAccess(); res = await fetch(API_BASE + path, options); }
      else { clearTokens(); showToast("Session expired","Please login again.","warn"); window.location.href = "/login/"; return res; }
    }
    return res;
  } catch(e) { showToast("Network error","Unable to reach server.","error",5000); throw e; }
}

async function refreshToken() {
  var refresh = getRefresh(); if (!refresh) return false;
  var res = await fetch(API_BASE + "/auth/jwt/refresh/", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ refresh: refresh }) });
  if (!res.ok) return false;
  var data = await res.json();
  tokenStore().setItem("access_token", data.access);
  return true;
}

/* ─── Auth helpers ─── */
function requireAuthOrRedirect() { if (!getAccess()) window.location.href = "/login/"; }

function bindLogout() {
  var btn = document.getElementById("logoutBtn"); if (!btn) return;
  btn.addEventListener("click", function() {
    clearTokens(); showToast("Logged out","You have been logged out.","ok"); window.location.href = "/login/";
  });
}

/* ─── Form helpers ─── */
function validateEmail(email) { return email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email); }

function setBtnLoading(btn, isLoading, label) {
  if (!btn) return;
  btn.disabled = isLoading;
  btn.innerHTML = isLoading ? '<span class="spinner"></span>Loading...' : label;
}

function togglePass(id) {
  var el = document.getElementById(id); if (!el) return;
  el.type = el.type === "password" ? "text" : "password";
}

/* ─── Smooth Scroll (respects reduced motion) ─── */
function initSmoothScroll() {
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.querySelectorAll('a[href^="#"]').forEach(function(a) {
    var href = a.getAttribute("href"); if (href === "#" || !href) return;
    var target = document.querySelector(href); if (!target) return;
    a.addEventListener("click", function(e) { e.preventDefault(); target.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" }); });
  });
}

/* ─── Program Filter ─── */
function initProgramFilter() {
  var pills = document.querySelectorAll(".filter-pill[data-filter]");
  var grid = document.getElementById("programsGrid");
  if (!pills.length || !grid) return;
  var cards = grid.querySelectorAll(".program-card[data-category]");
  pills.forEach(function(pill) {
    pill.addEventListener("click", function() {
      var filter = pill.getAttribute("data-filter");
      pills.forEach(function(p) { p.classList.toggle("active", p === pill); p.setAttribute("aria-pressed", p === pill ? "true" : "false"); });
      cards.forEach(function(card) { var show = filter === "all" || card.getAttribute("data-category") === filter; card.style.display = show ? "" : "none"; });
    });
  });
}

/* ─── Init ─── */
document.addEventListener("DOMContentLoaded", function() {
  bindLogout();
  initSmoothScroll();
  initProgramFilter();
});
