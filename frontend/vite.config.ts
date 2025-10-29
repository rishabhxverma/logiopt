import path from "path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "tailwindcss"; // <-- 1. Import Tailwind's PostCSS plugin
import autoprefixer from "autoprefixer"; // <-- 2. Import autoprefixer

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },


  css: {
    postcss: {
      plugins: [tailwindcss, autoprefixer],
    },
  },
});
