// src/api/index.js — Axios instance for CodeTrace API
// Points to FastAPI backend at http://localhost:8000

import axios from "axios";

// Create the shared Axios instance.
// NOTE: Do NOT set a default Content-Type header here.
// - For JSON requests Axios sets it to 'application/json' automatically.
// - For file uploads (POST /api/analyze) Axios must set 'multipart/form-data'
//   automatically when a FormData object is passed — overriding it globally
//   would break file uploads.
const api = axios.create({
  baseURL: "http://localhost:8000",
  withCredentials: false, // Set to true when cookie-based auth is added
});

// ── Response interceptor ───────────────────────────────────────────────────
// Centralized error handling — logs errors and re-throws for the caller.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail || error.message || "Unknown error";
    console.error("[API Error]", message);
    return Promise.reject(error);
  }
);

export default api;
