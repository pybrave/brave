import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
  base: './',
  resolve: {
    alias: {
      '@': path.join(__dirname, 'src'),
    },
  },
  plugins: [react()],
  server:{
    proxy:{
      '/api':{
        target: `http://localhost:3000`,
        ws: true
      },'/jupyter':{
        target: `http://localhost:10100`,
        ws: true
      },'/mvp-api':{
        target: `http://localhost:4000`,
        ws: true
      },
    }
  }
})
