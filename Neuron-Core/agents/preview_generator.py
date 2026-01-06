"""
Neuron-Core/agents/preview_generator.py

Diff Preview System - Shows changes before applying them
Inspired by GitHub Copilot's suggestion preview
"""

import difflib
from pathlib import Path
from typing import Dict, List
from enum import Enum


class RiskLevel(Enum):
    """Risk levels for changes"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PreviewGenerator:
    """
    Generates unified diffs and preview HTML for code changes.
    Allows users to review before applying.
    """
    
    @staticmethod
    def generate_diff(original_content: str, new_content: str, file_path: str = "file") -> Dict:
        """
        Generate unified diff format between two versions.
        
        Args:
            original_content: Original file content (or empty string for new files)
            new_content: Proposed new content
            file_path: Path to file (for display)
            
        Returns:
            {
                "diff": "unified diff string",
                "stats": {
                    "additions": int,
                    "deletions": int,
                    "modifications": int,
                    "total_lines_changed": int
                },
                "risk_level": "low|medium|high|critical",
                "risk_factors": [reasons for risk level]
            }
        """
        
        # Handle empty files
        if not original_content:
            # New file creation
            new_lines = new_content.splitlines(keepends=True)
            diff_lines = [
                f"--- /dev/null\n",
                f"+++ {file_path}\n",
                f"@@ -0,0 +1,{len(new_lines)} @@\n"
            ]
            diff_lines.extend([f"+{line}" if not line.startswith('+') else line for line in new_lines])
            
            return {
                "diff": ''.join(diff_lines),
                "stats": {
                    "additions": len(new_lines),
                    "deletions": 0,
                    "modifications": 0,
                    "total_lines_changed": len(new_lines)
                },
                "risk_level": "low",
                "risk_factors": ["New file creation"]
            }
        
        # Generate unified diff
        original_lines = original_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=''
        )
        
        diff_text = '\n'.join(diff)
        
        # Calculate statistics
        additions = diff_text.count('\n+') - 1  # -1 for the +++ line
        deletions = diff_text.count('\n-') - 1  # -1 for the --- line
        
        # Modifications are lines that appear as both added and deleted
        modifications = min(additions, deletions)
        
        stats = {
            "additions": additions,
            "deletions": deletions,
            "modifications": modifications,
            "total_lines_changed": additions + deletions
        }
        
        # Assess risk level
        risk_level, risk_factors = PreviewGenerator._assess_risk(
            original_content, new_content, stats, file_path
        )
        
        return {
            "diff": diff_text,
            "stats": stats,
            "risk_level": risk_level,
            "risk_factors": risk_factors
        }
    
    @staticmethod
    def _assess_risk(original: str, new: str, stats: Dict, file_path: str) -> tuple:
        """
        Assess the risk level of proposed changes.
        
        Returns:
            (risk_level, [risk_factors])
        """
        
        risk_factors = []
        risk_score = 0
        
        # Factor 1: Large number of changes
        total_changes = stats["total_lines_changed"]
        if total_changes > 500:
            risk_factors.append(f"Very large change ({total_changes} lines)")
            risk_score += 3
        elif total_changes > 200:
            risk_factors.append(f"Large change ({total_changes} lines)")
            risk_score += 2
        elif total_changes > 50:
            risk_factors.append(f"Moderate change ({total_changes} lines)")
            risk_score += 1
        
        # Factor 2: High deletion ratio
        if stats["deletions"] > 0:
            deletion_ratio = stats["deletions"] / (stats["additions"] + stats["deletions"])
            if deletion_ratio > 0.5:
                risk_factors.append(f"High deletion ratio ({deletion_ratio:.0%})")
                risk_score += 2
        
        # Factor 3: Critical files
        critical_files = ['config', 'env', 'auth', 'security', 'database', 'migration']
        if any(keyword in file_path.lower() for keyword in critical_files):
            risk_factors.append("Modifying critical file")
            risk_score += 2
        
        # Factor 4: API changes
        if 'route' in file_path.lower() or 'api' in file_path.lower():
            # Check if HTTP methods or endpoints are being changed
            if any(method in new for method in ['POST', 'GET', 'PUT', 'DELETE', 'PATCH']):
                if original and new != original:
                    risk_factors.append("API endpoint modification")
                    risk_score += 1
        
        # Factor 5: Database changes
        db_keywords = ['DROP', 'ALTER TABLE', 'DELETE FROM', 'TRUNCATE', 'migrate']
        if any(keyword in new for keyword in db_keywords):
            risk_factors.append("Database schema change")
            risk_score += 3
        
        # Factor 6: Complete file replacement
        if original and len(original) > 100:
            similarity = difflib.SequenceMatcher(None, original, new).ratio()
            if similarity < 0.3:
                risk_factors.append(f"Complete file rewrite (only {similarity:.0%} similar)")
                risk_score += 2
        
        # Determine risk level
        if risk_score >= 6:
            return RiskLevel.CRITICAL.value, risk_factors
        elif risk_score >= 4:
            return RiskLevel.HIGH.value, risk_factors
        elif risk_score >= 2:
            return RiskLevel.MEDIUM.value, risk_factors
        else:
            return RiskLevel.LOW.value, risk_factors if risk_factors else ["Minor changes"]
    
    @staticmethod
    def generate_preview_summary(file_changes: List[Dict]) -> Dict:
        """
        Generate a summary of all file changes.
        
        Args:
            file_changes: List of dicts with {path, action, diff_result}
            
        Returns:
            {
                "total_files": int,
                "new_files": int,
                "modified_files": int,
                "total_additions": int,
                "total_deletions": int,
                "overall_risk": "low|medium|high|critical",
                "high_risk_files": [...]
            }
        """
        
        total_files = len(file_changes)
        new_files = sum(1 for f in file_changes if f['action'] == 'create')
        modified_files = total_files - new_files
        
        total_additions = sum(f['diff_result']['stats']['additions'] for f in file_changes)
        total_deletions = sum(f['diff_result']['stats']['deletions'] for f in file_changes)
        
        # Find high-risk files
        high_risk_files = [
            f['path'] for f in file_changes 
            if f['diff_result']['risk_level'] in ['high', 'critical']
        ]
        
        # Determine overall risk
        risk_scores = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        
        max_risk = max([risk_scores[f['diff_result']['risk_level']] for f in file_changes])
        
        overall_risk_map = {1: 'low', 2: 'medium', 3: 'high', 4: 'critical'}
        overall_risk = overall_risk_map[max_risk]
        
        return {
            "total_files": total_files,
            "new_files": new_files,
            "modified_files": modified_files,
            "total_additions": total_additions,
            "total_deletions": total_deletions,
            "overall_risk": overall_risk,
            "high_risk_files": high_risk_files
        }
    
    @staticmethod
    def generate_cli_preview(file_changes: List[Dict]) -> str:
        """
        Generate a CLI-friendly preview of changes.
        
        Args:
            file_changes: List of file change dicts
            
        Returns:
            Formatted string for CLI display
        """
        
        summary = PreviewGenerator.generate_preview_summary(file_changes)
        
        output = []
        output.append("\n" + "=" * 70)
        output.append("PREVIEW OF PROPOSED CHANGES")
        output.append("=" * 70)
        
        # Summary
        output.append(f"\n[SUMMARY] Summary:")
        output.append(f"  Total files: {summary['total_files']}")
        output.append(f"  New files: {summary['new_files']}")
        output.append(f"  Modified files: {summary['modified_files']}")
        output.append(f"  Lines added: +{summary['total_additions']}")
        output.append(f"  Lines deleted: -{summary['total_deletions']}")
        
        # Risk assessment
        risk_colors = {
            'low': '[LOW]',
            'medium': '[MED]',
            'high': '[HIGH]',
            'critical': '[CRIT]'
        }
        
        risk_icon = risk_colors.get(summary['overall_risk'], '[?]')
        output.append(f"\n{risk_icon} Overall Risk: {summary['overall_risk'].upper()}")
        
        if summary['high_risk_files']:
            output.append(f"\n[WARN] High-risk files:")
            for file_path in summary['high_risk_files']:
                output.append(f"    - {file_path}")
        
        # Detailed file changes
        output.append("\n" + "-" * 70)
        output.append("DETAILED CHANGES:")
        output.append("-" * 70)
        
        for change in file_changes:
            action = change['action']
            path = change['path']
            diff_result = change['diff_result']
            
            action_icon = "[NEW]" if action == "create" else "[MOD]"
            risk_icon = risk_colors.get(diff_result['risk_level'], '[?]')
            
            output.append(f"\n{action_icon} {action.upper()}: {path}")
            output.append(f"   {risk_icon} Risk: {diff_result['risk_level']}")
            
            stats = diff_result['stats']
            output.append(f"   +{stats['additions']} -{stats['deletions']} lines changed")
            
            if diff_result['risk_factors']:
                output.append(f"   Risks: {', '.join(diff_result['risk_factors'])}")
            
            # Show first few lines of diff
            diff_lines = diff_result['diff'].split('\n')[:10]
            if diff_lines:
                output.append("\n   Preview:")
                for line in diff_lines:
                    if line.startswith('+'):
                        output.append(f"   {line}")
                    elif line.startswith('-'):
                        output.append(f"   {line}")
                    elif line.startswith('@@'):
                        output.append(f"   {line}")
                
                if len(diff_result['diff'].split('\n')) > 10:
                    output.append("   ... (see full diff with --show-full)")
        
        output.append("\n" + "=" * 70)
        output.append("Review the changes above before applying.")
        output.append("=" * 70 + "\n")
        
        return '\n'.join(output)


# Example usage
if __name__ == "__main__":
    
    # Test 1: New file creation
    new_content = """def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
