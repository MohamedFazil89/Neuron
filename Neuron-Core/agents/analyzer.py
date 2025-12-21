import os
import json
import re
from pathlib import Path
from collections import defaultdict

# Directories to exclude from analysis
EXCLUDED_DIRS = {
    'node_modules', 'build', 'dist', '.git', '.next', 'coverage',
    '__pycache__', '.venv', 'venv', 'env', '.pytest_cache',
    '.idea', '.vscode', '.cache', 'tmp', 'temp'
}

# Tech stack signatures
TECH_SIGNATURES = {
    # Frontend Frameworks
    'react': {
        'package_deps': ['react', 'react-dom'],
        'file_patterns': ['*.jsx', '*.tsx'],
        'imports': ['from react', 'from "react"', "from 'react'"],
        'type': 'frontend'
    },
    'vue': {
        'package_deps': ['vue'],
        'file_patterns': ['*.vue'],
        'imports': ['from vue', 'from "vue"', "from 'vue'"],
        'type': 'frontend'
    },
    'angular': {
        'package_deps': ['@angular/core'],
        'file_patterns': ['*.component.ts', '*.module.ts'],
        'imports': ['from @angular'],
        'type': 'frontend'
    },
    'svelte': {
        'package_deps': ['svelte'],
        'file_patterns': ['*.svelte'],
        'type': 'frontend'
    },
    'next.js': {
        'package_deps': ['next'],
        'file_patterns': ['pages/**/*.js', 'pages/**/*.tsx', 'app/**/*.tsx'],
        'config_files': ['next.config.js', 'next.config.mjs'],
        'type': 'frontend'
    },
    
    # Backend Frameworks
    'express': {
        'package_deps': ['express'],
        'imports': ['from express', 'require("express")', "require('express')"],
        'type': 'backend'
    },
    'fastapi': {
        'file_patterns': ['*.py'],
        'imports': ['from fastapi', 'import fastapi'],
        'type': 'backend'
    },
    'django': {
        'file_patterns': ['*.py'],
        'imports': ['from django', 'import django'],
        'config_files': ['manage.py', 'settings.py'],
        'type': 'backend'
    },
    'flask': {
        'file_patterns': ['*.py'],
        'imports': ['from flask', 'import flask'],
        'type': 'backend'
    },
    'nest.js': {
        'package_deps': ['@nestjs/core'],
        'imports': ['from @nestjs'],
        'type': 'backend'
    },
    'koa': {
        'package_deps': ['koa'],
        'imports': ['from koa', 'require("koa")', "require('koa')"],
        'type': 'backend'
    },
    
    # Languages
    'typescript': {
        'file_patterns': ['*.ts', '*.tsx'],
        'config_files': ['tsconfig.json'],
        'type': 'language'
    },
    'python': {
        'file_patterns': ['*.py'],
        'config_files': ['requirements.txt', 'setup.py', 'pyproject.toml'],
        'type': 'language'
    },
    'javascript': {
        'file_patterns': ['*.js', '*.jsx', '*.mjs'],
        'type': 'language'
    },
    
    # State Management
    'redux': {
        'package_deps': ['redux', '@reduxjs/toolkit', 'react-redux'],
        'type': 'state_management'
    },
    'zustand': {
        'package_deps': ['zustand'],
        'type': 'state_management'
    },
    'mobx': {
        'package_deps': ['mobx', 'mobx-react'],
        'type': 'state_management'
    },
    
    # Styling
    'tailwind': {
        'package_deps': ['tailwindcss'],
        'config_files': ['tailwind.config.js', 'tailwind.config.ts'],
        'type': 'styling'
    },
    'styled-components': {
        'package_deps': ['styled-components'],
        'type': 'styling'
    },
    'sass': {
        'package_deps': ['sass', 'node-sass'],
        'file_patterns': ['*.scss', '*.sass'],
        'type': 'styling'
    },
    
    # Databases
    'mongodb': {
        'package_deps': ['mongodb', 'mongoose'],
        'type': 'database'
    },
    'postgresql': {
        'package_deps': ['pg', 'postgres', 'psycopg2'],
        'type': 'database'
    },
    'mysql': {
        'package_deps': ['mysql', 'mysql2'],
        'type': 'database'
    },
    'prisma': {
        'package_deps': ['prisma', '@prisma/client'],
        'config_files': ['prisma/schema.prisma'],
        'type': 'orm'
    },
    'sequelize': {
        'package_deps': ['sequelize'],
        'type': 'orm'
    },
    
    # Testing
    'jest': {
        'package_deps': ['jest'],
        'config_files': ['jest.config.js', 'jest.config.ts'],
        'type': 'testing'
    },
    'vitest': {
        'package_deps': ['vitest'],
        'type': 'testing'
    },
    'pytest': {
        'package_deps': ['pytest'],
        'type': 'testing'
    },
}

