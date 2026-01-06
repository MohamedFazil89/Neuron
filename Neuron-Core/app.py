#!/usr/bin/env python3
"""
Neuron Backend - Flask API for AI-powered code generation
"""

from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import traceback
import os

# Import agents and core modules
from agents.architect import architect_agent
from agents.backend_contextual import backend_agent_contextual
from agents.frontend_contextual import frontend_agent_contextual
from agents.analyzer import analyze_project, get_analysis_summary
from agents.orchestrator import orchestrator_agent
from agents.integration_verifier import IntegrationVerifier
from core.intent_detector import IntentDetector
from core.project_analyzer import ProjectAnalyzer
from core.project_manager import ProjectManager
from core.input_validator import InputValidator
from core.scaffolder import Scaffolder

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# ============================================
# HEALTH CHECK
# ============================================

@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint
    """
    return jsonify({"status": "ok"}), 200


# ============================================
# PROJECT MANAGEMENT ENDPOINTS
# ============================================

@app.route("/set-project", methods=["POST"])
def set_project():
    """
    Set the current active project
    """
    try:
        data = request.get_json()
        
        if not data or "project_path" not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'project_path' in request body"
            }), 400
        
        project_path = data["project_path"]
        
        # Validate path exists
        path = Path(project_path)
        if not path.exists():
            return jsonify({
                "status": "error",
                "message": f"Project path does not exist: {project_path}"
            }), 400
        
        # Set project using ProjectManager
        project_info = ProjectManager.set_current_project(project_path)
        
        # Analyze the project
        analysis = analyze_project(project_path)
        
        print(f"\n[SET-PROJECT] Current Project set: {project_info['name']}")
        print(f"[SET-PROJECT] Path: {project_path}\n")
        
        return jsonify({
            "status": "success",
            "message": f"Project '{project_info['name']}' set successfully",
            "project_name": project_info["name"],
            "project_path": project_path,
            "project_id": project_info.get("id"),
            "analysis": analysis
        }), 200
    
    except Exception as e:
        print(f"\n[ERROR] Set project failed: {str(e)}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/scaffold", methods=["POST"])
def scaffold_project():
    """
    Scaffold a new project
    """
    try:
        data = request.get_json()
        
        if not data or "project_name" not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'project_name' in request body"
            }), 400
        
        project_name = data["project_name"]
        frontend = data.get("frontend", "none")
        backend = data.get("backend", "none")
        path = data.get("path")
        
        # Determine project directory
        if path:
            project_dir = Path(path) / project_name
        else:
            project_dir = Path.cwd().parent / project_name # Default to sibling of Neuron-Core
            
        # Check if directory already exists
        if project_dir.exists():
            return jsonify({
                "status": "error",
                "message": f"Directory '{project_dir}' already exists"
            }), 400
            
        # Create project directory
        project_dir.mkdir(parents=True)
        
        # Scaffold frontend
        if frontend != 'none':
            Scaffolder.scaffold_frontend(project_dir, frontend)
            
        # Scaffold backend
        if backend != 'none':
            Scaffolder.scaffold_backend(project_dir, backend)
            
        # Create .gitignore
        Scaffolder.create_gitignore(project_dir)
        
        # Create README
        Scaffolder.create_readme(project_dir, project_name, frontend, backend)
        
        # Auto-set as current project
        project_info = ProjectManager.set_current_project(str(project_dir))
        
        return jsonify({
            "status": "success",
            "message": f"Project '{project_name}' scaffolded successfully",
            "project_path": str(project_dir.resolve()),
            "project_name": project_name
        }), 201
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/list-projects", methods=["GET"])
def list_projects():
    """
    List all registered projects
    """
    try:
        all_projects = ProjectManager.list_all_projects()
        current_project = ProjectManager.get_current_project()
        
        # Convert to format frontend expects
        projects_list = []
        for name, info in all_projects.items():
            projects_list.append({
                "id": info.get("id", name),
                "name": name,
                "path": info["path"],
                "features_count": len(info.get("features_added", [])),
                "last_accessed": info.get("last_accessed", "Unknown")
            })
        
        return jsonify({
            "status": "success",
            "data": projects_list,
            "current": current_project["name"] if current_project else None
        }), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/dashboard-state", methods=["GET"])
def get_dashboard_state():
    """
    Get complete dashboard state for real-time updates
    """
    try:
        from datetime import datetime
        
        project_info = ProjectManager.get_current_project()
        
        if not project_info:
            return jsonify({
                "status": "success",
                "has_project": False,
                "project": None
            }), 200
        
        # Get fresh analysis
        analysis = analyze_project(project_info["path"])
        
        # Get features
        features = project_info.get("features_added", [])
        
        # Calculate metrics from analysis
        backend_count = len(analysis.get("backend_files", []))
        frontend_count = len(analysis.get("frontend_files", []))
        
        metrics = {
            "tokensUsed": backend_count * 100 + frontend_count * 50,
            "apiCalls": frontend_count,
            "estimatedCost": (backend_count * 0.01) + (frontend_count * 0.005),
            "avgTaskTime": 145,
            "agentFailureRate": 0,
            "retryCount": 0,
        }
        
        return jsonify({
            "status": "success",
            "has_project": True,
            "project": {
                "id": project_info.get("id"),
                "name": project_info.get("name"),
                "path": project_info.get("path"),
                "last_accessed": project_info.get("last_accessed"),
            },
            "metrics": metrics,
            "features": features,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/analyze", methods=["GET"])
def analyze():
    """
    Analyze current project structure
    """
    try:
        project_info = ProjectManager.get_current_project()
        
        if not project_info:
            return jsonify({
                "status": "error",
                "message": "No project set. Use /set-project first."
            }), 400
        
        analysis = analyze_project(project_info["path"])
        
        return jsonify({
            "status": "success",
            "analysis": analysis
        }), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/project-features", methods=["GET"])
def get_project_features():
    """
    Get features added to current project
    """
    try:
        project_info = ProjectManager.get_current_project()
        
        if not project_info:
            return jsonify({
                "status": "error",
                "message": "No project set"
            }), 400
        
        features = project_info.get("features_added", [])
        
        return jsonify({
            "status": "success",
            "features": features
        }), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================
# FEATURE GENERATION ENDPOINT
# ============================================

@app.route("/build-and-save", methods=["POST"])
def build_and_save():
    """
    Main endpoint for feature generation
    Handles both FEATURE requests and VERIFICATION
    """
    try:
        data = request.get_json()
        
        if not data or "feature" not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'feature' in request body"
            }), 400
        
        feature_description = data["feature"]
        
        # Get current project
        project_info = ProjectManager.get_current_project()
        
        if not project_info:
            return jsonify({
                "status": "error",
                "message": "No project set. Use /set-project first."
            }), 400
        
        project_path = project_info["path"]
        
        print(f"\n{'='*60}")
        print(f"[NEURON] Starting feature generation")
        print(f"[NEURON] Feature: {feature_description}")
        print(f"[NEURON] Project: {project_path}")
        print(f"{'='*60}\n")
        
        # Validate input
        validation = InputValidator.validate(feature_description)
        if not validation["valid"]:
            return jsonify({
                "status": "error",
                "message": validation["blocked_reason"]
            }), 400
        
        # Detect intent
        intent_info = IntentDetector.explain(feature_description)
        intent_type = intent_info["intent"]
        
        print(f"\n[INTENT] Detected: {intent_type}")
        print(f"[INTENT] Confidence: {intent_info['confidence']}\n")
        
        # Route based on intent
        if intent_type == "ANALYSIS":
            # Handle verification/analysis request
            analysis_result = ProjectAnalyzer.verify_project(project_path)
            
            if analysis_result["status"] == "error":
                return jsonify(analysis_result), 400
                
            return jsonify({
                "status": "success",
                "request_type": "ANALYSIS",
                "analysis": {
                    "issues": analysis_result.get("issues", []),
                    "summary": analysis_result.get("summary", {}),
                    "recommendations": analysis_result.get("recommendations", []),
                    "tech_stack": analysis_result.get("analysis", {}).get("tech_stack", {})
                }
            }), 200
        
        else:
            # Handle feature generation (FEATURE type)
            # Analyze project
            analysis = analyze_project(project_path)
            
            # Build feature using orchestrator
            result = orchestrator_agent(
                feature_description=feature_description,
                project_path=project_path,
                analysis=analysis
            )
            
            if result["status"] == "success":
                # Save feature to project history
                ProjectManager.add_feature(
                    project_path,
                    feature_description,
                    result.get("saved_files", [])
                )
                
                print(f"\n[SUCCESS] Feature generated successfully!")
                print(f"[SUCCESS] Files saved: {len(result.get('saved_files', []))}\n")
                
                return jsonify({
                    "status": "success",
                    "request_type": "FEATURE",
                    "message": "Feature generated successfully",
                    "saved_files": result.get("saved_files", []),
                    "execution_plan": result.get("execution_plan", {}),
                    "analysis": analysis
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": result.get("message", "Feature generation failed")
                }), 500
    
    except Exception as e:
        print(f"\n[ERROR] Feature generation failed: {str(e)}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================
# AGENT STATUS ENDPOINT
# ============================================

@app.route("/agents/status", methods=["GET"])
def get_agents_status():
    """
    Get status of all agents (for dashboard real-time updates)
    """
    try:
        # Return mock agent status (you can enhance this with real agent tracking)
        agents = [
            {
                "id": "architect",
                "name": "Architect Agent",
                "status": "idle",
                "currentAction": "Ready",
                "lastResponseTime": 0,
                "tokenUsage": 0
            },
            {
                "id": "backend",
                "name": "Backend Agent",
                "status": "idle",
                "currentAction": "Ready",
                "lastResponseTime": 0,
                "tokenUsage": 0
            },
            {
                "id": "frontend",
                "name": "Frontend Agent",
                "status": "idle",
                "currentAction": "Ready",
                "lastResponseTime": 0,
                "tokenUsage": 0
            }
        ]
        
        return jsonify({
            "status": "success",
            "agents": agents
        }), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================
# LOGS ENDPOINT
# ============================================

@app.route("/logs", methods=["GET"])
def get_logs():
    """
    Get execution logs (optional - for debugging)
    """
    try:
        # Return empty logs for now (you can implement log tracking)
        return jsonify({
            "status": "success",
            "logs": []
        }), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================
# HELPER FUNCTIONS
# ============================================

def _get_max_severity(issues):
    """Determine maximum severity from issues list"""
    if not issues:
        return "healthy"
    
    severity_order = ["critical", "warning", "info"]
    for severity in severity_order:
        if any(issue.get("severity") == severity for issue in issues):
            return severity
    
    return "info"


def _get_recommendations(issues):
    """Generate recommendations based on issues"""
    recommendations = []
    
    for issue in issues:
        if issue.get("type") == "missing_integration":
            recommendations.append(
                f"Import and use {issue.get('component', 'component')} in your main file"
            )
        elif issue.get("type") == "unused_file":
            recommendations.append(
                f"Remove unused file: {issue.get('file', 'unknown')}"
            )
    
    return recommendations


# ============================================
# START SERVER
# ============================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"\n{'='*60}")
    print(f"Neuron Backend Starting")
    print(f"{'='*60}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"{'='*60}\n")
    
    app.run(port=port, debug=debug, host="0.0.0.0")
