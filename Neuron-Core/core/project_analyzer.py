# core/project_analyzer.py
import os
from pathlib import Path
from agents.analyzer import analyze_project

class ProjectAnalyzer:
    """
    Analyze existing project for:
    - Unused files
    - Broken imports
    - Orphaned code
    - Code quality metrics
    """
    
    @staticmethod
    def verify_project(project_path):
        """
        Comprehensive project verification
        
        Returns:
            {
                "status": "success",
                "summary": {...},
                "files": {
                    "backend": {...},
                    "frontend": {...}
                },
                "issues": [...],
                "recommendations": [...]
            }
        """
        
        if not os.path.isdir(project_path):
            return {
                "status": "error",
                "message": f"Project path does not exist: {project_path}"
            }
        
        print(f"[PROJECT_ANALYZER] Verifying: {project_path}")
        
        # Analyze project
        analysis = analyze_project(project_path)
        
        # Check for issues
        issues = ProjectAnalyzer._find_issues(analysis, project_path)
        recommendations = ProjectAnalyzer._generate_recommendations(issues, analysis)
        
        # Summary
        summary = {
            "total_backend_files": len(analysis["backend"]["files"]),
            "total_frontend_files": len(analysis["frontend"]["files"]),
            "has_package_json": analysis["package_json"] is not None,
            "has_requirements_txt": analysis["requirements_txt"] is not None,
            "issues_found": len(issues),
            "severity": ProjectAnalyzer._calculate_severity(issues),
            "tech_stack_detected": len([t for cat in analysis['tech_stack'].values() for t in cat]),
            "backend_framework": analysis["backend"]["detected_framework"],
            "frontend_framework": analysis["frontend"]["detected_framework"]
        }
        
        print(f"[PROJECT_ANALYZER] Analysis complete")
        print(f"  Backend files: {summary['total_backend_files']}")
        print(f"  Frontend files: {summary['total_frontend_files']}")
        print(f"  Issues: {summary['issues_found']}")
        
        return {
            "status": "success",
            "summary": summary,
            "analysis": {
                "tech_stack": analysis["tech_stack"],
                "backend": {
                    "exists": analysis["backend"]["exists"],
                    "detected_framework": analysis["backend"]["detected_framework"],
                    "files": analysis["backend"]["files"],
                    "structure": analysis["backend"]["structure"],
                    "file_count": len(analysis["backend"]["files"])
                },
                "frontend": {
                    "exists": analysis["frontend"]["exists"],
                    "detected_framework": analysis["frontend"]["detected_framework"],
                    "files": analysis["frontend"]["files"],
                    "structure": analysis["frontend"]["structure"],
                    "file_count": len(analysis["frontend"]["files"])
                },
                "shared": {
                    "files": analysis["shared"]["files"],
                    "structure": analysis["shared"]["structure"]
                },
                "env_files": analysis.get("env_files", [])
            },
            "issues": issues,
            "recommendations": recommendations
        }
    
    @staticmethod
    def _find_issues(analysis, project_path):
        """Find problems in project"""
        
        issues = []
        project_root = Path(project_path)
        
        # Issue 1: Empty files
        for file_path, content in analysis.get("file_contents", {}).items():
            if not content or len(content.strip()) == 0:
                issues.append({
                    "type": "empty_file",
                    "severity": "warning",
                    "file": file_path,
                    "description": "File is empty or has no content"
                })
        
        # Issue 2: Missing package.json (for JS projects)
        if analysis["package_json"] is None and analysis["frontend"]["exists"]:
            issues.append({
                "type": "missing_package_json",
                "severity": "critical",
                "file": "package.json",
                "description": "package.json not found. Project dependencies unclear."
            })
        
        # Issue 3: Missing requirements.txt (for Python projects)
        if analysis["requirements_txt"] is None and analysis["backend"]["detected_framework"] in ['django', 'flask', 'fastapi']:
            issues.append({
                "type": "missing_requirements",
                "severity": "warning",
                "file": "requirements.txt",
                "description": "requirements.txt not found for Python project."
            })
        
        # Issue 4: Missing .env
        if not analysis.get("env_files"):
            issues.append({
                "type": "no_env_file",
                "severity": "warning",
                "file": ".env",
                "description": "No .env file found. Environment variables may not be configured."
            })
        
        # Issue 5: No testing framework
        if not analysis["tech_stack"]["testing"]:
            issues.append({
                "type": "no_testing",
                "severity": "warning",
                "file": "N/A",
                "description": "No testing framework detected. Consider adding tests."
            })
        
        # Issue 6: Large files (potential code smell)
        for file_path, content in analysis.get("file_contents", {}).items():
            if content and len(content.splitlines()) > 500:
                issues.append({
                    "type": "large_file",
                    "severity": "info",
                    "file": file_path,
                    "description": f"File has {len(content.splitlines())} lines. Consider splitting into smaller modules."
                })
        
        # Issue 7: No backend detected but has frontend
        if analysis["frontend"]["exists"] and not analysis["backend"]["exists"]:
            issues.append({
                "type": "frontend_only",
                "severity": "info",
                "file": "N/A",
                "description": "Frontend-only application detected. This is fine for static sites or SPAs."
            })
        
        # Issue 8: No frontend detected but has backend
        if analysis["backend"]["exists"] and not analysis["frontend"]["exists"]:
            issues.append({
                "type": "backend_only",
                "severity": "info",
                "file": "N/A",
                "description": "Backend-only API detected. This is fine for REST APIs or microservices."
            })
        
        # Issue 9: Neither frontend nor backend detected
        if not analysis["backend"]["exists"] and not analysis["frontend"]["exists"]:
            issues.append({
                "type": "no_framework",
                "severity": "warning",
                "file": "N/A",
                "description": "No clear frontend or backend framework detected. May be a library or utility project."
            })
        
        # Issue 10: Inconsistent file organization
        backend_structure = analysis["backend"]["structure"]
        if backend_structure:
            other_category = backend_structure.get("other", [])
            other_count = len(other_category) if isinstance(other_category, list) else other_category.get("count", 0)
            
            if len(analysis["backend"]["files"]) > 0 and other_count > len(analysis["backend"]["files"]) * 0.3:
                issues.append({
                    "type": "unorganized_backend",
                    "severity": "info",
                    "file": "N/A",
                    "description": "Many backend files are uncategorized. Consider organizing into routes, models, controllers."
                })
        
        frontend_structure = analysis["frontend"]["structure"]
        if frontend_structure:
            other_category = frontend_structure.get("other", [])
            other_count = len(other_category) if isinstance(other_category, list) else other_category.get("count", 0)
            
            if len(analysis["frontend"]["files"]) > 0 and other_count > len(analysis["frontend"]["files"]) * 0.3:
                issues.append({
                    "type": "unorganized_frontend",
                    "severity": "info",
                    "file": "N/A",
                    "description": "Many frontend files are uncategorized. Consider organizing into components, pages, hooks."
                })
        
        return issues
    
    @staticmethod
    def _generate_recommendations(issues, analysis):
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Group issues by type
        issue_types = {}
        for issue in issues:
            issue_type = issue["type"]
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(issue)
        
        # Generate recommendations based on issues
        if "empty_file" in issue_types:
            count = len(issue_types["empty_file"])
            recommendations.append(f"Remove or populate {count} empty file(s)")
        
        if "missing_package_json" in issue_types:
            recommendations.append("Run 'npm init' to create package.json and manage dependencies")
        
        if "missing_requirements" in issue_types:
            recommendations.append("Create requirements.txt with: pip freeze > requirements.txt")
        
        if "no_env_file" in issue_types:
            recommendations.append("Create .env file with required environment variables (API keys, DB URLs, etc.)")
        
        if "no_testing" in issue_types:
            frontend_framework = analysis["frontend"]["detected_framework"]
            backend_framework = analysis["backend"]["detected_framework"]
            
            if frontend_framework == "react":
                recommendations.append("Add testing with Jest and React Testing Library: npm install --save-dev jest @testing-library/react")
            elif backend_framework == "express":
                recommendations.append("Add testing with Jest and Supertest: npm install --save-dev jest supertest")
            elif backend_framework in ["django", "flask", "fastapi"]:
                recommendations.append("Add testing with pytest: pip install pytest pytest-cov")
        
        if "large_file" in issue_types:
            count = len(issue_types["large_file"])
            recommendations.append(f"Refactor {count} large file(s) into smaller, more maintainable modules")
        
        if "unorganized_backend" in issue_types:
            recommendations.append("Organize backend files into clear directories: routes/, controllers/, models/, middleware/")
        
        if "unorganized_frontend" in issue_types:
            recommendations.append("Organize frontend files into clear directories: components/, pages/, hooks/, utils/")
        
        # Tech stack recommendations
        tech_stack = analysis["tech_stack"]
        
        if analysis["frontend"]["exists"] and not tech_stack.get("styling"):
            recommendations.append("Consider adding a styling solution like Tailwind CSS or Styled Components")
        
        if analysis["frontend"]["exists"] and not tech_stack.get("state_management") and len(analysis["frontend"]["files"]) > 20:
            recommendations.append("For larger apps, consider adding state management (Redux, Zustand, or Context API)")
        
        if analysis["backend"]["exists"] and not tech_stack.get("database") and not tech_stack.get("orm"):
            recommendations.append("Consider adding a database layer if your app needs data persistence")
        
        if "typescript" not in tech_stack.get("language", {}):
            recommendations.append("Consider migrating to TypeScript for better type safety and developer experience")
        
        # If no major issues, add positive recommendations
        if len(issues) <= 2:
            recommendations.append("Project structure looks good! Keep maintaining code quality.")
        
        return recommendations
    
    @staticmethod
    def _calculate_severity(issues):
        """Calculate overall severity"""
        
        if not issues:
            return "healthy"
        
        critical_count = len([i for i in issues if i["severity"] == "critical"])
        warning_count = len([i for i in issues if i["severity"] == "warning"])
        info_count = len([i for i in issues if i["severity"] == "info"])
        
        if critical_count > 0:
            return "critical"
        elif warning_count > 3:
            return "warning"
        elif warning_count > 0 or info_count > 0:
            return "info"
        else:
            return "healthy"