def should_exclude_path(path):
    """Check if path should be excluded from analysis"""
    parts = Path(path).parts
    return any(excluded in parts for excluded in EXCLUDED_DIRS)

def detect_tech_from_package_json(package_json):
    """Detect technologies from package.json"""
    detected = []
    if not package_json:
        return detected
    
    all_deps = {}
    if 'dependencies' in package_json:
        all_deps.update(package_json['dependencies'])
    if 'devDependencies' in package_json:
        all_deps.update(package_json['devDependencies'])
    
    for tech, signature in TECH_SIGNATURES.items():
        if 'package_deps' in signature:
            for dep in signature['package_deps']:
                if dep in all_deps:
                    detected.append(tech)
                    break
    
    return detected

def detect_tech_from_files(project_root):
    """Detect technologies from file patterns and imports"""
    detected = defaultdict(int)
    
    # Check for config files
    for tech, signature in TECH_SIGNATURES.items():
        if 'config_files' in signature:
            for config_file in signature['config_files']:
                if (project_root / config_file).exists() or list(project_root.glob(f"**/{config_file}")):
                    detected[tech] += 10
    
    # Scan all relevant files
    for file_path in project_root.rglob('*'):
        if file_path.is_file() and not should_exclude_path(str(file_path)):
            try:
                # Check file extensions
                suffix = file_path.suffix
                for tech, signature in TECH_SIGNATURES.items():
                    if 'file_patterns' in signature:
                        for pattern in signature['file_patterns']:
                            if pattern.endswith(suffix):
                                detected[tech] += 1
                
                # Check imports in files
                if file_path.stat().st_size < 500000:  # Skip large files
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            for tech, signature in TECH_SIGNATURES.items():
                                if 'imports' in signature:
                                    for import_pattern in signature['imports']:
                                        if import_pattern.lower() in content.lower():
                                            detected[tech] += 5
                                            break
                    except:
                        pass
            except:
                pass
    
    return detected

def categorize_file(file_path, content_sample=None):
    """Intelligently categorize a file based on its path and content"""
    path_lower = file_path.lower()
    
    # Backend patterns
    if any(x in path_lower for x in ['routes', 'router', 'api', 'endpoints']):
        return 'routes'
    if any(x in path_lower for x in ['model', 'schema', 'entity']):
        return 'models'
    if any(x in path_lower for x in ['controller', 'handler']):
        return 'controllers'
    if any(x in path_lower for x in ['middleware', 'guard', 'interceptor']):
        return 'middleware'
    if any(x in path_lower for x in ['service', 'repository', 'dao']):
        return 'services'
    if any(x in path_lower for x in ['util', 'helper', 'lib']):
        return 'utilities'
    
    # Frontend patterns
    if any(x in path_lower for x in ['component']):
        return 'components'
    if any(x in path_lower for x in ['page', 'view', 'screen']):
        return 'pages'
    if any(x in path_lower for x in ['hook']):
        return 'hooks'
    if any(x in path_lower for x in ['store', 'state', 'redux', 'zustand']):
        return 'state'
    if any(x in path_lower for x in ['style', 'css', 'scss', 'sass']):
        return 'styles'
    if any(x in path_lower for x in ['context']):
        return 'contexts'
    
    # Test files
    if any(x in path_lower for x in ['test', 'spec', '__tests__']):
        return 'tests'
    
    # Config files
    if any(x in path_lower for x in ['config', 'setting']):
        return 'config'
    
    return 'other'

