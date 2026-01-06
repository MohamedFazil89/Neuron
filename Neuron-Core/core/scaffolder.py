#!/usr/bin/env python3
"""
Scaffolder - Handles project structure creation
"""

import json
import os
from pathlib import Path

class Scaffolder:
    """
    Handles scaffolding of new projects
    """
    
    @staticmethod
    def scaffold_frontend(project_dir, framework):
        """Scaffold frontend boilerplate"""
        frontend_dir = Path(project_dir) / "frontend"
        frontend_dir.mkdir(exist_ok=True)
        
        if framework == 'react' or framework == 'vite':
            # Create React with Vite boilerplate
            (frontend_dir / "src").mkdir(exist_ok=True)
            (frontend_dir / "public").mkdir(exist_ok=True)
            
            # package.json
            package_json = {
                "name": "frontend",
                "private": True,
                "version": "0.0.0",
                "type": "module",
                "scripts": {
                    "dev": "vite",
                    "build": "vite build",
                    "preview": "vite preview"
                },
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0"
                },
                "devDependencies": {
                    "@types/react": "^18.2.43",
                    "@types/react-dom": "^18.2.17",
                    "@vitejs/plugin-react": "^4.2.1",
                    "vite": "^5.0.8"
                }
            }
            with open(frontend_dir / "package.json", 'w') as f:
                json.dump(package_json, f, indent=2)
            
            # vite.config.js
            vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
"""
            (frontend_dir / "vite.config.js").write_text(vite_config)
            
            # src/App.jsx
            app_jsx = """function App() {
  return (
    <div className="App">
      <h1>Welcome to your new React app!</h1>
      <p>Start building your features with Neuron.</p>
    </div>
  )
}

export default App
"""
            (frontend_dir / "src" / "App.jsx").write_text(app_jsx)
            
            # src/main.jsx
            main_jsx = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""
            (frontend_dir / "src" / "main.jsx").write_text(main_jsx)
            
            # index.html
            index_html = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Neuron App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""
            (frontend_dir / "index.html").write_text(index_html)
            
            # src/index.css
            (frontend_dir / "src" / "index.css").write_text("/* Add your styles here */\\n")
            
        elif framework == 'nextjs':
             # Placeholder for Next.js - for now just directory
             (frontend_dir / "app").mkdir(exist_ok=True)
             (frontend_dir / "public").mkdir(exist_ok=True)
             (frontend_dir / "package.json").write_text('{"name": "nextjs-app", "scripts": {"dev": "next dev"}}')

    @staticmethod
    def scaffold_backend(project_dir, framework):
        """Scaffold backend boilerplate"""
        backend_dir = Path(project_dir) / "backend"
        backend_dir.mkdir(exist_ok=True)
        
        if framework == 'nodejs':
            # Create Express boilerplate
            (backend_dir / "routes").mkdir(exist_ok=True)
            (backend_dir / "models").mkdir(exist_ok=True)
            (backend_dir / "controllers").mkdir(exist_ok=True)
            
            # package.json
            package_json = {
                "name": "backend",
                "version": "1.0.0",
                "main": "server.js",
                "scripts": {
                    "start": "node server.js",
                    "dev": "nodemon server.js"
                },
                "dependencies": {
                    "express": "^4.18.2",
                    "cors": "^2.8.5",
                    "dotenv": "^16.3.1"
                },
                "devDependencies": {
                    "nodemon": "^3.0.2"
                }
            }
            with open(backend_dir / "package.json", 'w') as f:
                json.dump(package_json, f, indent=2)
            
            # server.js
            server_js = """const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Server is running' });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
"""
            (backend_dir / "server.js").write_text(server_js)
            
            # .env
            (backend_dir / ".env").write_text("PORT=5000\\n")
        
        elif framework == 'python':
            # Create Flask boilerplate
            (backend_dir / "routes").mkdir(exist_ok=True)
            (backend_dir / "models").mkdir(exist_ok=True)
            
            # requirements.txt
            requirements = """flask==3.0.0
flask-cors==4.0.0
python-dotenv==1.0.0
"""
            (backend_dir / "requirements.txt").write_text(requirements)
            
            # app.py
            app_py = """from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Server is running'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, port=port)
"""
            (backend_dir / "app.py").write_text(app_py)
            
            # .env
            (backend_dir / ".env").write_text("PORT=5000\\n")

    @staticmethod
    def create_gitignore(project_dir):
        """Create .gitignore file"""
        gitignore = """# Dependencies
node_modules/
__pycache__/
*.pyc

# Environment
.env
.env.local

# Build
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        (Path(project_dir) / ".gitignore").write_text(gitignore)

    @staticmethod
    def create_readme(project_dir, project_name, frontend, backend):
        """Create README.md"""
        readme = f"""# {project_name}

Generated with Neuron AI

## Tech Stack

"""
        if frontend != 'none':
            readme += f"- **Frontend**: {frontend.capitalize()}\\n"
        if backend != 'none':
            readme += f"- **Backend**: {backend.capitalize()}\\n"
        
        readme += """
## Getting Started

"""
        
        if frontend != 'none':
            readme += """### Frontend

```bash
cd frontend
npm install
npm run dev
```

"""
        
        if backend != 'none':
            if backend == 'nodejs':
                readme += """### Backend

```bash
cd backend
npm install
npm start
```

"""
            else:
                readme += """### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

"""
        
        readme += """## Adding Features

Use Neuron to add features:

```bash
neuron add-feature "Your feature description"
```
"""
        (Path(project_dir) / "README.md").write_text(readme)
