import path from 'node:path'
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { heyApiPlugin } from '@hey-api/vite-plugin';



export default defineConfig({
  server: {
    port: 5173,
    host: true,
    open: true,
    allowedHosts: ["proxy-fisso.internal.matteosillitti.it"],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        ws: true,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (_proxyReq, req, _res) => {
            console.log('Sending Request to the Target:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
          });
        },
      }
    }
  },
  plugins: [vue(), tailwindcss(), heyApiPlugin(
    {
      config: {
        input: "http://localhost:8000/openapi.json",
        output: 'src/api',
      },
      vite: {
        apply: 'serve',
      },
    }
  )],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