def analyze_project_structure(project_root):
    """Dynamically analyze project structure"""
    structure = defaultdict(lambda: defaultdict(list))
    
    for file_path in project_root.rglob('*'):
        if file_path.is_file() and not should_exclude_path(str(file_path)):
            relative_path = str(file_path.relative_to(project_root)).replace("\\", "/")
            
            # Determine if frontend or backend based on tech and location
            category = categorize_file(relative_path)
            
            # Determine domain (frontend/backend)
            if any(x in relative_path.lower() for x in ['client', 'frontend', 'ui', 'public', 'src/components', 'src/pages']):
                domain = 'frontend'
            elif any(x in relative_path.lower() for x in ['server', 'backend', 'api', 'src/routes', 'src/controllers']):
                domain = 'backend'
            else:
                # Auto-detect based on file type and category
                if file_path.suffix in ['.jsx', '.tsx', '.vue', '.svelte']:
                    domain = 'frontend'
                elif category in ['routes', 'models', 'controllers', 'middleware']:
                    domain = 'backend'
                elif file_path.suffix == '.py':
                    domain = 'backend'
                else:
                    domain = 'shared'
            
            if category not in structure[domain]:
              structure[domain][category] = []
              structure[domain][category].append(relative_path)
    
    return structure

def analyze_project(project_path):
    """
    Advanced AI-powered project analysis with dynamic tech stack detection.
    
    Input: project_path (str) - absolute path to project root
    Output: dict - comprehensive project analysis
    """
    
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")
    
    print(f"[AI ANALYZER] 🔍 Scanning project: {project_path}")
    
    project_root = Path(project_path)
    
    # Initialize analysis structure
    analysis = {
        "project_path": project_path,
        "tech_stack": {
            "frontend": {},
            "backend": {},
            "database": {},
            "language": {},
            "styling": {},
            "state_management": {},
            "testing": {},
            "orm": {},
            "other": {}
        },
        "backend": {
            "exists": False,
            "detected_framework": None,
            "structure": {},
            "files": []
        },
        "frontend": {
            "exists": False,
            "detected_framework": None,
            "structure": {},
            "files": []
        },
        "shared": {
            "structure": {},
            "files": []
        },
        "package_json": None,
        "requirements_txt": None,
        "env_files": [],
        "file_contents": {}
    }
    
    # Read package.json
    package_json_path = project_root / "package.json"
    if package_json_path.exists():
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                analysis["package_json"] = json.load(f)
        except:
            analysis["package_json"] = {"error": "Could not parse package.json"}
    
    # Read requirements.txt (Python)
    requirements_path = project_root / "requirements.txt"
    if requirements_path.exists():
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                analysis["requirements_txt"] = f.read().splitlines()
        except:
            pass
    
    # Detect technologies
    print("[AI ANALYZER] 🤖 Detecting tech stack...")
    
    detected_from_package = detect_tech_from_package_json(analysis["package_json"])
    detected_from_files = detect_tech_from_files(project_root)
    
    # Combine detections
    all_detected = set(detected_from_package)
    for tech, count in detected_from_files.items():
        if count >= 3:  # Threshold for confidence
            all_detected.add(tech)
    
    # Categorize detected technologies
    for tech in all_detected:
        if tech in TECH_SIGNATURES:
            tech_type = TECH_SIGNATURES[tech]['type']
            confidence = "high" if tech in detected_from_package else "medium"
            analysis["tech_stack"][tech_type][tech] = {
                "detected": True,
                "confidence": confidence,
                "count": detected_from_files.get(tech, 0)
            }
    
    # Determine primary frameworks
    frontend_frameworks = [t for t, s in TECH_SIGNATURES.items() if s['type'] == 'frontend' and t in all_detected]
    backend_frameworks = [t for t, s in TECH_SIGNATURES.items() if s['type'] == 'backend' and t in all_detected]
    
    if frontend_frameworks:
        analysis["frontend"]["detected_framework"] = frontend_frameworks[0]
        analysis["frontend"]["exists"] = True
    
    if backend_frameworks:
        analysis["backend"]["detected_framework"] = backend_frameworks[0]
        analysis["backend"]["exists"] = True
    
    # Analyze project structure dynamically
    print("[AI ANALYZER] 📂 Analyzing project structure...")
    structure = analyze_project_structure(project_root)
    
    # Populate backend/frontend/shared structures
    for domain in ['frontend', 'backend', 'shared']:
        if domain in structure:
            analysis[domain]["structure"] = dict(structure[domain])
            for category, files in structure[domain].items():
                analysis[domain]["files"].extend(files)
    
    # Read file contents (sample for context)
    print("[AI ANALYZER] 📖 Reading file contents...")
    for domain in ['frontend', 'backend', 'shared']:
        for file_path in analysis[domain]["files"][:50]:  # Limit to first 50 files
            full_path = project_root / file_path
            if full_path.exists() and full_path.stat().st_size < 100000:
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        if "file_contents" not in analysis:
                           analysis["file_contents"] = {}
                           analysis["file_contents"][file_path] = f.read()
                except:
                    pass
    
    # Check for env files
    env_files = [".env", ".env.local", ".env.development", ".env.production"]
    for env_file in env_files:
        if (project_root / env_file).exists():
            analysis["env_files"].append(env_file)
    
    # Summary
    print(f"\n[AI ANALYZER] ✅ Analysis Complete!")
    print(f"  Frontend: {'✓ ' + analysis['frontend']['detected_framework'] if analysis['frontend']['exists'] else '✗ Not detected'}")
    print(f"  Backend: {'✓ ' + analysis['backend']['detected_framework'] if analysis['backend']['exists'] else '✗ Not detected'}")
    print(f"  Files: {len(analysis['frontend']['files'])} frontend, {len(analysis['backend']['files'])} backend")
    print(f"  Tech Stack: {len([t for cat in analysis['tech_stack'].values() for t in cat])} technologies detected")
    
    return analysis


