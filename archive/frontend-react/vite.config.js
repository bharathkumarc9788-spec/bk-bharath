import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Backend this frontend talks to. Our Django server runs on 8002 in this
// workspace (8000/8001 are used by other projects on this machine).
const backend = process.env.BACKEND_URL || 'http://127.0.0.1:8002'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': backend,
      '/media': backend,
      '/admin': backend,
      '/static': backend,
    },
  },
})