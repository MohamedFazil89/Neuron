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
        recommendations = ProjectAnalyzer._generate_recommendations(issues)
        
        # Summary
        summary = {
            "total_backend_files": len(analysis["backend"]["files"]),
            "total_frontend_files": len(analysis["frontend"]["files"]),
            "has_package_json": analysis["package_json"] is not None,
            "issues_found": len(issues),
            "severity": ProjectAnalyzer._calculate_severity(issues)
        }
        
        print(f"[PROJECT_ANALYZER] ✓ Analysis complete")
        print(f"  Backend files: {summary['total_backend_files']}")
        print(f"  Frontend files: {summary['total_frontend_files']}")
        print(f"  Issues: {summary['issues_found']}")
        
        return {
            "status": "success",
            "summary": summary,
            "analysis": {
                "backend": {
                    "files": analysis["backend"]["files"],
                    "routes": analysis["backend"]["routes"],
                    "controllers": analysis["backend"]["controllers"],
                    "models": analysis["backend"]["models"],
                    "middleware": analysis["backend"]["middleware"]
                },
                "frontend": {
                    "files": analysis["frontend"]["files"],
                    "components": analysis["frontend"]["components"],
                    "pages": analysis["frontend"]["pages"],
                    "hooks": analysis["frontend"]["hooks"]
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
        
        # Issue 1: Unused imports
        for file_path, content in analysis.get("file_contents", {}).items():
            if not content:
                issues.append({
                    "type": "empty_file",
                    "severity": "warning",
                    "file": file_path,
                    "description": "File is empty or has no content"
                })
        
        # Issue 2: Missing package.json
        if analysis["package_json"] is None:
            issues.append({
                "type": "missing_package_json",
                "severity": "critical",
                "file": "package.json",
                "description": "package.json not found. Project dependencies unclear."
            })
        
        # Issue 3: Missing .env
        if not analysis.get("env_files"):
            issues.append({
                "type": "no_env_file",
                "severity": "warning",
                "file": ".env",
                "description": "No .env file found. Environment variables may not be configured."
            })
        
        # Issue 4: Orphaned files (files not in any category)
        all_categorized = set(
            analysis["backend"]["files"] + 
            analysis["frontend"]["files"]
        )
        
        all_files = set(analysis.get("all_source_files", {}).get("js", []) +
                       analysis.get("all_source_files", {}).get("jsx", []) +
                       analysis.get("all_source_files", {}).get("ts", []) +
                       analysis.get("all_source_files", {}).get("tsx", []))
        
        orphaned = all_files - all_categorized
        for file in orphaned:
            if not file.startswith('node_modules'):
                issues.append({
                    "type": "orphaned_file",
                    "severity": "info",
                    "file": file,
                    "description": "File not recognized as backend or frontend component"
                })
        
        return issues
    
    @staticmethod
    def _generate_recommendations(issues):
        """Generate actionable recommendations"""
        
        recommendations = []
        
        for issue in issues:
            if issue["type"] == "empty_file":
                recommendations.append(f"Remove empty file: {issue['file']}")
            elif issue["type"] == "missing_package_json":
                recommendations.append("Run 'npm init' to create package.json")
            elif issue["type"] == "no_env_file":
                recommendations.append("Create .env file with required environment variables")
            elif issue["type"] == "orphaned_file":
                recommendations.append(f"Review {issue['file']} - may be unused or miscategorized")
        
        return recommendations
    
    @staticmethod
    def _calculate_severity(issues):
        """Calculate overall severity"""
        
        if not issues:
            return "healthy"
        
        critical_count = len([i for i in issues if i["severity"] == "critical"])
        warning_count = len([i for i in issues if i["severity"] == "warning"])
        
        if critical_count > 0:
            return "critical"
        elif warning_count > 0:
            return "warning"
        else:
            return "info"