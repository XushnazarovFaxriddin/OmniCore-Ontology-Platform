import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const serverPort = Number(process.env.VITE_PORT || 3000)
const proxyTarget = process.env.VITE_PROXY_TARGET || 'http://localhost:18000'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // Allow external connections (needed for remote access)
    port: serverPort,
    strictPort: true,
    proxy: {
      '/api': {
        target: proxyTarget,
        changeOrigin: true,
        secure: false,
      },
    },
    cors: true,
  },
  preview: {
    host: '0.0.0.0',
    port: serverPort,
    cors: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
