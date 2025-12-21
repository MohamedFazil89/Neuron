# app.py - REFACTORED WITH ORCHESTRATOR
from pathlib import Path
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import traceback

# Existing agents
from agents.architect import architect_agent
from agents.backend_contextual import backend_agent_contextual
from agents.frontend_contextual import frontend_agent_contextual
from agents.analyzer import analyze_project, get_analysis_summary

# NEW: Orchestrator and Integration Verifier
from agents.orchestrator import orchestrator_agent
from agents.integration_verifier import IntegrationVerifier

# Existing utilities
from core.intent_detector import IntentDetector
from core.project_analyzer import ProjectAnalyzer
from core.project_manager import ProjectManager

load_dotenv()

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/set-project", methods=["POST"])
def set_project():
    """Set the project path for context-aware generation."""
    try:
        data = request.get_json()
        if not data or "project_path" not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'project_path' in request body"
            }), 400
        
        project_path = data["project_path"]
        result = ProjectManager.set_project(project_path)
        
        if result["status"] == "error":
            return jsonify(result), 400
        
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
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/analyze", methods=["GET"])
def analyze():
    """Comprehensive project analysis with AI-powered tech stack detection."""
    try:
        project_info = ProjectManager.get_current_project()
        
        if not project_info:
            return jsonify({
                "status": "error",
                "message": "Project path not set. Use /set-project first."
            }), 400
        
        project_path = project_info["path"]
        analysis = analyze_project(project_path)
        analysis_summary = get_analysis_summary(analysis)
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
    """Generate intelligent insights about the project."""
    insights = []
    
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
    
    testing_tools = analysis["tech_stack"]["testing"]
    if not testing_tools:
        insights.append({
            "type": "testing",
            "level": "warning",
            "message": "No testing framework detected. Consider adding Jest, Vitest, or Pytest."
        })
    
    return insights


