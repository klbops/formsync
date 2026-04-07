import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true, // Essencial para rodar no Docker e acessar pelo IP do Proxmox
    port: 5173,
    watch: {
      usePolling: true // Garante que o hot-reload funcione perfeitamente no Docker
    }
  }
})
