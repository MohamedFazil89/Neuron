# agents/integration_verifier.py - PROPERLY FIXED VERSION
"""
Integration Verifier Agent - ACTUALLY FIXES ISSUES

Key fixes:
1. Never import a file into itself
2. Proper relative path calculation
3. Smart detection of what should actually be imported into App.jsx
4. Removal of invalid imports works correctly
"""

import os
import re
from pathlib import Path
from typing import List, Dict


class IntegrationVerifier:
    """Verifies that generated files are properly integrated."""
    
    @staticmethod
    def verify_frontend_integration(project_path: str, generated_files: List[str]) -> Dict:
        """
        Verify frontend components are properly integrated.
        
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
        
        # FIRST: Check App.jsx for critical issues (self-imports, invalid paths)
        if app_jsx and app_jsx.exists():
            app_issues = IntegrationVerifier._validate_file_imports(app_jsx, project_root)
            
            for issue in app_issues:
                issues.append(issue)
                
                if issue['type'] in ['invalid_import', 'naming_conflict']:
                    fix_plan.append({
                        "action": "remove_invalid_import",
                        "target_file": str(app_jsx),
                        "import_line": issue.get('import_line', ''),
                        "import_path": issue.get('import_path', ''),
                        "reason": issue['description']
                    })
        
        # SECOND: Check each generated component
        for file_path in generated_files:
            if not any(ext in file_path for ext in ['.jsx', '.tsx', '.js']):
                continue
            
            full_path = project_root / file_path
            component_name = Path(file_path).stem
            
            # CRITICAL CHECK: Don't try to import App.jsx into itself
            if app_jsx and full_path.resolve() == app_jsx.resolve():
                print(f"[INTEGRATION] Skipping {file_path} - it's the main App file")
                continue
            
            # CRITICAL CHECK: Don't try to import main.jsx into App
            if 'main.jsx' in file_path or 'index.jsx' in file_path:
                print(f"[INTEGRATION] Skipping {file_path} - it's an entry file")
                continue
            
            # Check if component is imported in App.jsx
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
            
            # Report issues ONLY for actual components that should be imported
            if not is_imported and IntegrationVerifier._should_import_into_app(file_path):
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
    def _should_import_into_app(file_path: str) -> bool:
        """
        Determine if a file should be imported into App.jsx
        
        Rules:
        - YES: Pages (App.jsx should render pages)
        - NO: Components (pages should use components, not App.jsx)
        - NO: App.jsx itself, main.jsx, index.jsx, utility files
        """
        file_path_lower = file_path.lower()
        
        # Don't import these
        if any(x in file_path_lower for x in ['app.jsx', 'app.tsx', 'main.jsx', 'index.jsx', 'main.tsx', 'index.tsx']):
            return False
        
        # Don't import utils, helpers, hooks, services directly into App
        if any(x in file_path_lower for x in ['util', 'helper', 'hook', 'service', 'api', 'config']):
            return False
        
        # IMPORTANT: Don't import individual components into App.jsx
        # Components should be imported by PAGES, not directly by App
        if 'component' in file_path_lower and 'page' not in file_path_lower:
            return False
        
        # DO import pages into App.jsx
        if 'page' in file_path_lower:
            return True
        
        # Default: No - be conservative
        return False
    
    @staticmethod
    def _validate_file_imports(file_path: Path, project_root: Path) -> List[Dict]:
        """
        Validate all imports in a file.
        
        Detects:
        - Self-imports (App importing App)
        - Invalid paths
        - Imports from outside project
        """
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            file_name = file_path.stem
            
            # Extract all imports
            import_pattern = r'^import\s+(.+?)\s+from\s+[\'"](.+?)[\'"]'
            
            for line_num, line in enumerate(lines, 1):
                match = re.match(import_pattern, line.strip())
                if match:
                    imported_names = match.group(1)
                    import_path = match.group(2)
                    
                    # Check 1: Self-import (App importing App)
                    if file_name in imported_names and file_name != 'React':
                        issues.append({
                            "type": "naming_conflict",
                            "severity": "critical",
                            "file": str(file_path),
                            "line": line_num,
                            "name": file_name,
                            "import_line": line.strip(),
                            "import_path": import_path,
                            "description": f"Self-import: '{file_name}' cannot import itself",
                            "auto_fixable": True
                        })
                        continue
                    
                    # Check 2: Importing from way outside the project
                    if import_path.startswith('../../../'):
                        issues.append({
                            "type": "invalid_import",
                            "severity": "critical",
                            "file": str(file_path),
                            "line": line_num,
                            "import_line": line.strip(),
                            "import_path": import_path,
                            "description": f"Invalid import path (outside project): {import_path}",
                            "auto_fixable": True
                        })
                        continue
                    
                    # Check 3: Importing entry files into regular files
                    if any(x in import_path for x in ['main.jsx', 'index.jsx', 'main.tsx', 'index.tsx']) and 'node_modules' not in import_path:
                        issues.append({
                            "type": "invalid_import",
                            "severity": "critical",
                            "file": str(file_path),
                            "line": line_num,
                            "import_line": line.strip(),
                            "import_path": import_path,
                            "description": f"Should not import entry file: {import_path}",
                            "auto_fixable": True
                        })
        
        except Exception as e:
            print(f"[WARNING] Could not validate imports in {file_path}: {e}")
        
        return issues
    
    @staticmethod
    def verify_backend_integration(project_path: str, generated_files: List[str]) -> Dict:
        """Verify backend routes/controllers are properly wired."""
        
        project_root = Path(project_path)
        issues = []
        fix_plan = []
        
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
        
        for file_path in generated_files:
            if 'route' in file_path.lower() or 'controller' in file_path.lower():
                file_name = Path(file_path).stem
                
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
        
        IMPROVED VERSION - Actually works now.
        """
        
        print(f"\n[INTEGRATION-FIX] === STARTING AUTO-FIX ===")
        print(f"[INTEGRATION-FIX] Project: {project_path}")
        print(f"[INTEGRATION-FIX] Fix plan items: {len(fix_plan)}")
        
        project_root = Path(project_path)
        fixed = []
        failed = []
        
        for i, fix in enumerate(fix_plan, 1):
            print(f"\n[INTEGRATION-FIX] --- Fix {i}/{len(fix_plan)} ---")
            print(f"[INTEGRATION-FIX] Action: {fix.get('action')}")
            print(f"[INTEGRATION-FIX] Target: {fix.get('target_file')}")
            
            try:
                if fix["action"] == "remove_invalid_import":
                    target_path = Path(fix["target_file"])
                    print(f"[INTEGRATION-FIX] Removing invalid import from: {target_path}")
                    IntegrationVerifier._remove_invalid_import(
                        target_path,
                        fix.get("import_line", ""),
                        fix.get("import_path", "")
                    )
                    fixed.append(fix)
                
                elif fix["action"] == "add_import":
                    target_path = Path(fix["target_file"])
                    source_path = project_root / fix["source"]
                    
                    # CRITICAL CHECK: Never add self-imports
                    if target_path.resolve() == source_path.resolve():
                        print(f"[INTEGRATION-FIX] [WARN] Skipping self-import: {fix['component']}")
                        continue
                    
                    print(f"[INTEGRATION-FIX] Adding import to: {target_path}")
                    print(f"[INTEGRATION-FIX]   Component: {fix['component']}")
                    print(f"[INTEGRATION-FIX]   Source: {fix['source']}")
                    IntegrationVerifier._add_import(
                        target_path,
                        fix["component"],
                        fix["source"],
                        project_root
                    )
                    fixed.append(fix)
                
                elif fix["action"] == "add_usage":
                    target_path = Path(fix["target_file"])
                    print(f"[INTEGRATION-FIX] Adding component usage to: {target_path}")
                    IntegrationVerifier._add_component_usage(
                        target_path,
                        fix["component"]
                    )
                    fixed.append(fix)
                
                print(f"[INTEGRATION-FIX] [OK] Fix {i} completed")
                
            except Exception as e:
                print(f"[INTEGRATION-FIX] [FAIL] Fix {i} FAILED: {e}")
                import traceback
                traceback.print_exc()
                failed.append({
                    "fix": fix,
                    "error": str(e)
                })
        
        status = "success" if not failed else "partial"
        
        print(f"\n[INTEGRATION-FIX] === AUTO-FIX COMPLETE ===")
        print(f"[INTEGRATION-FIX] Fixed: {len(fixed)}")
        print(f"[INTEGRATION-FIX] Failed: {len(failed)}")
        
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
                # Prefer files in src/ over others
                src_matches = [m for m in matches if 'src' in str(m)]
                if src_matches:
                    return src_matches[0]
                return matches[0]
        return None
    
    @staticmethod
    def _remove_invalid_import(target_file: Path, import_line: str, import_path: str = None):
        """
        Remove an invalid import line.
        
        IMPROVED: More accurate matching.
        """
        if not target_file.exists():
            print(f"[INTEGRATION-FIX] ⚠ File not found: {target_file}")
            return
        
        try:
            content = target_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            filtered_lines = []
            removed_count = 0
            
            for line in lines:
                should_remove = False
                
                # Method 1: Exact match
                if line.strip() == import_line.strip():
                    should_remove = True
                
                # Method 2: Match by import path
                elif import_path and f'from "{import_path}"' in line or f"from '{import_path}'" in line:
                    should_remove = True
                
                # Method 3: Check for self-imports (App importing App)
                elif line.strip().startswith('import') and target_file.stem in line and 'from' in line:
                    # Extract what's being imported
                    import_match = re.match(r'import\s+(.+?)\s+from', line)
                    if import_match:
                        imported = import_match.group(1).strip()
                        # Remove default, named, or namespace imports of same name
                        if target_file.stem in imported:
                            should_remove = True
                
                if should_remove:
                    removed_count += 1
                    print(f"[INTEGRATION-FIX] [REMOVE] Removing: {line.strip()}")
                else:
                    filtered_lines.append(line)
            
            if removed_count > 0:
                target_file.write_text('\n'.join(filtered_lines), encoding='utf-8')
                print(f"[INTEGRATION-FIX] [OK] Removed {removed_count} invalid import(s) from {target_file.name}")
            else:
                print(f"[INTEGRATION-FIX] [WARN] No matching import found to remove")
                
        except Exception as e:
            print(f"[INTEGRATION-FIX] [ERR] Error removing import: {e}")
            import traceback
            traceback.print_exc()
    
    @staticmethod
    def _add_import(target_file: Path, component: str, source: str, project_root: Path):
        """
        Add import statement to file.
        
        PROPERLY FIXED: Correct path calculation and duplicate detection.
        """
        if not target_file.exists():
            print(f"[INTEGRATION-FIX] ⚠ File not found: {target_file}")
            return
        
        try:
            content = target_file.read_text(encoding='utf-8')
            
            # Check if import already exists
            if f"import {component}" in content or f"import {{ {component} }}" in content:
                print(f"[INTEGRATION-FIX] ℹ Import for {component} already exists")
                return
            
            # Calculate correct relative path
            source_path = project_root / source
            
            if not source_path.exists():
                print(f"[INTEGRATION-FIX] [WARN] Source file not found: {source_path}")
                return
            
            # Calculate relative path from target to source
            try:
                relative_path = os.path.relpath(source_path, target_file.parent).replace("\\", "/")
            except ValueError:
                print(f"[INTEGRATION-FIX] [WARN] Cannot calculate relative path")
                return
            
            # Ensure path starts with ./
            if not relative_path.startswith('.'):
                relative_path = './' + relative_path
            
            # Remove extension
            relative_path = re.sub(r'\.(jsx|tsx|js|ts)$', '', relative_path)
            
            # Create import line
            import_line = f"import {component} from '{relative_path}';"
            
            # Find where to insert (after last import)
            lines = content.split('\n')
            insert_index = 0
            
            for i, line in enumerate(lines):
                if line.strip().startswith('import '):
                    insert_index = i + 1
            
            # Insert the import
            lines.insert(insert_index, import_line)
            
            # Write back
            new_content = '\n'.join(lines)
            target_file.write_text(new_content, encoding='utf-8')
            print(f"[INTEGRATION-FIX] [OK] Added import for {component} in {target_file.name}")
            print(f"[INTEGRATION-FIX]   Import: {import_line}")
            
        except Exception as e:
            print(f"[INTEGRATION-FIX] [ERR] Error adding import: {e}")
            import traceback
            traceback.print_exc()
    
    @staticmethod
    def _add_component_usage(target_file: Path, component: str):
        """
        Add component to JSX properly.
        
        ROBUST VERSION: Handles edge cases including minimal App.jsx files.
        """
        if not target_file.exists():
            print(f"[INTEGRATION-FIX] ⚠ File not found: {target_file}")
            return
        
        try:
            content = target_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check if component is already used
            if f"<{component}" in content or f"<{component}>" in content:
                print(f"[INTEGRATION-FIX] ℹ Component {component} already in use")
                return
            
            # FIRST: Check if this is a mostly empty App.jsx (only imports)
            has_function = any('function' in line.lower() or 'const' in line and '=>' in line for line in lines)
            has_return = any('return' in line for line in lines)
            has_jsx = any('<' in line and '>' in line and 'import' not in line for line in lines)
            
            if not (has_function and has_return and has_jsx):
                # App.jsx is incomplete - need to create a proper structure
                print(f"[INTEGRATION-FIX] [WARN] App.jsx appears incomplete - creating basic structure")
                
                # Find where imports end
                last_import_line = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('import '):
                        last_import_line = i
                
                # Create a basic App component structure
                new_app_content = []
                
                # Keep imports
                for i in range(last_import_line + 1):
                    new_app_content.append(lines[i])
                
                # Add blank line
                new_app_content.append('')
                
                # Add function component
                new_app_content.append('function App() {')
                new_app_content.append('  return (')
                new_app_content.append('    <div className="App">')
                new_app_content.append(f'      <{component} />')
                new_app_content.append('    </div>')
                new_app_content.append('  )')
                new_app_content.append('}')
                new_app_content.append('')
                new_app_content.append('export default App')
                
                new_content = '\n'.join(new_app_content)
                target_file.write_text(new_content, encoding='utf-8')
                print(f"[INTEGRATION-FIX] [OK] Created App component with {component}")
                return
            
            # SECOND: App.jsx has structure - find insertion point
            modified = False
            
            # Strategy 1: Find the main return statement
            in_return = False
            return_indent = 0
            insert_line = -1
            brace_depth = 0
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Detect return statement
                if 'return' in stripped and ('(' in stripped or '<' in stripped):
                    in_return = True
                    return_indent = len(line) - len(line.lstrip())
                    continue
                
                # If we're in a return block
                if in_return:
                    # Track JSX depth roughly
                    brace_depth += line.count('<') - line.count('</')
                    
                    # Look for a closing tag that's not the final one
                    if ('</' in stripped or '/>' in stripped) and brace_depth > 1:
                        # This is a good insertion point
                        insert_line = i
                        break
                    
                    # If we hit the closing of return, insert before it
                    if stripped == ')' or stripped == ');':
                        # Go back one line
                        insert_line = i - 1
                        break
            
            # If we found a good spot, insert the component
            if insert_line != -1 and insert_line > 0:
                # Get indentation from the line before
                prev_line = lines[insert_line]
                indent_match = re.match(r'^(\s*)', prev_line)
                indent = indent_match.group(1) if indent_match else '      '
                
                usage_line = f"{indent}<{component} />"
                lines.insert(insert_line, usage_line)
                modified = True
            
            # Strategy 2: If Strategy 1 failed, find last JSX closing tag
            if not modified:
                for i in range(len(lines) - 1, -1, -1):
                    line = lines[i]
                    if ('</div>' in line or '</>' in line or '/>' in line) and 'import' not in line:
                        # Get indentation
                        indent_match = re.match(r'^(\s*)', line)
                        indent = indent_match.group(1) if indent_match else '      '
                        
                        usage_line = f"{indent}<{component} />"
                        lines.insert(i, usage_line)
                        modified = True
                        break
            
            # Strategy 3: Last resort - add before closing brace
            if not modified:
                for i in range(len(lines) - 1, -1, -1):
                    line = lines[i]
                    if line.strip() == '}' and i > 0:
                        # Add with standard indentation
                        usage_line = f"    <{component} />"
                        lines.insert(i, usage_line)
                        modified = True
                        break
            
            if modified:
                new_content = '\n'.join(lines)
                target_file.write_text(new_content, encoding='utf-8')
                print(f"[INTEGRATION-FIX] [OK] Added usage of {component} in {target_file.name}")
            else:
                print(f"[INTEGRATION-FIX] [WARN] Could not find suitable insertion point for {component}")
                print(f"[INTEGRATION-FIX] ℹ File content preview:")
                print('\n'.join(lines[:20]))  # Show first 20 lines for debugging
                
        except Exception as e:
            print(f"[INTEGRATION-FIX] [ERR] Error adding component usage: {e}")
            import traceback
            traceback.print_exc()