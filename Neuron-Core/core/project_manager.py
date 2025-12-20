# core/project_manager.py
import json
import os
from pathlib import Path
from datetime import datetime

CONFIG_DIR = Path(__file__).parent.parent / "config"
PROJECTS_FILE = CONFIG_DIR / "projects.json"

# Ensure config directory exists
CONFIG_DIR.mkdir(exist_ok=True)

class ProjectManager:
    """Persistent project memory system"""
    
    @staticmethod
    def _ensure_file_exists():
        """Create projects.json if it doesn't exist"""
        if not PROJECTS_FILE.exists():
            PROJECTS_FILE.write_text(json.dumps({
                "projects": {},
                "current": None,
                "last_updated": datetime.now().isoformat()
            }, indent=2))
    
    @staticmethod
    def set_project(project_path, project_name=None):
        """
        Set active project and save to memory
        
        Args:
            project_path: Absolute path to project
            project_name: Optional name. If None, extracts from path
        
        Returns:
            dict with status and project info
        """
        ProjectManager._ensure_file_exists()
        
        # Validate path
        project_path = str(Path(project_path).resolve())
        if not os.path.isdir(project_path):
            return {"status": "error", "message": f"Path does not exist: {project_path}"}
        
        # Extract project name if not provided
        if not project_name:
            project_name = os.path.basename(project_path)
        
        # Read current data
        data = json.loads(PROJECTS_FILE.read_text())
        
        # Add/update project
        data["projects"][project_name] = {
            "path": project_path,
            "created_at": data["projects"].get(project_name, {}).get("created_at", datetime.now().isoformat()),
            "last_accessed": datetime.now().isoformat(),
            "features_added": data["projects"].get(project_name, {}).get("features_added", [])
        }
        
        # Set as current
        data["current"] = project_name
        data["last_updated"] = datetime.now().isoformat()
        
        # Write back
        PROJECTS_FILE.write_text(json.dumps(data, indent=2))
        
        print(f"[PROJECT_MANAGER] Project '{project_name}' set as active")
        print(f"  Path: {project_path}")
        
        return {
            "status": "success",
            "project_name": project_name,
            "project_path": project_path
        }
    
    @staticmethod
    def get_current_project():
        """
        Get current active project
        
        Returns:
            dict with project info or None
        """
        ProjectManager._ensure_file_exists()
        
        data = json.loads(PROJECTS_FILE.read_text())
        
        if not data["current"]:
            return None
        
        current_name = data["current"]
        return {
            "name": current_name,
            **data["projects"].get(current_name, {})
        }
    
    @staticmethod
    def add_feature_to_project(feature_name, project_name=None):
        """
        Track features added to project
        
        Args:
            feature_name: Name of feature added
            project_name: Which project (uses current if None)
        """
        ProjectManager._ensure_file_exists()
        
        data = json.loads(PROJECTS_FILE.read_text())
        
        if not project_name:
            project_name = data["current"]
        
        if project_name not in data["projects"]:
            return {"status": "error", "message": f"Project '{project_name}' not found"}
        
        # Add feature to history
        data["projects"][project_name]["features_added"].append({
            "name": feature_name,
            "added_at": datetime.now().isoformat()
        })
        
        PROJECTS_FILE.write_text(json.dumps(data, indent=2))
        
        return {"status": "success"}
    
    @staticmethod
    def list_projects():
        """Get all projects"""
        ProjectManager._ensure_file_exists()
        
        data = json.loads(PROJECTS_FILE.read_text())
        return {
            "projects": data["projects"],
            "current": data["current"]
        }
    
    @staticmethod
    def get_project_features(project_name=None):
        """Get features added to a project"""
        ProjectManager._ensure_file_exists()
        
        data = json.loads(PROJECTS_FILE.read_text())
        
        if not project_name:
            project_name = data["current"]
        
        if project_name not in data["projects"]:
            return []
        
        return data["projects"][project_name].get("features_added", [])