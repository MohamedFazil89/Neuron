"""
Neuron-Core/core/version_control.py

Rollback System - Create snapshots and revert changes
Works with or without Git
"""

import os
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class VersionControl:
    """
    Manages snapshots and rollbacks for Neuron-generated code.
    
    Strategy:
    1. If Git exists: Create lightweight Git branches
    2. If no Git: Create ZIP backups
    """
    
    SNAPSHOT_DIR = ".neuron/snapshots"
    SNAPSHOT_METADATA = ".neuron/snapshot_metadata.json"
    
    @staticmethod
    def _ensure_snapshot_dir(project_path: str) -> Path:
        """Ensure snapshot directory exists"""
        snapshot_dir = Path(project_path) / VersionControl.SNAPSHOT_DIR
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        return snapshot_dir
    
    @staticmethod
    def _get_metadata_path(project_path: str) -> Path:
        """Get path to snapshot metadata file"""
        neuron_dir = Path(project_path) / ".neuron"
        neuron_dir.mkdir(exist_ok=True)
        return neuron_dir / "snapshot_metadata.json"
    
    @staticmethod
    def _load_metadata(project_path: str) -> Dict:
        """Load snapshot metadata"""
        metadata_path = VersionControl._get_metadata_path(project_path)
        
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {"snapshots": []}
    
    @staticmethod
    def _save_metadata(project_path: str, metadata: Dict):
        """Save snapshot metadata"""
        metadata_path = VersionControl._get_metadata_path(project_path)
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    @staticmethod
    def has_git(project_path: str) -> bool:
        """Check if project has Git initialized"""
        git_dir = Path(project_path) / ".git"
        return git_dir.exists()
    
    @staticmethod
    def create_snapshot(project_path: str, feature_name: str, files_changed: List[str] = None) -> Dict:
        """
        Create a snapshot before applying changes.
        
        Args:
            project_path: Path to project
            feature_name: Name of feature being added
            files_changed: List of files that will be changed
            
        Returns:
            {
                "snapshot_id": str,
                "timestamp": str,
                "feature": str,
                "method": "git" | "zip",
                "files_changed": [...]
            }
        """
        
        print(f"[VERSION_CONTROL] Creating snapshot for: {feature_name}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_id = f"neuron_{timestamp}"
        
        if VersionControl.has_git(project_path):
            # Use Git
            success = VersionControl._create_git_snapshot(project_path, snapshot_id, feature_name)
            method = "git"
        else:
            # Use ZIP backup
            success = VersionControl._create_zip_snapshot(
                project_path, snapshot_id, feature_name, files_changed
            )
            method = "zip"
        
        if not success:
            raise Exception("Failed to create snapshot")
        
        # Save metadata
        metadata = VersionControl._load_metadata(project_path)
        
        snapshot_info = {
            "snapshot_id": snapshot_id,
            "timestamp": datetime.now().isoformat(),
            "feature": feature_name,
            "method": method,
            "files_changed": files_changed or []
        }
        
        metadata["snapshots"].append(snapshot_info)
        
        # Keep only last 10 snapshots
        if len(metadata["snapshots"]) > 10:
            oldest = metadata["snapshots"][0]
            VersionControl._delete_snapshot(project_path, oldest)
            metadata["snapshots"] = metadata["snapshots"][1:]
        
        VersionControl._save_metadata(project_path, metadata)
        
        print(f"[VERSION_CONTROL] Snapshot created: {snapshot_id}")
        
        return snapshot_info
    
    @staticmethod
    def _create_git_snapshot(project_path: str, snapshot_id: str, feature_name: str) -> bool:
        """Create a Git branch snapshot"""
        try:
            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            has_changes = bool(result.stdout.strip())
            
            if has_changes:
                # Stash changes temporarily
                subprocess.run(["git", "stash", "push", "-u"], cwd=project_path, check=True)
            
            # Create snapshot branch from current state
            branch_name = f"neuron/backup/{snapshot_id}"
            subprocess.run(
                ["git", "branch", branch_name],
                cwd=project_path,
                check=True
            )
            
            if has_changes:
                # Restore stashed changes
                subprocess.run(["git", "stash", "pop"], cwd=project_path, check=True)
            
            print(f"[VERSION_CONTROL] Created Git branch: {branch_name}")
            
            return True
        
        except subprocess.CalledProcessError as e:
            print(f"[VERSION_CONTROL] Git error: {e}")
            return False
    
    @staticmethod
    def _create_zip_snapshot(
        project_path: str, 
        snapshot_id: str, 
        feature_name: str,
        files_changed: List[str] = None
    ) -> bool:
        """Create a ZIP backup of changed files"""
        try:
            snapshot_dir = VersionControl._ensure_snapshot_dir(project_path)
            snapshot_path = snapshot_dir / f"{snapshot_id}.zip"
            
            # Create a temporary directory for backup
            import zipfile
            
            with zipfile.ZipFile(snapshot_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                
                if files_changed:
                    # Backup only changed files
                    for file_path in files_changed:
                        full_path = Path(project_path) / file_path
                        if full_path.exists():
                            zipf.write(full_path, arcname=file_path)
                else:
                    # Backup entire project (excluding node_modules, etc.)
                    exclude_dirs = {
                        'node_modules', '.git', '__pycache__', 'venv', 
                        '.venv', 'build', 'dist', '.neuron/snapshots'
                    }
                    
                    for root, dirs, files in os.walk(project_path):
                        # Filter out excluded directories
                        dirs[:] = [d for d in dirs if d not in exclude_dirs]
                        
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(project_path)
                            zipf.write(file_path, arcname=arcname)
            
            print(f"[VERSION_CONTROL] Created ZIP backup: {snapshot_path.name}")
            
            return True
        
        except Exception as e:
            print(f"[VERSION_CONTROL] ZIP error: {e}")
            return False
    
    @staticmethod
    def list_snapshots(project_path: str) -> List[Dict]:
        """
        List all available snapshots.
        
        Returns:
            List of snapshot info dicts
        """
        metadata = VersionControl._load_metadata(project_path)
        
        # Sort by timestamp (newest first)
        snapshots = sorted(
            metadata["snapshots"],
            key=lambda x: x["timestamp"],
            reverse=True
        )
        
        return snapshots
    
    @staticmethod
    def rollback(project_path: str, snapshot_id: str) -> Dict:
        """
        Rollback to a specific snapshot.
        
        Args:
            project_path: Path to project
            snapshot_id: ID of snapshot to restore
            
        Returns:
            {
                "status": "success" | "error",
                "message": str,
                "files_restored": [...]
            }
        """
        
        print(f"[VERSION_CONTROL] Rolling back to: {snapshot_id}")
        
        metadata = VersionControl._load_metadata(project_path)
        
        # Find snapshot
        snapshot = None
        for snap in metadata["snapshots"]:
            if snap["snapshot_id"] == snapshot_id:
                snapshot = snap
                break
        
        if not snapshot:
            return {
                "status": "error",
                "message": f"Snapshot '{snapshot_id}' not found"
            }
        
        # Rollback based on method
        if snapshot["method"] == "git":
            result = VersionControl._rollback_git(project_path, snapshot_id)
        else:
            result = VersionControl._rollback_zip(project_path, snapshot_id, snapshot["files_changed"])
        
        if result["status"] == "success":
            print(f"[VERSION_CONTROL] Rollback successful")
        else:
            print(f"[VERSION_CONTROL] Rollback failed: {result['message']}")
        
        return result
    
    @staticmethod
    def _rollback_git(project_path: str, snapshot_id: str) -> Dict:
        """Rollback using Git"""
        try:
            branch_name = f"neuron/backup/{snapshot_id}"
            
            # Check if branch exists
            result = subprocess.run(
                ["git", "branch", "--list", branch_name],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if not result.stdout.strip():
                return {
                    "status": "error",
                    "message": f"Branch '{branch_name}' not found"
                }
            
            # Stash current changes
            subprocess.run(["git", "stash", "push", "-u"], cwd=project_path)
            
            # Reset to snapshot branch
            subprocess.run(
                ["git", "reset", "--hard", branch_name],
                cwd=project_path,
                check=True
            )
            
            return {
                "status": "success",
                "message": f"Rolled back to {snapshot_id}",
                "files_restored": []
            }
        
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "message": f"Git rollback failed: {str(e)}"
            }
    
    @staticmethod
    def _rollback_zip(project_path: str, snapshot_id: str, files_changed: List[str]) -> Dict:
        """Rollback using ZIP backup"""
        try:
            import zipfile
            
            snapshot_dir = VersionControl._ensure_snapshot_dir(project_path)
            snapshot_path = snapshot_dir / f"{snapshot_id}.zip"
            
            if not snapshot_path.exists():
                return {
                    "status": "error",
                    "message": f"Backup file not found: {snapshot_path}"
                }
            
            # Extract ZIP
            files_restored = []
            
            with zipfile.ZipFile(snapshot_path, 'r') as zipf:
                for file_info in zipf.infolist():
                    zipf.extract(file_info, project_path)
                    files_restored.append(file_info.filename)
            
            return {
                "status": "success",
                "message": f"Rolled back to {snapshot_id}",
                "files_restored": files_restored
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"ZIP rollback failed: {str(e)}"
            }
    
    @staticmethod
    def _delete_snapshot(project_path: str, snapshot: Dict):
        """Delete a snapshot to save space"""
        snapshot_id = snapshot["snapshot_id"]
        
        if snapshot["method"] == "git":
            # Delete Git branch
            try:
                branch_name = f"neuron/backup/{snapshot_id}"
                subprocess.run(
                    ["git", "branch", "-D", branch_name],
                    cwd=project_path,
                    stderr=subprocess.DEVNULL
                )
            except:
                pass
        else:
            # Delete ZIP file
            snapshot_dir = VersionControl._ensure_snapshot_dir(project_path)
            snapshot_path = snapshot_dir / f"{snapshot_id}.zip"
            
            if snapshot_path.exists():
                snapshot_path.unlink()


# Example usage and tests
if __name__ == "__main__":
    
    # Test with a sample project
    test_project = "/tmp/test_project"
    os.makedirs(test_project, exist_ok=True)
    
    # Create a test file
    test_file = Path(test_project) / "test.txt"
    test_file.write_text("Original content")
    
    # Test 1: Create snapshot
    snapshot = VersionControl.create_snapshot(
        test_project,
        "Add test feature",
        ["test.txt"]
    )
    print(f"Created snapshot: {snapshot['snapshot_id']}")
    
    # Modify file
    test_file.write_text("Modified content")
    
    # Test 2: List snapshots
    snapshots = VersionControl.list_snapshots(test_project)
    print(f"Available snapshots: {len(snapshots)}")
    
    # Test 3: Rollback
    result = VersionControl.rollback(test_project, snapshot['snapshot_id'])
    print(f"Rollback result: {result['status']}")
    
    # Verify
    content = test_file.read_text()
    print(f"File content after rollback: {content}")
    assert content == "Original content", "Rollback failed!"
    
    print("\n✓ All tests passed!")