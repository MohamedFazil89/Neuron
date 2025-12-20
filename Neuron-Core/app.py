from flask import Flask, request, jsonify
from dotenv import load_dotenv
import traceback
from agents.architect import architect_agent
from agents.backend import backend_agent
from agents.frontend import frontend_agent
from agents.analyzer import analyze_project
from agents.backend_contextual import backend_agent_contextual
from agents.frontend_contextual import frontend_agent_contextual

load_dotenv()

app = Flask(__name__)

# Store project path (can be set via config)
PROJECT_PATH = None

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/set-project", methods=["POST"])
def set_project():
    """
    Set the project path for context-aware generation.
    
    Input: {"project_path": "/absolute/path/to/project"}
    """
    global PROJECT_PATH
    
    try:
        data = request.get_json()
        if not data or "project_path" not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'project_path' in request body"
            }), 400
        
        PROJECT_PATH = data["project_path"]
        
        # Analyze project immediately
        analysis = analyze_project(PROJECT_PATH)
        
        return jsonify({
            "status": "success",
            "message": f"Project path set to: {PROJECT_PATH}",
            "analysis": {
                "backend_files": len(analysis["backend"]["files"]),
                "frontend_files": len(analysis["frontend"]["files"]),
                "has_package_json": analysis["package_json"] is not None
            }
        }), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/analyze", methods=["GET"])
def analyze():
    """
    Analyze the current project structure.
    """
    global PROJECT_PATH
    
    if not PROJECT_PATH:
        return jsonify({
            "status": "error",
            "message": "Project path not set. Use /set-project first."
        }), 400
    
    try:
        analysis = analyze_project(PROJECT_PATH)
        
        # Remove file contents from response (too large)
        analysis_summary = {
            "project_path": analysis["project_path"],
            "backend": {
                "exists": analysis["backend"]["exists"],
                "files": analysis["backend"]["files"],
                "routes": analysis["backend"]["routes"],
                "models": analysis["backend"]["models"],
                "controllers": analysis["backend"]["controllers"]
            },
            "frontend": {
                "exists": analysis["frontend"]["exists"],
                "files": analysis["frontend"]["files"],
                "components": analysis["frontend"]["components"],
                "pages": analysis["frontend"]["pages"],
                "hooks": analysis["frontend"]["hooks"]
            },
            "has_package_json": analysis["package_json"] is not None,
            "env_files": analysis["env_files"]
        }
        
        return jsonify({
            "status": "success",
            "analysis": analysis_summary
        }), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/build-contextual", methods=["POST"])
def build_contextual():
    """
    Context-aware build: analyzes existing project before generating code.
    
    Input: {"feature": "Add user login with email and password"}
    """
    global PROJECT_PATH
    
    if not PROJECT_PATH:
        return jsonify({
            "status": "error",
            "message": "Project path not set. Use /set-project first."
        }), 400
    
    try:
        data = request.get_json()
        if not data or "feature" not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'feature' in request body"
            }), 400
        
        feature = data["feature"]
        
        print("\n" + "=" * 60)
        print(f"[CONTEXTUAL-PIPELINE] Starting: {feature}")
        print(f"[CONTEXTUAL-PIPELINE] Project: {PROJECT_PATH}")
        print("=" * 60 + "\n")
        
        # Step 1: Analyze project
        print("[CONTEXTUAL-PIPELINE] → Analyzing existing project...")
        analysis = analyze_project(PROJECT_PATH)
        
        # Step 2: Architect
        print("[CONTEXTUAL-PIPELINE] → Creating contract...")
        contract = architect_agent(feature)
        
        # Step 3: Context-aware backend
        print("[CONTEXTUAL-PIPELINE] → Generating backend code...")
        backend_result = backend_agent_contextual(feature, contract, analysis)
        
        # Step 4: Context-aware frontend
        print("[CONTEXTUAL-PIPELINE] → Generating frontend code...")
        frontend_result = frontend_agent_contextual(feature, contract, analysis)
        
        print("\n" + "=" * 60)
        print(f"[CONTEXTUAL-PIPELINE] ✓✓✓ COMPLETE ✓✓✓")
        print(f"  Backend: {len(backend_result['files'])} files")
        print(f"  Frontend: {len(frontend_result['files'])} files")
        print("=" * 60 + "\n")
        
        return jsonify({
            "status": "success",
            "contract": contract,
            "backend": backend_result,
            "frontend": frontend_result,
            "project_analysis": {
                "backend_files_scanned": len(analysis["backend"]["files"]),
                "frontend_files_scanned": len(analysis["frontend"]["files"])
            }
        }), 200
    
    except Exception as e:
        print("\n[ERROR] Contextual pipeline failed")
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Keep existing routes
@app.route("/build", methods=["POST"])
def run_full_pipeline():
    # ... (keep your existing /build route)
    pass


@app.route("/build-and-save", methods=["POST"])
def build_and_save():
    """
    Context-aware build AND save files to disk automatically.
    
    Input: {"feature": "Add user login with email and password"}
    """
    global PROJECT_PATH
    
    if not PROJECT_PATH:
        return jsonify({
            "status": "error",
            "message": "Project path not set. Use /set-project first."
        }), 400
    
    import os
    from pathlib import Path
    
    try:
        data = request.get_json()
        if not data or "feature" not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'feature' in request body"
            }), 400
        
        feature = data["feature"]
        
        print("\n" + "=" * 60)
        print(f"[BUILD-AND-SAVE] Starting: {feature}")
        print(f"[BUILD-AND-SAVE] Project: {PROJECT_PATH}")
        print("=" * 60 + "\n")
        
        # Step 1: Analyze project
        analysis = analyze_project(PROJECT_PATH)
        
        # Step 2: Architect
        contract = architect_agent(feature)
        
        # Step 3: Backend
        backend_result = backend_agent_contextual(feature, contract, analysis)
        
        # Step 4: Frontend
        frontend_result = frontend_agent_contextual(feature, contract, analysis)
        
        # Step 5: SAVE FILES TO DISK
        project_root = Path(PROJECT_PATH)
        saved_files = []
        
        # Save backend files
        for file in backend_result['files']:
            file_path = project_root / file['path']
            
            # Create directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file['content'])
            
            saved_files.append({
                "path": file['path'],
                "action": file['action'],
                "type": "backend"
            })
            print(f"[SAVED] {file['action'].upper()}: {file['path']}")
        
        # Save frontend files
        for file in frontend_result['files']:
            file_path = project_root / file['path']
            
            # Create directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file['content'])
            
            saved_files.append({
                "path": file['path'],
                "action": file['action'],
                "type": "frontend"
            })
            print(f"[SAVED] {file['action'].upper()}: {file['path']}")
        
        print("\n" + "=" * 60)
        print(f"[BUILD-AND-SAVE] ✓✓✓ COMPLETE ✓✓✓")
        print(f"  Saved {len(saved_files)} files to disk")
        print("=" * 60 + "\n")
        
        return jsonify({
            "status": "success",
            "message": f"Successfully saved {len(saved_files)} files",
            "saved_files": saved_files,
            "contract": contract
        }), 200
    
    except Exception as e:
        print("\n[ERROR] Build-and-save failed")
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



if __name__ == "__main__":
    app.run(port=8000, debug=True)
