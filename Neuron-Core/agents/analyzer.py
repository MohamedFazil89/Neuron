# agents/analyzer.py
import os
import json
from pathlib import Path

# Directories to exclude from analysis
EXCLUDED_DIRS = {
    'node_modules',
    'build',
    'dist',
    '.git',
    '.next',
    'coverage',
    '__pycache__',
    '.venv',
    'venv',
    'env',
    '.pytest_cache',
    '.idea',
    '.vscode'
}

def should_exclude_path(path):
    """Check if path should be excluded from analysis"""
    parts = Path(path).parts
    return any(excluded in parts for excluded in EXCLUDED_DIRS)

def scan_all_source_files(project_root):
    """Scan all source files in the project"""
    all_files = {
        "js": [],
        "jsx": [],
        "ts": [],
        "tsx": [],
        "json": []
    }
    
    extensions = {'.js', '.jsx', '.ts', '.tsx', '.json'}
    
    for root, dirs, files in os.walk(project_root):
        # Remove excluded directories from the walk
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in extensions:
                relative_path = file_path.relative_to(project_root)
                relative_str = str(relative_path).replace("\\", "/")
                
                ext_key = file_path.suffix[1:]  # Remove the dot
                if ext_key in all_files:
                    all_files[ext_key].append(relative_str)
    
    return all_files

def analyze_project(project_path):
    """
    Analyze existing project structure and return a comprehensive report.
    """
    
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")
    
    print(f"[ANALYZER] Scanning project: {project_path}")
    
    project_root = Path(project_path)
    
    # First, scan all source files
    all_files = scan_all_source_files(project_root)
    
    print(f"[ANALYZER] Found:")
    print(f"  - {len(all_files['js'])} .js files")
    print(f"  - {len(all_files['jsx'])} .jsx files")
    print(f"  - {len(all_files['ts'])} .ts files")
    print(f"  - {len(all_files['tsx'])} .tsx files")
    
    analysis = {
        "project_path": project_path,
        "all_source_files": all_files,  # Add this for debugging
        "backend": {
            "exists": False,
            "files": [],
            "routes": [],
            "models": [],
            "controllers": [],
            "middleware": []
        },
        "frontend": {
            "exists": False,
            "files": [],
            "components": [],
            "pages": [],
            "hooks": [],
            "services": []
        },
        "package_json": None,
        "env_files": []
    }
    
    # Categorize backend files
    for file_path in all_files['js'] + all_files['ts']:
        lower_path = file_path.lower()
        
        if 'routes' in lower_path or 'route' in lower_path:
            analysis["backend"]["routes"].append(file_path)
            analysis["backend"]["files"].append(file_path)
            analysis["backend"]["exists"] = True
        elif 'models' in lower_path or 'model' in lower_path:
            analysis["backend"]["models"].append(file_path)
            analysis["backend"]["files"].append(file_path)
            analysis["backend"]["exists"] = True
        elif 'controllers' in lower_path or 'controller' in lower_path:
            analysis["backend"]["controllers"].append(file_path)
            analysis["backend"]["files"].append(file_path)
            analysis["backend"]["exists"] = True
        elif 'middleware' in lower_path:
            analysis["backend"]["middleware"].append(file_path)
            analysis["backend"]["files"].append(file_path)
            analysis["backend"]["exists"] = True
        # If it's in src/ or server/ or api/, consider it backend
        elif any(x in lower_path for x in ['src/server', 'src/api', 'server/', 'api/']):
            analysis["backend"]["files"].append(file_path)
            analysis["backend"]["exists"] = True
    
    # Categorize frontend files
    for file_path in all_files['jsx'] + all_files['tsx'] + all_files['js'] + all_files['ts']:
        lower_path = file_path.lower()
        
        if 'components' in lower_path or 'component' in lower_path:
            analysis["frontend"]["components"].append(file_path)
            analysis["frontend"]["files"].append(file_path)
            analysis["frontend"]["exists"] = True
        elif 'pages' in lower_path or 'page' in lower_path:
            analysis["frontend"]["pages"].append(file_path)
            analysis["frontend"]["files"].append(file_path)
            analysis["frontend"]["exists"] = True
        elif 'hooks' in lower_path or 'hook' in lower_path:
            analysis["frontend"]["hooks"].append(file_path)
            analysis["frontend"]["files"].append(file_path)
            analysis["frontend"]["exists"] = True
        elif 'services' in lower_path or 'service' in lower_path:
            analysis["frontend"]["services"].append(file_path)
            analysis["frontend"]["files"].append(file_path)
            analysis["frontend"]["exists"] = True
        # If it's a .jsx or .tsx file, it's likely frontend
        elif file_path.endswith(('.jsx', '.tsx')):
            analysis["frontend"]["files"].append(file_path)
            analysis["frontend"]["exists"] = True
    
    # Remove duplicates
    analysis["backend"]["files"] = list(set(analysis["backend"]["files"]))
    analysis["frontend"]["files"] = list(set(analysis["frontend"]["files"]))
    
    # Check package.json
    package_json_path = project_root / "package.json"
    if package_json_path.exists():
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                analysis["package_json"] = json.load(f)
        except Exception as e:
            analysis["package_json"] = {"error": f"Could not parse: {str(e)}"}
    
    # Check for env files
    env_files = [".env", ".env.local", ".env.development", ".env.production"]
    for env_file in env_files:
        env_path = project_root / env_file
        if env_path.exists():
            analysis["env_files"].append(env_file)
    
    # Read file contents for context
    analysis["file_contents"] = {}
    
    # Read all source files (backend + frontend)
    all_source_files = analysis["backend"]["files"] + analysis["frontend"]["files"]
    
    for file_path in all_source_files:
        full_path = project_root / file_path
        if full_path.exists() and full_path.stat().st_size < 100000:  # Skip large files
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    analysis["file_contents"][file_path] = f.read()
            except Exception as e:
                print(f"[ANALYZER] Could not read {file_path}: {e}")
    
    print(f"[ANALYZER] ✓ Categorized {len(analysis['backend']['files'])} backend files")
    print(f"[ANALYZER] ✓ Categorized {len(analysis['frontend']['files'])} frontend files")
    
    return analysis


def get_existing_file_path(analysis, target_file):
    """
    Check if a file already exists in the project.
    Returns: file_path if exists, None otherwise
    """
    # Normalize path
    target_file = target_file.replace("\\", "/")
    target_name = target_file.split("/")[-1]  # Get just the filename
    
    # Check in backend files
    for file_path in analysis["backend"]["files"]:
        if file_path.endswith(target_file) or file_path.endswith(target_name):
            return file_path
    
    # Check in frontend files
    for file_path in analysis["frontend"]["files"]:
        if file_path.endswith(target_file) or file_path.endswith(target_name):
            return file_path
    
    return None


def should_modify_file(analysis, file_path):
    """
    Determine if a file should be modified or created new.
    Returns: ("modify", existing_content) or ("create", None)
    """
    normalized_path = file_path.replace("\\", "/")
    
    # Check if file exists
    existing = get_existing_file_path(analysis, normalized_path)
    
    if existing and existing in analysis["file_contents"]:
        return ("modify", analysis["file_contents"][existing])
    
    return ("create", None)
