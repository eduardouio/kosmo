import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    // Directorio de salida principal para todos los assets generados por Vite
    outDir: '../src/static/js/app', 
    emptyOutDir: false, // Para no borrar otros archivos en outDir si los hubiera
    rollupOptions: {
      output: {
        entryFileNames: 'app-order.js',
        // Si se generan chunks (divisiones de código), también usarán este prefijo
        chunkFileNames: 'app-order.[hash].js', 
        assetFileNames: (assetInfo) => {
          // Para los archivos CSS, nombrarlos específicamente
          if (assetInfo.name && assetInfo.name.endsWith('.css')) {
            return 'app-orders.css'; // Se generará como app-orders.css en outDir
          }
          // Para otros assets (imágenes, fuentes, etc.)
          return 'assets/app-order.[name]-[hash].[ext]';
        },
        // Intentar generar un solo archivo JS si es posible (deshabilitando chunks manuales)
        manualChunks: undefined 
      }
    }
  }
})