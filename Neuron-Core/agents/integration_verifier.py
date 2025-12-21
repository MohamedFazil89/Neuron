# agents/integration_verifier.py
"""
Integration Verifier Agent

Ensures generated code is properly wired into the project.
Detects orphaned files, missing imports, and broken integrations.
"""

import os
import re
from pathlib import Path
from typing import List, Dict


class IntegrationVerifier:
    """
    Verifies that generated files are properly integrated.
    """
    
    @staticmethod
    def verify_frontend_integration(project_path: str, generated_files: List[str]) -> Dict:
        """
        Verify frontend components are properly integrated.
        
        Checks:
        1. Are components imported in App.jsx or routing files?
        2. Are they actually rendered/used?
        3. Are there missing imports?
        
        Returns:
            {
                "status": "ok" | "issues_found",
                "issues": [...],
                "auto_fixable": bool,
                "fix_plan": [...]
            }
        """
        
        project_root = Path(project_path)
        issues = []
        fix_plan = []
        
        # Find main entry points
        app_jsx = IntegrationVerifier._find_file(project_root, ["App.jsx", "App.tsx", "App.js"])
        routes_file = IntegrationVerifier._find_file(project_root, ["routes.jsx", "routes.tsx", "routes.js", "index.jsx"])
        main_file = IntegrationVerifier._find_file(project_root, ["main.jsx", "main.tsx", "index.jsx", "index.tsx"])
        
        # Check each generated component
        for file_path in generated_files:
            if not any(ext in file_path for ext in ['.jsx', '.tsx', '.js']):
                continue
            
            component_name = Path(file_path).stem
            
            # Check if component is imported anywhere
            is_imported = False
            is_used = False
            
            if app_jsx and app_jsx.exists():
                app_content = app_jsx.read_text(encoding='utf-8', errors='ignore')
                
                # Check for import
                import_patterns = [
                    f"import.*{component_name}.*from",
                    f"import.*{{.*{component_name}.*}}.*from",
                ]
                
                for pattern in import_patterns:
                    if re.search(pattern, app_content, re.IGNORECASE):
                        is_imported = True
                        break
                
                # Check if component is used in JSX
                usage_patterns = [
                    f"<{component_name}",
                    f"{{{component_name}}}",
                ]
                
                for pattern in usage_patterns:
                    if pattern in app_content:
                        is_used = True
                        break
            
            # If not found in App.jsx, check routes
            if not is_imported and routes_file and routes_file.exists():
                routes_content = routes_file.read_text(encoding='utf-8', errors='ignore')
                
                import_patterns = [
                    f"import.*{component_name}.*from",
                    f"import.*{{.*{component_name}.*}}.*from",
                ]
                
                for pattern in import_patterns:
                    if re.search(pattern, routes_content, re.IGNORECASE):
                        is_imported = True
                        is_used = True  # Assume used if in routes
                        break
            
            # Report issues
            if not is_imported:
                issues.append({
                    "type": "missing_import",
                    "severity": "critical",
                    "file": file_path,
                    "component": component_name,
                    "description": f"Component '{component_name}' is not imported in any entry file",
                    "auto_fixable": True
                })
                
                fix_plan.append({
                    "action": "add_import",
                    "target_file": str(app_jsx) if app_jsx else "App.jsx",
                    "component": component_name,
                    "source": file_path
                })
            
            elif is_imported and not is_used:
                issues.append({
                    "type": "imported_but_unused",
                    "severity": "warning",
                    "file": file_path,
                    "component": component_name,
                    "description": f"Component '{component_name}' is imported but never rendered",
                    "auto_fixable": True
                })
                
                fix_plan.append({
                    "action": "add_usage",
                    "target_file": str(app_jsx) if app_jsx else "App.jsx",
                    "component": component_name
                })
        
        status = "issues_found" if issues else "ok"
        auto_fixable = all(issue.get("auto_fixable", False) for issue in issues)
        
        return {
            "status": status,
            "issues": issues,
            "auto_fixable": auto_fixable,
            "fix_plan": fix_plan
        }
    
    @staticmethod
    def verify_backend_integration(project_path: str, generated_files: List[str]) -> Dict:
        """
        Verify backend routes/controllers are properly wired.
        
        Checks:
        1. Are routes registered in main app file?
        2. Are controllers imported?
        3. Are database models registered?
        
        Returns:
            {
                "status": "ok" | "issues_found",
                "issues": [...],
                "auto_fixable": bool,
                "fix_plan": [...]
            }
        """
        
        project_root = Path(project_path)
        issues = []
        fix_plan = []
        
        # Find main backend entry point
        app_file = IntegrationVerifier._find_file(project_root, ["server.js", "app.js", "index.js", "app.py", "main.py"])
        
        if not app_file or not app_file.exists():
            return {
                "status": "warning",
                "issues": [{
                    "type": "no_entry_point",
                    "severity": "warning",
                    "description": "Cannot find main backend entry file"
                }],
                "auto_fixable": False,
                "fix_plan": []
            }
        
        app_content = app_file.read_text(encoding='utf-8', errors='ignore')
        
        # Check each generated backend file
        for file_path in generated_files:
            if 'route' in file_path.lower() or 'controller' in file_path.lower():
                file_name = Path(file_path).stem
                
                # Check if route is imported/registered
                is_registered = False
                
                import_patterns = [
                    f"require.*{file_name}",
                    f"import.*{file_name}",
                    f"from.*{file_name}.*import",
                    f"app.use.*{file_name}",
                ]
                
                for pattern in import_patterns:
                    if re.search(pattern, app_content, re.IGNORECASE):
                        is_registered = True
                        break
                
                if not is_registered:
                    issues.append({
                        "type": "route_not_registered",
                        "severity": "critical",
                        "file": file_path,
                        "description": f"Route '{file_name}' is not registered in {app_file.name}",
                        "auto_fixable": True
                    })
                    
                    fix_plan.append({
                        "action": "register_route",
                        "target_file": str(app_file),
                        "route_file": file_path,
                        "route_name": file_name
                    })
        
        status = "issues_found" if issues else "ok"
        auto_fixable = all(issue.get("auto_fixable", False) for issue in issues)
        
        return {
            "status": status,
            "issues": issues,
            "auto_fixable": auto_fixable,
            "fix_plan": fix_plan
        }
    
    @staticmethod
    def auto_fix_integration(project_path: str, fix_plan: List[Dict]) -> Dict:
        """
        Automatically fix integration issues.
        
        Args:
            project_path: Project root
            fix_plan: List of fixes to apply
        
        Returns:
            {
                "status": "success" | "failed",
                "fixed": [...],
                "failed": [...]
            }
        """
        
        project_root = Path(project_path)
        fixed = []
        failed = []
        
        for fix in fix_plan:
            try:
                if fix["action"] == "add_import":
                    IntegrationVerifier._add_import(
                        project_root / fix["target_file"],
                        fix["component"],
                        fix["source"]
                    )
                    fixed.append(fix)
                
                elif fix["action"] == "add_usage":
                    IntegrationVerifier._add_component_usage(
                        project_root / fix["target_file"],
                        fix["component"]
                    )
                    fixed.append(fix)
                
                elif fix["action"] == "register_route":
                    IntegrationVerifier._register_route(
                        project_root / fix["target_file"],
                        fix["route_file"],
                        fix["route_name"]
                    )
                    fixed.append(fix)
                
            except Exception as e:
                failed.append({
                    "fix": fix,
                    "error": str(e)
                })
        
        status = "success" if not failed else "failed"
        
        return {
            "status": status,
            "fixed": fixed,
            "failed": failed
        }
    
    # Helper methods
    
    @staticmethod
    def _find_file(root: Path, candidates: List[str]) -> Path:
        """Find first matching file"""
        for candidate in candidates:
            matches = list(root.rglob(candidate))
            if matches:
                return matches[0]
        return None
    
    @staticmethod
    def _add_import(target_file: Path, component: str, source: str):
        """Add import statement to file"""
        if not target_file.exists():
            return
        
        content = target_file.read_text(encoding='utf-8')
        
        # Calculate relative import path
        relative_path = os.path.relpath(source, target_file.parent).replace("\\", "/")
        if not relative_path.startswith('.'):
            relative_path = './' + relative_path
        relative_path = relative_path.replace('.jsx', '').replace('.tsx', '').replace('.js', '')
        
        # Add import at top of file (after existing imports)
        import_line = f"import {component} from '{relative_path}';\n"
        
        # Find where to insert (after last import)
        lines = content.split('\n')
        insert_index = 0
        
        for i, line in enumerate(lines):
            if line.strip().startswith('import '):
                insert_index = i + 1
        
        lines.insert(insert_index, import_line.strip())
        
        target_file.write_text('\n'.join(lines), encoding='utf-8')
        print(f"[INTEGRATION-FIX] Added import for {component} in {target_file.name}")
    
    @staticmethod
    def _add_component_usage(target_file: Path, component: str):
        """Add component to JSX"""
        if not target_file.exists():
            return
        
        content = target_file.read_text(encoding='utf-8')
        
        # Find return statement or JSX block
        # Insert component in a safe place
        usage_line = f"      <{component} />\n"
        
        # Simple heuristic: add before closing </div> or last }
        if '</div>' in content:
            content = content.replace('</div>', f'{usage_line}    </div>', 1)
        
        target_file.write_text(content, encoding='utf-8')
        print(f"[INTEGRATION-FIX] Added usage of {component} in {target_file.name}")
    
    @staticmethod
    def _register_route(target_file: Path, route_file: str, route_name: str):
        """Register route in main app file"""
        if not target_file.exists():
            return
        
        content = target_file.read_text(encoding='utf-8')
        
        # Determine if Node.js or Python
        if target_file.suffix == '.py':
            # Python (Flask/FastAPI)
            import_line = f"from {route_file.replace('/', '.').replace('.py', '')} import {route_name}_bp\n"
            register_line = f"app.register_blueprint({route_name}_bp)\n"
        else:
            # Node.js (Express)
            relative_path = os.path.relpath(route_file, target_file.parent).replace("\\", "/")
            if not relative_path.startswith('.'):
                relative_path = './' + relative_path
            
            import_line = f"const {route_name}Router = require('{relative_path}');\n"
            register_line = f"app.use('/api/{route_name}', {route_name}Router);\n"
        
        # Add import
        lines = content.split('\n')
        insert_index = 0
        
        for i, line in enumerate(lines):
            if 'require(' in line or 'import ' in line:
                insert_index = i + 1
        
        lines.insert(insert_index, import_line.strip())
        
        # Add registration (find app.listen or if __name__)
        for i, line in enumerate(lines):
            if 'app.listen' in line or 'if __name__' in line:
                lines.insert(i, register_line.strip())
                break
        
        target_file.write_text('\n'.join(lines), encoding='utf-8')
        print(f"[INTEGRATION-FIX] Registered route {route_name} in {target_file.name}")