// vite.config.js — Vite configuration for CodeTrace frontend
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
	plugins: [react()],
	server: {
		port: 5173,
		proxy: {
			// Proxy API requests to FastAPI backend
			"/api": "http://localhost:8000"
		}
	}
});
