import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const backendPort = env.VITE_BACKEND_PORT || "8001";
  const backendUrl = env.VITE_API_URL || `http://localhost:${backendPort}`;

  return {
    plugins: [react()],

    server: {
      port: 5173,
      // Proxy /api requests to the FastAPI backend in development.
      // In production (Docker), the backend serves the frontend directly.
      proxy: {
        "/api": {
          target: backendUrl,
          changeOrigin: true,
          // Uncomment below if backend uses self-signed HTTPS:
          // secure: false,
        },
      },
    },

    build: {
      // Output to dist/ (expected by Dockerfile COPY command)
      outDir: "dist",
      // Generate source maps for production debugging
      sourcemap: false,
      // Chunk size warning threshold (KB)
      chunkSizeWarningLimit: 800,
      rollupOptions: {
        output: {
          // Split vendor code from app code for better caching
          manualChunks: {
            react: ["react", "react-dom"],
          },
        },
      },
    },

    // Define global constants for the app
    define: {
      __APP_VERSION__: JSON.stringify("2.0.0"),
    },
  };
});
