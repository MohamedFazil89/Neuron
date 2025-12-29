#!/usr/bin/env python3
"""
Project Manager - Handles project registration and tracking
"""

import json
import os
from pathlib import Path
from datetime import datetime


class ProjectManager:
    """
    Manages project configuration and history
    Stores project data in ~/.neuron/projects.json
    """
    
    CONFIG_DIR = Path.home() / ".neuron"
    PROJECTS_FILE = CONFIG_DIR / "projects.json"
    CURRENT_PROJECT_FILE = CONFIG_DIR / "current_project.json"
    
    @classmethod
    def _ensure_config_dir(cls):
        """Ensure config directory exists"""
        cls.CONFIG_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def _load_projects(cls):
        """Load all projects from config file"""
        cls._ensure_config_dir()
        
        if cls.PROJECTS_FILE.exists():
            with open(cls.PROJECTS_FILE, 'r') as f:
                return json.load(f)
        
        return {}
    
    @classmethod
    def _save_projects(cls, projects):
        """Save projects to config file"""
        cls._ensure_config_dir()
        
        with open(cls.PROJECTS_FILE, 'w') as f:
            json.dump(projects, f, indent=2)
    
    @classmethod
    def _load_current_project(cls):
        """Load current project from config"""
        cls._ensure_config_dir()
        
        if cls.CURRENT_PROJECT_FILE.exists():
            with open(cls.CURRENT_PROJECT_FILE, 'r') as f:
                return json.load(f)
        
        return None
    
    @classmethod
    def _save_current_project(cls, project_info):
        """Save current project to config"""
        cls._ensure_config_dir()
        
        with open(cls.CURRENT_PROJECT_FILE, 'w') as f:
            json.dump(project_info, f, indent=2)
    
    @classmethod
    def set_current_project(cls, project_path):
        """
        Set the current active project
        
        Args:
            project_path: Path to project directory
            
        Returns:
            dict: Project information
        """
        project_path = str(Path(project_path).resolve())
        
        # Load existing projects
        projects = cls._load_projects()
        
        # Get project name from path
        project_name = Path(project_path).name
        
        # Check if project already exists
        if project_name in projects:
            project_info = projects[project_name]
            project_info["last_accessed"] = datetime.now().isoformat()
        else:
            # Create new project entry
            project_info = {
                "id": project_name,
                "name": project_name,
                "path": project_path,
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "features_added": []
            }
            projects[project_name] = project_info
        
        # Save updated projects
        cls._save_projects(projects)
        
        # Set as current project
        cls._save_current_project(project_info)
        
        return project_info
    
    @classmethod
    def get_current_project(cls):
        """
        Get the current active project
        
        Returns:
            dict or None: Current project info or None if no project set
        """
        return cls._load_current_project()
    
    @classmethod
    def list_all_projects(cls):
        """
        List all registered projects
        
        Returns:
            dict: All projects
        """
        return cls._load_projects()
    
    @classmethod
    def add_feature(cls, project_path, feature_description, files_changed):
        """
        Add a feature to project history
        
        Args:
            project_path: Path to project
            feature_description: Description of the feature
            files_changed: List of files that were modified/created
        """
        project_path = str(Path(project_path).resolve())
        projects = cls._load_projects()
        
        project_name = Path(project_path).name
        
        if project_name in projects:
            feature_entry = {
                "name": feature_description,
                "added_at": datetime.now().isoformat(),
                "files_changed": files_changed
            }
            
            projects[project_name]["features_added"].append(feature_entry)
            projects[project_name]["last_accessed"] = datetime.now().isoformat()
            
            cls._save_projects(projects)
            
            # Update current project if it's the active one
            current = cls._load_current_project()
            if current and current.get("name") == project_name:
                cls._save_current_project(projects[project_name])
    
    @classmethod
    def get_project_features(cls, project_path):
        """
        Get all features added to a project
        
        Args:
            project_path: Path to project
            
        Returns:
            list: List of features
        """
        project_path = str(Path(project_path).resolve())
        projects = cls._load_projects()
        
        project_name = Path(project_path).name
        
        if project_name in projects:
            return projects[project_name].get("features_added", [])
        
        return []
    
    @classmethod
    def remove_project(cls, project_path):
        """
        Remove a project from tracking
        
        Args:
            project_path: Path to project
        """
        project_path = str(Path(project_path).resolve())
        projects = cls._load_projects()
        
        project_name = Path(project_path).name
        
        if project_name in projects:
            del projects[project_name]
            cls._save_projects(projects)
            
            # Clear current project if it was removed
            current = cls._load_current_project()
            if current and current.get("name") == project_name:
                if cls.CURRENT_PROJECT_FILE.exists():
                    cls.CURRENT_PROJECT_FILE.unlink()
