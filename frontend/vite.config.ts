import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The FastAPI backend serves both the catalogue API and the product images.
// Proxying keeps the frontend on one origin in development, so no CORS in the browser.
const backend = process.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: backend, changeOrigin: true },
      '/media': { target: backend, changeOrigin: true },
    },
  },
})
