import os

src_dir = r"n:\PROJECTS\INSIST\sih26034\frontend\src"
pages_dir = os.path.join(src_dir, "pages")

# 1. index.css
with open(os.path.join(src_dir, "index.css"), "w", encoding="utf-8") as f:
    f.write("""@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  background-color: #030712;
  color: #f3f4f6;
}

code, pre {
  font-family: 'JetBrains Mono', monospace;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: #0b0f19;
}
::-webkit-scrollbar-thumb {
  background: #1e293b;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #334155;
}
""")

# 2. main.jsx
with open(os.path.join(src_dir, "main.jsx"), "w", encoding="utf-8") as f:
    f.write("""import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
""")

print("index.css and main.jsx generated")
