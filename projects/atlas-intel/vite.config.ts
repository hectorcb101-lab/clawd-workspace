import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    allowedHosts: true,
    proxy: {
      '/api/data': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/api/webcam': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/data': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
  build: {
    target: 'es2022',
    rollupOptions: {
      output: {
        manualChunks: {
          'globe': ['globe.gl', 'three'],
          'map2d': ['deck.gl', 'maplibre-gl'],
          'd3': ['d3'],
        },
      },
    },
  },
  optimizeDeps: {
    include: ['globe.gl', 'three', 'd3', 'dompurify', 'marked'],
  },
});
