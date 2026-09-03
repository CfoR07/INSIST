import os

f_dir = r"n:\PROJECTS\INSIST\sih26034\frontend"

# 1. vite.config.js
with open(os.path.join(f_dir, "vite.config.js"), "w", encoding="utf-8") as f:
    f.write("""import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/uploads': 'http://127.0.0.1:8000'
    }
  }
})
""")

# 2. tailwind.config.js
with open(os.path.join(f_dir, "tailwind.config.js"), "w", encoding="utf-8") as f:
    f.write("""/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
""")

# 3. postcss.config.js
with open(os.path.join(f_dir, "postcss.config.js"), "w", encoding="utf-8") as f:
    f.write("""export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""")

# 4. index.html
with open(os.path.join(f_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write("""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>SIH26034 — AI-Assisted Commodity Inspection System</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  </head>
  <body class="bg-slate-950 text-slate-100 antialiased font-sans">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
""")

print("Config files generated successfully")
