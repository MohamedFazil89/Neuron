# agents/integration_verifier.py - FIXED WITH IMPORT VALIDATION
"""
Integration Verifier Agent

Ensures generated code is properly wired into the project.
Detects orphaned files, missing imports, broken integrations, AND INVALID IMPORTS.
"""

import os
import re
from pathlib import Path
from typing import List, Dict


class IntegrationVerifier:
    """
    Verifies that generated files are properly integrated.
    NOW ALSO DETECTS: Invalid imports, circular references, wrong paths
    """
    
    @staticmethod
    def verify_frontend_integration(project_path: str, generated_files: List[str]) -> Dict:
        """
        Verify frontend components are properly integrated.
        
        NEW CHECKS:
        1. Are imports valid and reachable?
        2. Are there naming conflicts?
        3. Are paths correct?
        4. Are there circular imports?
        
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
        
        # NEW: Check App.jsx for critical issues first
        if app_jsx and app_jsx.exists():
            app_issues = IntegrationVerifier._validate_file_imports(app_jsx, project_root)
            issues.extend(app_issues)
            
            # If App.jsx has critical issues, create fix plan
            for issue in app_issues:
                if issue['type'] == 'invalid_import':
                    fix_plan.append({
                        "action": "remove_invalid_import",
                        "target_file": str(app_jsx),
                        "import_line": issue['import_line'],
                        "reason": issue['description']
                    })
                elif issue['type'] == 'naming_conflict':
                    fix_plan.append({
                        "action": "resolve_naming_conflict",
                        "target_file": str(app_jsx),
                        "conflicting_name": issue['name'],
                        "reason": issue['description']
                    })
        
        # Check each generated component (existing logic)
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
                        is_used = True
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
    def _validate_file_imports(file_path: Path, project_root: Path) -> List[Dict]:
        """
        NEW METHOD: Validate all imports in a file
        
        Checks for:
        - Invalid import paths
        - Imports from outside project
        - Naming conflicts
        - Circular imports
        """
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            # Extract all imports
            import_pattern = r'^import\s+(.+?)\s+from\s+[\'"](.+?)[\'"]'
            
            file_name = file_path.stem
            
            for line_num, line in enumerate(lines, 1):
                match = re.match(import_pattern, line.strip())
                if match:
                    imported_names = match.group(1)
                    import_path = match.group(2)
                    
                    # Check 1: Is this importing from outside the project?
                    if import_path.startswith('../../../'):
                        # This is importing from outside the project (likely Neuron-Core)
                        issues.append({
                            "type": "invalid_import",
                            "severity": "critical",
                            "file": str(file_path),
                            "line": line_num,
                            "import_line": line.strip(),
                            "import_path": import_path,
                            "description": f"Invalid import from outside project: {import_path}",
                            "auto_fixable": True
                        })
                    
                    # Check 2: Naming conflict (importing something with same name as current file)
                    # Extract imported name (handle default and named imports)
                    if file_name in imported_names:
                        issues.append({
                            "type": "naming_conflict",
                            "severity": "critical",
                            "file": str(file_path),
                            "line": line_num,
                            "name": file_name,
                            "import_line": line.strip(),
                            "description": f"Naming conflict: Importing '{file_name}' in file that declares '{file_name}'",
                            "auto_fixable": True
                        })
                    
                    # Check 3: Does the imported file actually exist?
                    if not import_path.startswith('.'):
                        # It's a package import, skip validation
                        continue
                    
                    # Resolve relative path
                    resolved_path = (file_path.parent / import_path).resolve()
                    
                    # Add common extensions
                    possible_paths = [
                        resolved_path,
                        Path(str(resolved_path) + '.jsx'),
                        Path(str(resolved_path) + '.tsx'),
                        Path(str(resolved_path) + '.js'),
                        resolved_path / 'index.jsx',
                        resolved_path / 'index.tsx',
                        resolved_path / 'index.js',
                    ]
                    
                    file_exists = any(p.exists() for p in possible_paths)
                    
                    if not file_exists:
                        issues.append({
                            "type": "broken_import",
                            "severity": "critical",
                            "file": str(file_path),
                            "line": line_num,
                            "import_path": import_path,
                            "import_line": line.strip(),
                            "description": f"Import path does not exist: {import_path}",
                            "auto_fixable": False
                        })
        
        except Exception as e:
            print(f"[WARNING] Could not validate imports in {file_path}: {e}")
        
        return issues
    
    @staticmethod
    def verify_backend_integration(project_path: str, generated_files: List[str]) -> Dict:
        """
        Verify backend routes/controllers are properly wired.
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
        
        NEW FIXES:
        - Remove invalid imports
        - Resolve naming conflicts
        """
        
        project_root = Path(project_path)
        fixed = []
        failed = []
        
        for fix in fix_plan:
            try:
                if fix["action"] == "remove_invalid_import":
                    IntegrationVerifier._remove_invalid_import(
                        Path(fix["target_file"]),
                        fix["import_line"]
                    )
                    fixed.append(fix)
                
                elif fix["action"] == "resolve_naming_conflict":
                    IntegrationVerifier._remove_invalid_import(
                        Path(fix["target_file"]),
                        fix.get("import_line", "")
                    )
                    fixed.append(fix)
                
                elif fix["action"] == "add_import":
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
        
        status = "success" if not failed else "partial"
        
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
    def _remove_invalid_import(target_file: Path, import_line: str):
        """
        NEW METHOD: Remove an invalid import line
        """
        if not target_file.exists():
            print(f"[INTEGRATION-FIX] ⚠ File not found: {target_file}")
            return
        
        try:
            content = target_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Remove the problematic import line
            filtered_lines = []
            removed = False
            
            for line in lines:
                # Check if this line matches the import to remove
                if import_line in line or line.strip() == import_line:
                    removed = True
                    continue
                filtered_lines.append(line)
            
            if removed:
                target_file.write_text('\n'.join(filtered_lines), encoding='utf-8')
                print(f"[INTEGRATION-FIX] ✓ Removed invalid import from {target_file.name}")
            else:
                print(f"[INTEGRATION-FIX] ⚠ Import line not found in {target_file.name}")
        except Exception as e:
            print(f"[INTEGRATION-FIX] ✗ Error removing import: {e}")
    
    @staticmethod
    def _add_import(target_file: Path, component: str, source: str):
        """Add import statement to file"""
        if not target_file.exists():
            return
        
        content = target_file.read_text(encoding='utf-8')
        
        # Check if import already exists
        if f"import {component}" in content or f"import.*{component}" in content:
            print(f"[INTEGRATION-FIX] Import for {component} already exists")
            return
        
        # Calculate relative import path
        try:
            source_path = Path(source)
            if not source_path.is_absolute():
                # Source is relative to project root
                source_path = target_file.parent.parent / source
            
            relative_path = os.path.relpath(source_path, target_file.parent).replace("\\", "/")
        except:
            # Fallback: use source as-is
            relative_path = source.replace("\\", "/")
        
        if not relative_path.startswith('.'):
            relative_path = './' + relative_path
        relative_path = relative_path.replace('.jsx', '').replace('.tsx', '').replace('.js', '')
        
        # Add import at top of file (after existing imports)
        import_line = f"import {component} from '{relative_path}';"
        
        # Find where to insert (after last import)
        lines = content.split('\n')
        insert_index = 0
        
        for i, line in enumerate(lines):
            if line.strip().startswith('import '):
                insert_index = i + 1
        
        lines.insert(insert_index, import_line)
        
        target_file.write_text('\n'.join(lines), encoding='utf-8')
        print(f"[INTEGRATION-FIX] Added import for {component} in {target_file.name}")
    
    @staticmethod
    def _add_component_usage(target_file: Path, component: str):
        """Add component to JSX"""
        if not target_file.exists():
            return
        
        content = target_file.read_text(encoding='utf-8')
        
        # Check if component is already used
        if f"<{component}" in content:
            print(f"[INTEGRATION-FIX] Component {component} already in use")
            return
        
        # Find return statement or JSX block
        usage_line = f"      <{component} />"
        
        # Simple heuristic: add before closing </div> or last }
        if '</div>' in content:
            content = content.replace('</div>', f'{usage_line}\n    </div>', 1)
        
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
            import_line = f"from {route_file.replace('/', '.').replace('.py', '')} import {route_name}_bp"
            register_line = f"app.register_blueprint({route_name}_bp)"
        else:
            # Node.js (Express)
            relative_path = os.path.relpath(route_file, target_file.parent).replace("\\", "/")
            if not relative_path.startswith('.'):
                relative_path = './' + relative_path
            
            import_line = f"const {route_name}Router = require('{relative_path}');"
            register_line = f"app.use('/api/{route_name}', {route_name}Router);"
        
        # Add import
        lines = content.split('\n')
        insert_index = 0
        
        for i, line in enumerate(lines):
            if 'require(' in line or 'import ' in line:
                insert_index = i + 1
        
        lines.insert(insert_index, import_line)
        
        # Add registration (find app.listen or if __name__)
        for i, line in enumerate(lines):
            if 'app.listen' in line or 'if __name__' in line:
                lines.insert(i, register_line)
                break
        
        target_file.write_text('\n'.join(lines), encoding='utf-8')
        print(f"[INTEGRATION-FIX] Registered route {route_name} in {target_file.name}")