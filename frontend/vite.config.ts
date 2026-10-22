import path from 'node:path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
export default defineConfig({
  plugins: [react()],
  resolve: { alias: { src: path.resolve(process.cwd(), 'src') } },
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: Object.fromEntries(
      ['/api', '/auth', '/admin', '/media', '/learn/', '/sitemap.xml'].map((prefix) => [
        prefix,
        { target: 'http://127.0.0.1:8001' },
      ])
    ),
  },
  preview: { host: '127.0.0.1', port: 5173, strictPort: true },
});