@app.route("/list-projects", methods=["GET"])
def list_projects():
    """List all saved projects"""
    try:
        result = ProjectManager.list_projects()
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/project-features", methods=["GET"])
def get_project_features():
    """Get features added to current project"""
    try:
        features = ProjectManager.get_project_features()
        return jsonify({"status": "success", "features": features}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/build-and-save", methods=["POST"])
def build_and_save():
    """
    Main endpoint: Either build feature OR analyze project.
    Automatically detects intent using Orchestrator.
    
    NEW BEHAVIOR:
    - Uses Orchestrator to decide which agents run
    - Only calls necessary agents
    - Verifies integration after generation
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
        print("=" * 60 + "\n")
        
        # STEP 2: ROUTE BASED ON INTENT
        if intent == "ANALYSIS":
            return _handle_analysis_request(feature)
        else:  # FEATURE
            return _handle_feature_request_with_orchestrator(feature)
    
    except Exception as e:
        print("\n[ERROR] Build-and-save failed")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


def _handle_analysis_request(request_text):
    """Handle analysis/verification requests (NO CODE GENERATION)"""
    try:
        project_info = ProjectManager.get_current_project()
        
        if not project_info:
            return jsonify({
                "status": "error",
                "message": "No project set. Use /set-project first."
            }), 400
        
        project_path = project_info["path"]
        
        print(f"\n[ANALYSIS_REQUEST] Running: {request_text}")
        print(f"[ANALYSIS_REQUEST] Project: {project_info['name']}\n")
        
        analysis_result = ProjectAnalyzer.verify_project(project_path)
        
        if analysis_result["status"] == "error":
            return jsonify(analysis_result), 400
        
        print(f"\n[ANALYSIS_REQUEST] ✓ COMPLETE")
        print(f"  Issues found: {analysis_result['summary']['issues_found']}\n")
        
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
        return jsonify({"status": "error", "message": str(e)}), 500


def _handle_feature_request_with_orchestrator(feature):
    """
    NEW: Handle feature building with Orchestrator control.
    
    This replaces the old hardcoded approach.
    Now the Orchestrator decides which agents run.
    """
    try:
        project_info = ProjectManager.get_current_project()
        
        if not project_info:
            return jsonify({
                "status": "error",
                "message": "No project set. Use /set-project first."
            }), 400
        
        project_path = project_info["path"]
        
        print("\n" + "=" * 60)
        print(f"[ORCHESTRATED-PIPELINE] Starting: {feature}")
        print(f"[ORCHESTRATED-PIPELINE] Project: {project_info['name']}")
        print("=" * 60 + "\n")
        
        # Step 1: Analyze project
        print("[ORCHESTRATED-PIPELINE] → Analyzing existing project...")
        analysis = analyze_project(project_path)
        
        # Step 2: Architect creates contract
        print("[ORCHESTRATED-PIPELINE] → Creating contract...")
        contract = architect_agent(feature)
        
        # Step 3: NEW - Orchestrator decides which agents to run
        print("[ORCHESTRATED-PIPELINE] → Consulting Orchestrator...")
        execution_plan = orchestrator_agent(feature, contract, analysis)
        
        # Step 4: Execute ONLY the agents specified by Orchestrator
        backend_result = None
        frontend_result = None
        
        for step in execution_plan["execution_plan"]:
            agent_type = step["agent"]
            
            if agent_type == "backend":
                print(f"[ORCHESTRATED-PIPELINE] → Running Backend Agent...")
                backend_result = backend_agent_contextual(feature, contract, analysis)
            
            elif agent_type == "frontend":
                print(f"[ORCHESTRATED-PIPELINE] → Running Frontend Agent...")
                frontend_result = frontend_agent_contextual(feature, contract, analysis)
        
        # Step 5: Save files to disk
        project_root = Path(project_path)
        saved_files = []
        
        if backend_result and backend_result.get("files"):
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
        
        if frontend_result and frontend_result.get("files"):
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
        
        # Step 6: NEW - Integration Verification
        integration_issues = []
        
        if execution_plan.get("integration_required"):
            print("\n[ORCHESTRATED-PIPELINE] → Verifying integration...")
            
            frontend_files = [f['path'] for f in saved_files if f['type'] == 'frontend']
            backend_files = [f['path'] for f in saved_files if f['type'] == 'backend']
            
            if frontend_files:
                frontend_verification = IntegrationVerifier.verify_frontend_integration(
                    project_path, frontend_files
                )
                if frontend_verification["status"] == "issues_found":
                    integration_issues.extend(frontend_verification["issues"])
                    
                    print(f"[INTEGRATION] ⚠ Found {len(frontend_verification['issues'])} frontend integration issues")
                    
                    # Auto-fix if possible
                    if frontend_verification["auto_fixable"]:
                        print(f"[INTEGRATION] → Applying auto-fixes...")
                        fix_result = IntegrationVerifier.auto_fix_integration(
                            project_path, frontend_verification["fix_plan"]
                        )
                        print(f"[INTEGRATION] ✓ Fixed {len(fix_result['fixed'])} issues")
            
            if backend_files:
                backend_verification = IntegrationVerifier.verify_backend_integration(
                    project_path, backend_files
                )
                if backend_verification["status"] == "issues_found":
                    integration_issues.extend(backend_verification["issues"])
                    
                    print(f"[INTEGRATION] ⚠ Found {len(backend_verification['issues'])} backend integration issues")
                    
                    if backend_verification["auto_fixable"]:
                        print(f"[INTEGRATION] → Applying auto-fixes...")
                        fix_result = IntegrationVerifier.auto_fix_integration(
                            project_path, backend_verification["fix_plan"]
                        )
                        print(f"[INTEGRATION] ✓ Fixed {len(fix_result['fixed'])} issues")
        
        # Step 7: Track feature in persistent memory
        ProjectManager.add_feature_to_project(feature)
        
        print("\n" + "=" * 60)
        print(f"[ORCHESTRATED-PIPELINE] ✓✓✓ COMPLETE ✓✓✓")
        print(f"  Saved {len(saved_files)} files")
        if integration_issues:
            print(f"  Integration issues: {len(integration_issues)} (auto-fixed)")
        print("=" * 60 + "\n")
        
        return jsonify({
            "status": "success",
            "request_type": "FEATURE",
            "message": f"Successfully saved {len(saved_files)} files",
            "saved_files": saved_files,
            "contract": contract,
            "execution_plan": execution_plan,
            "integration_verified": execution_plan.get("integration_required", False),
            "integration_issues": integration_issues,
            "project_info": {
                "name": project_info['name'],
                "path": project_path
            }
        }), 200
    
    except Exception as e:
        print(f"\n[ERROR] Feature request failed: {str(e)}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/audit-fix", methods=["POST"])
def audit_fix():
    """
    NEW ENDPOINT: Audit and fix integration issues in ANY project.
    
    This command:
    1. Scans entire project (works on any project, not just Neuron-generated)
    2. Detects integration issues (orphaned files, missing imports, etc.)
    3. Optionally auto-fixes detected issues
    
    Input:
    {
        "project_path": "/path/to/project" (optional if project already set),
        "auto_fix": true/false (default: false)
    }
    """
    try:
        data = request.get_json() or {}
        auto_fix = data.get("auto_fix", False)
        
        # Get project path
        project_path = data.get("project_path")
        if not project_path:
            project_info = ProjectManager.get_current_project()
            if not project_info:
                return jsonify({
                    "status": "error",
                    "message": "No project specified and no current project set"
                }), 400
            project_path = project_info["path"]
        else:
            # Set as current project
            ProjectManager.set_project(project_path)
        
        print("\n" + "=" * 60)
        print(f"[AUDIT-FIX] Auditing project: {project_path}")
        print(f"[AUDIT-FIX] Auto-fix: {'ENABLED' if auto_fix else 'DISABLED'}")
        print("=" * 60 + "\n")
        
        # Analyze project structure
        analysis = analyze_project(project_path)
        
        # Collect all files
        all_frontend_files = analysis["frontend"]["files"]
        all_backend_files = analysis["backend"]["files"]
        
        # Verify frontend integration
        print("[AUDIT-FIX] → Checking frontend integration...")
        frontend_verification = IntegrationVerifier.verify_frontend_integration(
            project_path, all_frontend_files
        )
        
        # Verify backend integration
        print("[AUDIT-FIX] → Checking backend integration...")
        backend_verification = IntegrationVerifier.verify_backend_integration(
            project_path, all_backend_files
        )
        
        # Collect all issues
        all_issues = []
        all_issues.extend(frontend_verification.get("issues", []))
        all_issues.extend(backend_verification.get("issues", []))
        
        print(f"\n[AUDIT-FIX] Found {len(all_issues)} total issues")
        
        # Auto-fix if requested
        fixes_applied = []
        if auto_fix and all_issues:
            print(f"[AUDIT-FIX] → Applying auto-fixes...")
            
            # Check if there are any auto-fixable issues
            auto_fixable_issues = [i for i in all_issues if i.get("auto_fixable", False)]
            
            if auto_fixable_issues:
                # Apply frontend fixes
                if frontend_verification.get("fix_plan"):
                    print(f"[AUDIT-FIX] → Fixing {len(frontend_verification['fix_plan'])} frontend issues...")
                    fix_result = IntegrationVerifier.auto_fix_integration(
                        project_path, frontend_verification["fix_plan"]
                    )
                    fixes_applied.extend(fix_result["fixed"])
                    
                    if fix_result.get("failed"):
                        print(f"[AUDIT-FIX] ⚠ {len(fix_result['failed'])} fixes failed")
                        for failed in fix_result["failed"]:
                            print(f"  - {failed['fix']['action']}: {failed['error']}")
                
                # Apply backend fixes
                if backend_verification.get("fix_plan"):
                    print(f"[AUDIT-FIX] → Fixing {len(backend_verification['fix_plan'])} backend issues...")
                    fix_result = IntegrationVerifier.auto_fix_integration(
                        project_path, backend_verification["fix_plan"]
                    )
                    fixes_applied.extend(fix_result["fixed"])
                    
                    if fix_result.get("failed"):
                        print(f"[AUDIT-FIX] ⚠ {len(fix_result['failed'])} fixes failed")
                        for failed in fix_result["failed"]:
                            print(f"  - {failed['fix']['action']}: {failed['error']}")
                
                print(f"[AUDIT-FIX] ✓ Applied {len(fixes_applied)} fixes")
            else:
                print(f"[AUDIT-FIX] ℹ No auto-fixable issues found")
        
        print("\n" + "=" * 60)
        print(f"[AUDIT-FIX] ✓ Audit complete")
        print("=" * 60 + "\n")
        
        return jsonify({
            "status": "success",
            "project_path": project_path,
            "issues_found": len(all_issues),
            "issues": all_issues,
            "auto_fix_enabled": auto_fix,
            "fixes_applied": len(fixes_applied) if auto_fix else 0,
            "fixes": fixes_applied if auto_fix else [],
            "frontend_verification": frontend_verification,
            "backend_verification": backend_verification
        }), 200
    
    except Exception as e:
        print(f"\n[ERROR] Audit-fix failed: {str(e)}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(port=8000, debug=True)