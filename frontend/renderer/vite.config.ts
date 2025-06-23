/**
 * Vite config for the renderer process.
 * Assumes React + TypeScript.
 */
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  root: __dirname,
  base: './',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
}); 