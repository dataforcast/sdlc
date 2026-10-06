import path from 'node:path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// API_BASE_URL (non-VITE_-prefixed) is read here via process.env, not import.meta.env.
export default defineConfig({
  plugins: [react()],
  envDir: path.resolve(__dirname, '..'),
  server: {
    port: Number(process.env.FRONTEND_PORT ?? 5173),
    proxy: {
      '/backend': {
        target: process.env.API_BASE_URL ?? 'http://127.0.0.1:8010',
        changeOrigin: true,
        // No path rewrite: the backend already serves routes under /backend.
      },
    },
  },
});
