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
    allowedHosts:true,
    proxy:{
      // '/api':{
      //   target: `http://localhost:3000`,
      //   ws: true
      // },
      '/jupyter':{
        target: `http://localhost:10100`,
        ws: true
      },'/brave-api':{
        target: `http://localhost:4000`,
        ws: true
      },'/api':{
        target: `http://10.110.1.11:11434`,
        ws: true
      },
    }
  }
})
