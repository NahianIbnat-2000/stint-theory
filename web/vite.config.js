import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages serves the site at /stint-theory/
export default defineConfig({ plugins: [react()], base: "/stint-theory/" });
