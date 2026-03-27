import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    assetsDir: 'static'
  },
  server: {
    port: 5173,
    proxy: {
      '/start-campaign': 'http://127.0.0.1:8000',
      '/submit-answer': 'http://127.0.0.1:8000',
      '/status': 'http://127.0.0.1:8000',
      '/dev-start': 'http://127.0.0.1:8000',
      '/render-html': 'http://127.0.0.1:8000',
      '/render-single': 'http://127.0.0.1:8000',
      '/render-status': 'http://127.0.0.1:8000',
      '/export-pack': 'http://127.0.0.1:8000',
      '/export-global': 'http://127.0.0.1:8000',
      '/preview-render': 'http://127.0.0.1:8000',
      '/upload-image': 'http://127.0.0.1:8000',
      '/transcreate-preview': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
      '/generated': 'http://127.0.0.1:8000',
      '/assets': 'http://127.0.0.1:8000',
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  }
})
