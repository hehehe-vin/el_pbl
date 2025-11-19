// frontend/auth.js

// Base API URL — works locally and on Google App Engine.
// Example: http://localhost:8080/api  OR  https://your-app-url/api
const API_BASE = window.location.origin.replace(/\/$/, "") + "/api";


// =====================================
// AUTH STORAGE HELPERS (localStorage)
// =====================================

function saveAuth(auth) {
  // auth = { token, email, role, name }
  localStorage.setItem("auth", JSON.stringify(auth));
}

function getAuth() {
  const raw = localStorage.getItem("auth");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function clearAuth() {
  localStorage.removeItem("auth");
}


// =====================================
// GENERIC API WRAPPER
// Automatically attaches JWT + headers
// =====================================

async function apiFetch(path, options = {}) {
  const auth = getAuth();

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  // attach JWT if available
  if (auth && auth.token) {
    headers["Authorization"] = "Bearer " + auth.token;
  }

  // send request
  const res = await fetch(API_BASE + path, {
    ...options,
    headers
  });

  return res;
}
