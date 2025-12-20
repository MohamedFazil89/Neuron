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

def analyze_project(project_path):
    """
    Analyze existing project structure and return a comprehensive report.
    
    Input: project_path (str) - absolute path to project root
    Output: dict - project structure analysis
    """
    
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")
    
    print(f"[ANALYZER] Scanning project: {project_path}")
    
    analysis = {
        "project_path": project_path,
        "backend": {
            "exists": False,
            "structure": {},
            "files": [],
            "routes": [],
            "models": [],
            "controllers": [],
            "middleware": []
        },
        "frontend": {
            "exists": False,
            "structure": {},
            "files": [],
            "components": [],
            "pages": [],
            "hooks": [],
            "services": []
        },
        "package_json": None,
        "env_files": []
    }
    
    project_root = Path(project_path)
    
    # Scan for backend files (excluding node_modules, etc.)
    backend_patterns = {
        "routes": ["routes/**/*.js", "routes/**/*.ts", "src/routes/**/*.js", "src/routes/**/*.ts"],
        "models": ["models/**/*.js", "models/**/*.ts", "src/models/**/*.js", "src/models/**/*.ts"],
        "controllers": ["controllers/**/*.js", "controllers/**/*.ts", "src/controllers/**/*.js", "src/controllers/**/*.ts"],
        "middleware": ["middleware/**/*.js", "middleware/**/*.ts", "src/middleware/**/*.js", "src/middleware/**/*.ts"]
    }
    
    # Scan for frontend files
    frontend_patterns = {
        "components": [
            "components/**/*.jsx", "components/**/*.tsx", "components/**/*.js",
            "src/components/**/*.jsx", "src/components/**/*.tsx", "src/components/**/*.js"
        ],
        "pages": [
            "pages/**/*.jsx", "pages/**/*.tsx", "pages/**/*.js",
            "src/pages/**/*.jsx", "src/pages/**/*.tsx", "src/pages/**/*.js"
        ],
        "hooks": [
            "hooks/**/*.js", "hooks/**/*.jsx", "hooks/**/*.ts",
            "src/hooks/**/*.js", "src/hooks/**/*.jsx", "src/hooks/**/*.ts"
        ],
        "services": [
            "services/**/*.js", "services/**/*.ts",
            "src/services/**/*.js", "src/services/**/*.ts"
        ]
    }
    
    # Check backend
    for category, patterns in backend_patterns.items():
        files = []
        for pattern in patterns:
            for file_path in project_root.glob(pattern):
                relative_path = str(file_path.relative_to(project_root))
                if not should_exclude_path(relative_path):
                    files.append(relative_path.replace("\\", "/"))
        
        if files:
            analysis["backend"]["exists"] = True
            analysis["backend"][category] = files
            analysis["backend"]["files"].extend(files)
    
    # Check frontend
    for category, patterns in frontend_patterns.items():
        files = []
        for pattern in patterns:
            for file_path in project_root.glob(pattern):
                relative_path = str(file_path.relative_to(project_root))
                if not should_exclude_path(relative_path):
                    files.append(relative_path.replace("\\", "/"))
        
        if files:
            analysis["frontend"]["exists"] = True
            analysis["frontend"][category] = files
            analysis["frontend"]["files"].extend(files)
    
    # Remove duplicates
    analysis["backend"]["files"] = list(set(analysis["backend"]["files"]))
    analysis["frontend"]["files"] = list(set(analysis["frontend"]["files"]))
    
    # Check package.json
    package_json_path = project_root / "package.json"
    if package_json_path.exists():
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                analysis["package_json"] = json.load(f)
        except:
            analysis["package_json"] = {"error": "Could not parse package.json"}
    
    # Check for env files
    env_files = [".env", ".env.local", ".env.development", ".env.production"]
    for env_file in env_files:
        env_path = project_root / env_file
        if env_path.exists():
            analysis["env_files"].append(env_file)
    
    # Read file contents for context (only source files, not node_modules)
    analysis["file_contents"] = {}
    
    # Read backend files
    for file_path in analysis["backend"]["files"]:
        full_path = project_root / file_path
        if full_path.exists() and full_path.stat().st_size < 100000:  # Skip files > 100KB
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    analysis["file_contents"][file_path] = f.read()
            except:
                pass
    
    # Read frontend files
    for file_path in analysis["frontend"]["files"]:
        full_path = project_root / file_path
        if full_path.exists() and full_path.stat().st_size < 100000:
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    analysis["file_contents"][file_path] = f.read()
            except:
                pass
    
    print(f"[ANALYZER] ✓ Found {len(analysis['backend']['files'])} backend files")
    print(f"[ANALYZER] ✓ Found {len(analysis['frontend']['files'])} frontend files")
    
    return analysis


def get_existing_file_path(analysis, target_file):
    """
    Check if a file already exists in the project.
    Returns: file_path if exists, None otherwise
    """
    # Normalize path
    target_file = target_file.replace("\\", "/")
    
    # Check in backend files
    for file_path in analysis["backend"]["files"]:
        if file_path.endswith(target_file) or file_path == target_file:
            return file_path
    
    # Check in frontend files
    for file_path in analysis["frontend"]["files"]:
        if file_path.endswith(target_file) or file_path == target_file:
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
