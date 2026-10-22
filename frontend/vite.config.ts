import path from 'node:path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
export default defineConfig({
  plugins: [react(), {
    name: 'deenly-entry-view-preload',
    apply: 'build',
    transformIndexHtml: {
      order: 'post',
      handler(_html, context) {
        const bundle = context.bundle ?? {};
        const files = new Set<string>();
        function include(file: string) {
          const chunk = bundle[file];
          if (!chunk || chunk.type !== 'chunk' || chunk.isEntry || files.has(file)) return;
          files.add(file);
          chunk.imports.forEach(include);
        }
        for (const chunk of Object.values(bundle)) {
          if (chunk.type === 'chunk' && Object.keys(chunk.modules).some((id) =>
            /\/src\/(app\/layouts\/dashboard\/layout\.tsx|modules\/dashboard\/index\.ts)$/.test(id.replaceAll('\\', '/'))
          )) include(chunk.fileName);
        }
        if (!files.size) throw new Error('Entry dashboard preload chunks were not found');
        return [...files].map((file) => ({
          tag: 'link', attrs: { rel: 'modulepreload', crossorigin: true, href: `/${file}` },
          injectTo: 'head' as const,
        }));
      },
    },
  }],
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