"""
    
    diff_result = PreviewGenerator.generate_diff("", new_content, "hello.py")
    print("Test 1 - New file:")
    print(f"  Additions: {diff_result['stats']['additions']}")
    print(f"  Risk: {diff_result['risk_level']}")
    print(f"  Factors: {diff_result['risk_factors']}")
    
    # Test 2: File modification
    original = """def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
"""
    
    modified = """def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")

def farewell(name):
    print(f"Goodbye, {name}!")

greet("Alice")
farewell("Bob")
"""
    
    diff_result = PreviewGenerator.generate_diff(original, modified, "greet.py")
    print("\nTest 2 - File modification:")
    print(f"  Additions: {diff_result['stats']['additions']}")
    print(f"  Deletions: {diff_result['stats']['deletions']}")
    print(f"  Risk: {diff_result['risk_level']}")
    
    # Test 3: CLI preview
    file_changes = [
        {
            "path": "hello.py",
            "action": "create",
            "diff_result": PreviewGenerator.generate_diff("", new_content, "hello.py")
        },
        {
            "path": "greet.py",
            "action": "modify",
            "diff_result": PreviewGenerator.generate_diff(original, modified, "greet.py")
        }
    ]
    
    cli_preview = PreviewGenerator.generate_cli_preview(file_changes)
    print("\nTest 3 - CLI Preview:")
    print(cli_preview)