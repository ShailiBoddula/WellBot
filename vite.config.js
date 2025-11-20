import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        timeout: 60000,
        proxyTimeout: 60000,
        rewrite: (path) => path.replace(/^\/auth/, '/auth')
      },
      '/chat': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        timeout: 30000,
        proxyTimeout: 30000,
        rewrite: (path) => path.replace(/^\/chat/, '/chat')
      },
      '/profile': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        timeout: 30000,
        proxyTimeout: 30000,
        rewrite: (path) => path.replace(/^\/profile/, '/profile')
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        timeout: 30000,
        proxyTimeout: 30000,
        rewrite: (path) => path.replace(/^\/health/, '/health')
      }
    }
  }
})
