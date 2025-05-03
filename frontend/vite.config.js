// NeonChat-main/frontend/vite.config.js
import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  // Setting root to static directory where index.html is located
  root: path.resolve(__dirname, 'static'),
  base: './', // Relative paths for assets
  build: {
    // Output directory relative to project root (NeonChat-main/frontend/dist)
    outDir: path.resolve(__dirname, 'dist'),
    emptyOutDir: true,
    rollupOptions: {
      input: {
        // Input HTML is now relative to the static directory
        main: path.resolve(__dirname, 'static', 'index.html'),
      },
    },
  },
  server: {
    port: 5173,
    // Proxy to backend on port 8001
    proxy: {
      '/api': 'http://localhost:8001',
      '/ws': { target: 'ws://localhost:8001', ws: true },
    },
  },
});
