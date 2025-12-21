from pathlib import Path
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import traceback
from agents.architect import architect_agent
from agents.backend import backend_agent
from agents.frontend import frontend_agent
from agents.analyzer import analyze_project, get_analysis_summary
from agents.backend_contextual import backend_agent_contextual
from agents.frontend_contextual import frontend_agent_contextual
from core.intent_detector import IntentDetector
from core.project_analyzer import ProjectAnalyzer
from core.project_manager import ProjectManager


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
    try:
        data = request.get_json()
        if not data or "project_path" not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'project_path' in request body"
            }), 400
        
        project_path = data["project_path"]
        
        # Set project using ProjectManager (PERSISTENT MEMORY)
        result = ProjectManager.set_project(project_path)
        
        if result["status"] == "error":
            return jsonify(result), 400
        
        # Analyze project immediately
        analysis = analyze_project(project_path)
        
        return jsonify({
            "status": "success",
            "message": f"Project '{result['project_name']}' set successfully",
            "project_name": result['project_name'],
            "project_path": result['project_path'],
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
    Comprehensive project analysis with AI-powered tech stack detection.
    Single endpoint that returns everything: structure, tech stack, and insights.
    """
    try:
        # Get project from PERSISTENT MEMORY
        project_info = ProjectManager.get_current_project()
        
        if not project_info:
            return jsonify({
                "status": "error",
                "message": "Project path not set. Use /set-project first."
            }), 400
        
        project_path = project_info["path"]
        
        # Run AI-powered analysis
        analysis = analyze_project(project_path)
        
        # Get clean summary (removes large file contents)
        analysis_summary = get_analysis_summary(analysis)
        
        # Add insights
        insights = generate_project_insights(analysis)
        analysis_summary["insights"] = insights
        
        return jsonify({
            "status": "success",
            "analysis": analysis_summary
        }), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500


def generate_project_insights(analysis):
    """
    Generate intelligent insights about the project.
    """
    insights = []
    
    # Check if project has both frontend and backend
    if analysis["frontend"]["exists"] and analysis["backend"]["exists"]:
        insights.append({
            "type": "architecture",
            "level": "info",
            "message": f"Full-stack application detected: {analysis['frontend']['detected_framework']} + {analysis['backend']['detected_framework']}"
        })
    elif analysis["frontend"]["exists"] and not analysis["backend"]["exists"]:
        insights.append({
            "type": "architecture",
            "level": "info",
            "message": f"Frontend-only application: {analysis['frontend']['detected_framework']}"
        })
    elif analysis["backend"]["exists"] and not analysis["frontend"]["exists"]:
        insights.append({
            "type": "architecture",
            "level": "info",
            "message": f"Backend-only API: {analysis['backend']['detected_framework']}"
        })
    else:
        insights.append({
            "type": "architecture",
            "level": "warning",
            "message": "No clear frontend or backend framework detected. This might be a utility/library project."
        })
    
    # Check for TypeScript
    if 'typescript' in analysis["tech_stack"]["language"]:
        insights.append({
            "type": "language",
            "level": "success",
            "message": "TypeScript detected - type safety enabled"
        })
    
    # Check for testing frameworks
    testing_tools = analysis["tech_stack"]["testing"]
    if testing_tools:
        insights.append({
            "type": "testing",
            "level": "success",
            "message": f"Testing configured with {', '.join(testing_tools.keys())}"
        })
    else:
        insights.append({
            "type": "testing",
            "level": "warning",
            "message": "No testing framework detected. Consider adding Jest, Vitest, or Pytest."
        })
    
    # Check for database
    databases = analysis["tech_stack"]["database"]
    orms = analysis["tech_stack"]["orm"]
    if databases or orms:
        db_info = list(databases.keys()) + list(orms.keys())
        insights.append({
            "type": "database",
            "level": "info",
            "message": f"Database layer: {', '.join(db_info)}"
        })
    
    # Check for state management (frontend)
    state_mgmt = analysis["tech_stack"]["state_management"]
    if state_mgmt and analysis["frontend"]["exists"]:
        insights.append({
            "type": "state",
            "level": "info",
            "message": f"State management: {', '.join(state_mgmt.keys())}"
        })
    
    # Check for styling solution
    styling = analysis["tech_stack"]["styling"]
    if styling:
        insights.append({
            "type": "styling",
            "level": "info",
            "message": f"Styling: {', '.join(styling.keys())}"
        })
    
    # Check for environment files
    if not analysis["env_files"]:
        insights.append({
            "type": "config",
            "level": "warning",
            "message": "No .env files detected. Consider adding environment configuration."
        })
    
    # Project size insights
    total_files = len(analysis["frontend"]["files"]) + len(analysis["backend"]["files"])
    if total_files > 500:
        insights.append({
            "type": "size",
            "level": "info",
            "message": f"Large project detected ({total_files} files). Consider modularization."
        })
    elif total_files < 20:
        insights.append({
            "type": "size",
            "level": "info",
            "message": "Small project - perfect for rapid development."
        })
    
    return insights

@app.route("/list-projects", methods=["GET"])
def list_projects():
    """List all saved projects"""
    try:
        result = ProjectManager.list_projects()
        return jsonify({
            "status": "success",
            "data": result
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/project-features", methods=["GET"])
def get_project_features():
    """Get features added to current project"""
    try:
        features = ProjectManager.get_project_features()
        return jsonify({
            "status": "success",
            "features": features
        }), 200
    except Exception as e:
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
    try:
        # Get project from PERSISTENT MEMORY
        project_info = ProjectManager.get_current_project()
        
        if not project_info:
            return jsonify({
                "status": "error",
                "message": "Project path not set. Use /set-project first."
            }), 400
        
        project_path = project_info["path"]
        
        data = request.get_json()
        if not data or "feature" not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'feature' in request body"
            }), 400
        
        feature = data["feature"]
        
        print("\n" + "=" * 60)
        print(f"[CONTEXTUAL-PIPELINE] Starting: {feature}")
        print(f"[CONTEXTUAL-PIPELINE] Project: {project_info['name']}")
        print("=" * 60 + "\n")
        
        # Step 1: Analyze project
        print("[CONTEXTUAL-PIPELINE] → Analyzing existing project...")
        analysis = analyze_project(project_path)
        
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


@app.route("/build-and-save", methods=["POST"])
def build_and_save():
    """
    Main endpoint: Either build feature OR analyze project
    Automatically detects intent
    
    Input: {"feature": "Add login"} or {"feature": "verify project"}
    """
    try:
        data = request.get_json()
        if not data or "feature" not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'feature' in request body"
            }), 400
        
        feature = data["feature"]
        
        # STEP 1: DETECT INTENT
        print("\n" + "=" * 60)
        print(f"[INTENT_DETECTOR] Analyzing: {feature}")
        
        intent = IntentDetector.detect(feature)
        intent_details = IntentDetector.explain(feature)
        
        print(f"[INTENT_DETECTOR] Intent: {intent}")
        print(f"  Confidence: {intent_details['confidence']:.0%}")
        print(f"  Analysis keywords: {intent_details['analysis_keywords_found']}")
        print(f"  Feature keywords: {intent_details['feature_keywords_found']}")
        print("=" * 60 + "\n")
        
        # STEP 2: ROUTE BASED ON INTENT
        if intent == "ANALYSIS":
            return _handle_analysis_request(feature)
        else:  # FEATURE
            return _handle_feature_request(feature)
    
    except Exception as e:
        print("\n[ERROR] Build-and-save failed")
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


def _handle_analysis_request(request_text):
    """Handle analysis/verification requests (NO CODE GENERATION)"""
    
    try:
        # Get current project from PERSISTENT MEMORY
        project_info = ProjectManager.get_current_project()
        
        if not project_info:
            return jsonify({
                "status": "error",
                "message": "No project set. Use /set-project first."
            }), 400
        
        project_path = project_info["path"]
        
        print("\n" + "=" * 60)
        print(f"[ANALYSIS_REQUEST] Running: {request_text}")
        print(f"[ANALYSIS_REQUEST] Project: {project_info['name']}")
        print("=" * 60 + "\n")
        
        # Analyze project (REPORT ONLY - NO CODE GENERATION)
        analysis_result = ProjectAnalyzer.verify_project(project_path)
        
        if analysis_result["status"] == "error":
            return jsonify(analysis_result), 400
        
        print("\n" + "=" * 60)
        print(f"[ANALYSIS_REQUEST] ✓ COMPLETE")
        print(f"  Total backend files: {analysis_result['summary']['total_backend_files']}")
        print(f"  Total frontend files: {analysis_result['summary']['total_frontend_files']}")
        print(f"  Issues found: {analysis_result['summary']['issues_found']}")
        print(f"  Severity: {analysis_result['summary']['severity']}")
        print("=" * 60 + "\n")
        
        return jsonify({
            "status": "success",
            "request_type": "ANALYSIS",
            "request_text": request_text,
            "project_info": {
                "name": project_info['name'],
                "path": project_path
            },
            "analysis": analysis_result
        }), 200
    
    except Exception as e:
        print(f"\n[ERROR] Analysis request failed: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


def _handle_feature_request(feature):
    """Handle feature building requests (CODE GENERATION)"""
    
    try:
        # Get current project from PERSISTENT MEMORY
        project_info = ProjectManager.get_current_project()
        
        if not project_info:
            return jsonify({
                "status": "error",
                "message": "No project set. Use /set-project first."
            }), 400
        
        project_path = project_info["path"]
        
        print("\n" + "=" * 60)
        print(f"[FEATURE_REQUEST] Building: {feature}")
        print(f"[FEATURE_REQUEST] Project: {project_info['name']}")
        print(f"[FEATURE_REQUEST] Path: {project_path}")
        print("=" * 60 + "\n")
        
        # Step 1: Analyze project
        analysis = analyze_project(project_path)
        
        # Step 2: Create contract
        contract = architect_agent(feature)
        
        # Step 3: Generate backend
        backend_result = backend_agent_contextual(feature, contract, analysis)
        
        # Step 4: Generate frontend
        frontend_result = frontend_agent_contextual(feature, contract, analysis)
        
        # Step 5: Write files to disk
        project_root = Path(project_path)
        saved_files = []
        
        # Save backend files
        for file in backend_result['files']:
            file_path = project_root / file['path']
            file_path.parent.mkdir(parents=True, exist_ok=True)
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
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file['content'])
            saved_files.append({
                "path": file['path'],
                "action": file['action'],
                "type": "frontend"
            })
            print(f"[SAVED] {file['action'].upper()}: {file['path']}")
        
        # Step 6: Track feature in persistent memory
        ProjectManager.add_feature_to_project(feature)
        
        print("\n" + "=" * 60)
        print(f"[FEATURE_REQUEST] ✓ COMPLETE")
        print(f"  Saved {len(saved_files)} files")
        print("=" * 60 + "\n")
        
        return jsonify({
            "status": "success",
            "request_type": "FEATURE",
            "message": f"Successfully saved {len(saved_files)} files",
            "saved_files": saved_files,
            "contract": contract,
            "project_info": {
                "name": project_info['name'],
                "path": project_path
            }
        }), 200
    
    except Exception as e:
        print(f"\n[ERROR] Feature request failed: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(port=8000, debug=True)