def get_existing_file_path(analysis, target_file):
    """Check if a file already exists in the project"""
    target_file = target_file.replace("\\", "/")
    
    for domain in ['backend', 'frontend', 'shared']:
        for file_path in analysis[domain]["files"]:
            if file_path.endswith(target_file) or file_path == target_file:
                return file_path
    
    return None


def should_modify_file(analysis, file_path):
    """
    Determine if a file should be modified or created new.
    Returns: ("modify", existing_content) or ("create", None)
    """
    normalized_path = file_path.replace("\\", "/")
    existing = get_existing_file_path(analysis, normalized_path)
    
    if existing and existing in analysis["file_contents"]:
        return ("modify", analysis["file_contents"][existing])
    
    return ("create", None)


def get_analysis_summary(analysis):
    """
    Generate a clean summary of the analysis for API responses.
    Removes large file contents and formats data for frontend consumption.
    """
    summary = {
        "project_path": analysis["project_path"],
        "tech_stack": {
            "frontend": {},
            "backend": {},
            "database": {},
            "language": {},
            "styling": {},
            "state_management": {},
            "testing": {},
            "orm": {},
            "other": {}
        },
        "backend": {
            "exists": analysis["backend"]["exists"],
            "detected_framework": analysis["backend"]["detected_framework"],
            "structure": {},
            "file_count": len(analysis["backend"]["files"]),
            "files": analysis["backend"]["files"][:100]  # Limit files in response
        },
        "frontend": {
            "exists": analysis["frontend"]["exists"],
            "detected_framework": analysis["frontend"]["detected_framework"],
            "structure": {},
            "file_count": len(analysis["frontend"]["files"]),
            "files": analysis["frontend"]["files"][:100]
        },
        "shared": {
            "structure": {},
            "file_count": len(analysis["shared"]["files"]),
            "files": analysis["shared"]["files"][:50]
        },
        "has_package_json": analysis["package_json"] is not None,
        "has_requirements_txt": analysis["requirements_txt"] is not None,
        "env_files": analysis["env_files"]
    }
    
    # Copy tech stack with cleaner format
    for category, techs in analysis["tech_stack"].items():
        summary["tech_stack"][category] = {
            tech: details["confidence"] 
            for tech, details in techs.items()
        }
    
    # Copy structure summaries (just counts, not full file lists)
    for domain in ['backend', 'frontend', 'shared']:
        for category, files in analysis[domain]["structure"].items():
            summary[domain]["structure"][category] = {
                "count": len(files),
                "files": files[:20]  # Sample files
            }
    
    return summary