"""Git integration for OpenAPI Generator."""

import os
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import base64
from cryptography.fernet import Fernet
import getpass


class GitIntegration:
    """Handle Git operations for OpenAPI Generator."""
    
    def __init__(self, repo_path: Optional[str] = None):
        """Initialize Git integration.
        
        Args:
            repo_path: Path to Git repository (default: current directory)
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.config_file = Path.home() / ".openapi-generator" / "git_config.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
    
    def is_git_repo(self) -> bool:
        """Check if current directory is a Git repository.
        
        Returns:
            True if Git repository, False otherwise
        """
        git_dir = self.repo_path / ".git"
        return git_dir.exists() and git_dir.is_dir()
    
    def clone_repo(self, remote_url: str, branch: Optional[str] = None) -> Tuple[bool, str]:
        """Clone a remote Git repository.
        
        Args:
            remote_url: URL of the remote repository
            branch: Branch to clone (default: default branch)
            
        Returns:
            Tuple of (success, message)
        """
        if self.is_git_repo():
            return True, "Repository already exists"
        
        try:
            # If directory exists but is not a git repo, remove it first
            if self.repo_path.exists():
                if not self.is_git_repo():
                    # Remove existing directory
                    shutil.rmtree(self.repo_path)
                else:
                    return True, "Repository already exists"
            else:
                # Create parent directory if it doesn't exist
                self.repo_path.parent.mkdir(parents=True, exist_ok=True)
            
            cmd = ["git", "clone", remote_url, str(self.repo_path)]
            if branch:
                cmd.extend(["-b", branch])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True, f"Repository cloned successfully to {self.repo_path}"
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else e.stdout
            return False, f"Failed to clone repository: {error_msg}"
        except FileNotFoundError:
            return False, "Git is not installed. Please install Git to use this feature."
        except Exception as e:
            return False, f"Error cloning repository: {str(e)}"
    
    def initialize_repo(self) -> Tuple[bool, str]:
        """Initialize a new Git repository if it doesn't exist.
        
        Returns:
            Tuple of (success, message)
        """
        if self.is_git_repo():
            return True, "Repository already initialized"
        
        try:
            # Create directory if it doesn't exist
            self.repo_path.mkdir(parents=True, exist_ok=True)
            
            result = subprocess.run(
                ["git", "init"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return True, "Git repository initialized successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to initialize Git repository: {e.stderr}"
        except FileNotFoundError:
            return False, "Git is not installed. Please install Git to use this feature."
    
    def get_git_status(self) -> Dict[str, Any]:
        """Get Git repository status.
        
        Returns:
            Dictionary with status information
        """
        if not self.is_git_repo():
            return {
                "is_repo": False,
                "message": "Not a Git repository"
            }
        
        try:
            # Check if there are changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            has_changes = bool(result.stdout.strip())
            
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            current_branch = branch_result.stdout.strip() or "main"
            
            # Check if remote exists and get details
            remote_result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            has_remote = bool(remote_result.stdout.strip())
            
            remote_info = {}
            remote_connected = False
            remote_url = None
            
            if has_remote:
                # Get remote URL
                remote_name = "origin"
                url_result = subprocess.run(
                    ["git", "remote", "get-url", remote_name],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                if url_result.returncode == 0:
                    remote_url = url_result.stdout.strip()
                    remote_info["url"] = remote_url
                    remote_info["name"] = remote_name
                    
                    # Test remote connectivity (non-blocking check)
                    try:
                        # Use ls-remote to test connectivity (with timeout)
                        test_result = subprocess.run(
                            ["git", "ls-remote", "--heads", remote_name],
                            cwd=self.repo_path,
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        remote_connected = test_result.returncode == 0
                        if remote_connected:
                            remote_info["status"] = "connected"
                            remote_info["status_message"] = "Remote repository is reachable"
                        else:
                            remote_info["status"] = "disconnected"
                            remote_info["status_message"] = f"Unable to reach remote: {test_result.stderr.strip()}"
                    except subprocess.TimeoutExpired:
                        remote_info["status"] = "timeout"
                        remote_info["status_message"] = "Connection to remote timed out"
                    except Exception as e:
                        remote_info["status"] = "unknown"
                        remote_info["status_message"] = f"Could not test connection: {str(e)}"
                else:
                    remote_info["status"] = "no_url"
                    remote_info["status_message"] = "Remote exists but URL not configured"
            
            return {
                "is_repo": True,
                "has_changes": has_changes,
                "current_branch": current_branch,
                "has_remote": has_remote,
                "remote_connected": remote_connected,
                "remote_info": remote_info,
                "repo_path": str(self.repo_path),
                "message": "Repository status retrieved"
            }
        except subprocess.CalledProcessError as e:
            return {
                "is_repo": True,
                "error": str(e),
                "message": "Failed to get Git status"
            }
        except FileNotFoundError:
            return {
                "is_repo": False,
                "message": "Git is not installed"
            }
    
    def copy_file_to_repo(self, source_file: str, dest_path: Optional[str] = None) -> Tuple[bool, str, str]:
        """Copy a file to the Git repository.
        
        Args:
            source_file: Path to source file (can be absolute or relative)
            dest_path: Destination path relative to repo (default: filename only)
            
        Returns:
            Tuple of (success, message, relative_path_in_repo)
        """
        if not self.is_git_repo():
            return False, "Not a Git repository", ""
        
        try:
            source = Path(source_file)
            if not source.exists():
                return False, f"Source file does not exist: {source_file}", ""
            
            # Determine destination path
            if dest_path:
                dest = self.repo_path / dest_path
            else:
                dest = self.repo_path / source.name
            
            # Create parent directories if needed
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source, dest)
            
            # Get relative path for Git operations
            rel_path = dest.relative_to(self.repo_path)
            
            return True, f"File copied to {rel_path}", str(rel_path)
        except Exception as e:
            return False, f"Failed to copy file: {str(e)}", ""
    
    def add_file(self, file_path: str) -> Tuple[bool, str]:
        """Add file to Git staging area.
        
        Args:
            file_path: Path to file to add (relative to repo_path or absolute)
            
        Returns:
            Tuple of (success, message)
        """
        if not self.is_git_repo():
            return False, "Not a Git repository"
        
        try:
            # Handle both absolute and relative paths
            file_path_obj = Path(file_path)
            
            # If absolute path, check if it's inside the repo
            if file_path_obj.is_absolute():
                try:
                    # Try to get relative path from repo root
                    rel_path = file_path_obj.relative_to(self.repo_path)
                    # Verify file exists
                    if not file_path_obj.exists():
                        return False, f"File not found: {file_path}"
                except ValueError:
                    # File is outside repo - this shouldn't happen if copy_file_to_repo was called
                    return False, f"File is outside repository: {file_path}"
            else:
                # Relative path - construct full path
                rel_path = Path(file_path)
                full_path = self.repo_path / rel_path
                # Verify file exists
                if not full_path.exists():
                    return False, f"File not found in repository: {rel_path}"
            
            # Use forward slashes for Git (works on both Windows and Unix)
            git_path = str(rel_path).replace('\\', '/')
            
            result = subprocess.run(
                ["git", "add", git_path],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=True
            )
            return True, f"File '{rel_path}' added to staging area"
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else e.stdout
            return False, f"Failed to add file: {error_msg}"
        except FileNotFoundError:
            return False, "Git is not installed"
        except Exception as e:
            return False, f"Error adding file: {str(e)}"
    
    def commit(self, message: str, author_name: Optional[str] = None, author_email: Optional[str] = None) -> Tuple[bool, str]:
        """Commit staged changes.
        
        Args:
            message: Commit message
            author_name: Author name (optional, uses Git config if not provided)
            author_email: Author email (optional, uses Git config if not provided)
            
        Returns:
            Tuple of (success, message)
        """
        if not self.is_git_repo():
            return False, "Not a Git repository"
        
        # Check if there are staged changes
        try:
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            # Check if there are staged changes (lines starting with A, M, D, R, C)
            staged_changes = [line for line in status_result.stdout.split('\n') if line and line[0] in 'AMD R']
            if not staged_changes:
                return False, "No staged changes to commit. Please add files first."
        except subprocess.CalledProcessError:
            pass  # Continue even if status check fails
        
        try:
            cmd = ["git", "commit", "-m", message]
            
            # Set author if provided
            if author_name and author_email:
                cmd.extend(["--author", f"{author_name} <{author_email}>"])
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return True, "Changes committed successfully"
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else e.stdout
            if "nothing to commit" in error_msg.lower() or "no changes added to commit" in error_msg.lower():
                return False, "No changes to commit. Make sure files are staged."
            # Get more detailed error
            return False, f"Failed to commit: {error_msg}"
        except FileNotFoundError:
            return False, "Git is not installed"
    
    def push(self, remote: str = "origin", branch: Optional[str] = None, force: bool = False, set_upstream: bool = True) -> Tuple[bool, str]:
        """Push commits to remote repository.
        
        Args:
            remote: Remote name (default: origin)
            branch: Branch name (default: current branch)
            force: Force push (default: False)
            set_upstream: Set upstream tracking branch (default: True, useful for new branches)
            
        Returns:
            Tuple of (success, message)
        """
        if not self.is_git_repo():
            return False, "Not a Git repository"
        
        # Verify remote exists before attempting push
        try:
            remote_check = subprocess.run(
                ["git", "remote", "get-url", remote],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            remote_url = remote_check.stdout.strip()
            if not remote_url:
                return False, f"Remote '{remote}' is not configured. Please set the remote URL first."
        except subprocess.CalledProcessError:
            return False, f"Remote '{remote}' does not exist. Please add the remote first using 'git remote add {remote} <url>'."
        
        try:
            # Get current branch if not provided
            if not branch:
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                branch = branch_result.stdout.strip() or "main"
            
            # Check if branch exists on remote
            branch_exists_remote = False
            try:
                result = subprocess.run(
                    ["git", "ls-remote", "--heads", remote, branch],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                branch_exists_remote = bool(result.stdout.strip())
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                pass  # If we can't check, assume it doesn't exist and set upstream
            
            cmd = ["git", "push"]
            if force:
                cmd.append("--force")
            
            # If branch doesn't exist on remote or set_upstream is True, use -u flag
            if set_upstream or not branch_exists_remote:
                cmd.extend(["-u", remote, branch])
            else:
                cmd.extend([remote, branch])
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return True, f"Successfully pushed to {remote}/{branch}"
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else e.stdout
            # Check if authentication is needed
            if "authentication" in error_msg.lower() or "permission denied" in error_msg.lower():
                return False, "Authentication failed. Please check your Git credentials."
            # Check if it's a new branch issue
            if "no upstream branch" in error_msg.lower() or "has no upstream branch" in error_msg.lower():
                # Try again with -u flag
                try:
                    cmd = ["git", "push", "-u", remote, branch]
                    if force:
                        cmd.insert(2, "--force")
                    result = subprocess.run(
                        cmd,
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    return True, f"Successfully pushed to {remote}/{branch} (upstream set)"
                except subprocess.CalledProcessError as retry_error:
                    retry_error_msg = retry_error.stderr if retry_error.stderr else retry_error.stdout
                    return False, f"Failed to push: {retry_error_msg}"
            return False, f"Failed to push: {error_msg}"
        except FileNotFoundError:
            return False, "Git is not installed"
    
    def commit_and_push(
        self,
        file_path: str,
        commit_message: str,
        remote: str = "origin",
        branch: Optional[str] = None,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        force: bool = False
    ) -> Tuple[bool, str]:
        """Add file, commit, and push in one operation.
        
        Args:
            file_path: Path to file to commit (can be absolute or relative)
            commit_message: Commit message
            remote: Remote name
            branch: Branch name
            author_name: Author name
            author_email: Author email
            force: Force push
            
        Returns:
            Tuple of (success, message)
        """
        if not self.is_git_repo():
            return False, "Not a Git repository"
        
        # Normalize the file path - handle both absolute and relative paths
        file_path_str = str(file_path).strip()
        
        # If path contains backslashes, ensure they're properly handled
        if '\\' in file_path_str:
            # Windows path - normalize it
            file_path_str = os.path.normpath(file_path_str)
        
        # Create Path object
        file_path_obj = Path(file_path_str)
        
        # If not absolute, try to resolve it
        if not file_path_obj.is_absolute():
            # Try to resolve relative to current working directory
            file_path_obj = Path.cwd() / file_path_obj
            file_path_obj = file_path_obj.resolve()
        else:
            # Absolute path - resolve to normalize
            file_path_obj = file_path_obj.resolve()
        
        # Check if file exists
        if not file_path_obj.exists():
            return False, f"Source file does not exist: {file_path_obj} (original: {file_path})"
        
        # Switch to the correct branch FIRST (before copying file)
        if branch:
            current_branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            current_branch = current_branch_result.stdout.strip() if current_branch_result.returncode == 0 else None
            
            if current_branch != branch:
                # Check if branch exists locally
                branch_exists_result = subprocess.run(
                    ["git", "branch", "--list", branch],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                if not branch_exists_result.stdout.strip():
                    # Branch doesn't exist, create it
                    success, msg = self.create_branch(branch, checkout=True)
                    if not success:
                        return False, f"Failed to create branch '{branch}': {msg}"
                else:
                    # Branch exists, switch to it
                    success, msg = self.checkout_branch(branch)
                    if not success:
                        return False, f"Failed to switch to branch '{branch}': {msg}"
        
        # Now copy file to repository (after we're on the correct branch)
        try:
            # Check if file is already in repo
            rel_path = file_path_obj.relative_to(self.repo_path.resolve())
            repo_file_path = self.repo_path / rel_path
            if not repo_file_path.exists():
                # File doesn't exist in repo, copy it
                success, msg, copied_rel_path = self.copy_file_to_repo(str(file_path_obj))
                if not success:
                    return False, f"Failed to copy file to repository: {msg}"
                rel_path = Path(copied_rel_path)
        except ValueError:
            # File is outside repo, copy it
            success, msg, copied_rel_path = self.copy_file_to_repo(str(file_path_obj))
            if not success:
                return False, f"Failed to copy file to repository: {msg}"
            rel_path = Path(copied_rel_path)
        
        # Verify file exists in repo before adding
        repo_file_path = self.repo_path / rel_path
        if not repo_file_path.exists():
            return False, f"File does not exist in repository: {rel_path} (full path: {repo_file_path})"
        
        # Add file using relative path
        success, msg = self.add_file(str(rel_path))
        if not success:
            return False, f"Add failed: {msg}"
        
        # Verify file was actually staged
        try:
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            # Check if our file is in the staged changes
            staged_files = [line for line in status_result.stdout.split('\n') if line.strip() and line[0] in 'AMD R']
            file_found = any(str(rel_path).replace('\\', '/') in line for line in staged_files)
            if not file_found and not staged_files:
                return False, f"No files staged. File path: {rel_path}, Repo path: {self.repo_path}"
        except subprocess.CalledProcessError:
            pass  # Continue even if status check fails
        
        # Commit
        success, msg = self.commit(commit_message, author_name, author_email)
        if not success:
            return False, f"Commit failed: {msg}"
        
        # Push with upstream tracking (important for new branches)
        success, msg = self.push(remote, branch, force, set_upstream=True)
        if not success:
            return False, f"Push failed: {msg}"
        
        return True, "File committed and pushed successfully"
    
    def list_branches(self, remote: bool = False) -> List[str]:
        """List Git branches.
        
        Args:
            remote: If True, list remote branches; if False, list local branches
            
        Returns:
            List of branch names
        """
        if not self.is_git_repo():
            return []
        
        try:
            cmd = ["git", "branch"]
            if remote:
                cmd.append("-r")
            else:
                cmd.append("-a")  # List all branches (local and remote)
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            branches = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    # Remove markers like '* ' (current branch) and 'remotes/origin/'
                    branch = line.strip().lstrip('* ').strip()
                    if remote and branch.startswith('remotes/'):
                        # Extract branch name from 'remotes/origin/branch-name'
                        branch = '/'.join(branch.split('/')[2:])
                    elif branch.startswith('remotes/'):
                        # For -a, keep remote branches as 'origin/branch-name'
                        branch = '/'.join(branch.split('/')[1:])
                    branches.append(branch)
            
            return sorted(set(branches))  # Remove duplicates and sort
        except subprocess.CalledProcessError:
            return []
    
    def list_remote_branches(self, remote: str = "origin") -> List[str]:
        """List remote branches.
        
        Args:
            remote: Remote name (default: origin)
            
        Returns:
            List of remote branch names
        """
        if not self.is_git_repo():
            return []
        
        # Check if remote exists
        remote_url = self.get_remote_url(remote)
        if not remote_url:
            # Remote doesn't exist, return empty list
            return []
        
        try:
            # Fetch remote branches first (but don't fail if it doesn't work)
            subprocess.run(
                ["git", "fetch", remote],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass  # Continue even if fetch fails
        
        try:
            result = subprocess.run(
                ["git", "branch", "-r"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            branches = []
            for line in result.stdout.strip().split('\n'):
                if line.strip() and remote in line:
                    # Extract branch name from 'remotes/origin/branch-name'
                    branch = line.strip().replace(f'remotes/{remote}/', '').strip()
                    if branch and not branch.startswith('HEAD'):
                        branches.append(branch)
            
            return sorted(branches)
        except subprocess.CalledProcessError:
            return []
    
    def create_branch(self, branch_name: str, checkout: bool = True, base_branch: Optional[str] = None) -> Tuple[bool, str]:
        """Create a new Git branch.
        
        Args:
            branch_name: Name of the branch to create
            checkout: If True, checkout the new branch after creating it
            base_branch: Base branch to create from (default: current branch or main)
            
        Returns:
            Tuple of (success, message)
        """
        if not self.is_git_repo():
            return False, "Not a Git repository"
        
        try:
            # Check if branch already exists
            result = subprocess.run(
                ["git", "branch", "--list", branch_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                if checkout:
                    # Branch exists, just checkout
                    success, msg = self.checkout_branch(branch_name)
                    if success:
                        return True, f"Switched to existing branch '{branch_name}'"
                    return False, msg
                else:
                    return True, f"Branch '{branch_name}' already exists"
            
            if checkout:
                # Create and checkout branch in one command
                if base_branch:
                    # Create from specific base branch
                    result = subprocess.run(
                        ["git", "checkout", "-b", branch_name, base_branch],
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                else:
                    # Create from current branch
                    result = subprocess.run(
                        ["git", "checkout", "-b", branch_name],
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                return True, f"Branch '{branch_name}' created and checked out"
            else:
                # Just create branch without checking out
                if base_branch:
                    result = subprocess.run(
                        ["git", "branch", branch_name, base_branch],
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                else:
                    result = subprocess.run(
                        ["git", "branch", branch_name],
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                return True, f"Branch '{branch_name}' created"
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else e.stdout
            if "already exists" in error_msg.lower():
                if checkout:
                    # Try to checkout existing branch
                    success, msg = self.checkout_branch(branch_name)
                    if success:
                        return True, f"Switched to existing branch '{branch_name}'"
                return False, f"Branch '{branch_name}' already exists"
            return False, f"Failed to create branch: {error_msg}"
        except FileNotFoundError:
            return False, "Git is not installed"
    
    def checkout_branch(self, branch_name: str) -> Tuple[bool, str]:
        """Checkout an existing branch.
        
        Args:
            branch_name: Name of the branch to checkout (can be local branch or remote branch like 'origin/branch-name')
            
        Returns:
            Tuple of (success, message)
        """
        if not self.is_git_repo():
            return False, "Not a Git repository"
        
        # Clean branch name - remove 'origin/' prefix if present
        clean_branch_name = branch_name
        if branch_name.startswith('origin/'):
            clean_branch_name = branch_name.replace('origin/', '', 1)
        elif branch_name.startswith('remotes/origin/'):
            clean_branch_name = branch_name.replace('remotes/origin/', '', 1)
        
        try:
            # First, try to checkout the local branch
            result = subprocess.run(
                ["git", "checkout", clean_branch_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return True, f"Switched to branch '{clean_branch_name}'"
        except subprocess.CalledProcessError:
            # If local branch doesn't exist, try to create a tracking branch from remote
            if branch_name.startswith('origin/') or branch_name.startswith('remotes/origin/'):
                try:
                    # Create and checkout tracking branch: git checkout -b local-branch origin/remote-branch
                    result = subprocess.run(
                        ["git", "checkout", "-b", clean_branch_name, branch_name],
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    return True, f"Created and switched to branch '{clean_branch_name}' tracking '{branch_name}'"
                except subprocess.CalledProcessError as e:
                    error_msg = e.stderr if e.stderr else e.stdout
                    return False, f"Failed to checkout branch '{branch_name}': {error_msg}"
            else:
                # Try original branch name in case it's a valid remote branch format
                try:
                    result = subprocess.run(
                        ["git", "checkout", branch_name],
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    return True, f"Switched to branch '{branch_name}'"
                except subprocess.CalledProcessError as e:
                    error_msg = e.stderr if e.stderr else e.stdout
                    return False, f"Failed to checkout branch '{branch_name}': {error_msg}"
        except FileNotFoundError:
            return False, "Git is not installed"
    
    def get_remote_url(self, remote: str = "origin") -> Optional[str]:
        """Get remote repository URL.
        
        Args:
            remote: Remote name
            
        Returns:
            Remote URL or None
        """
        if not self.is_git_repo():
            return None
        
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", remote],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def set_remote_url(self, remote: str, url: str) -> Tuple[bool, str]:
        """Set remote repository URL.
        
        Args:
            remote: Remote name
            url: Remote URL
            
        Returns:
            Tuple of (success, message)
        """
        if not self.is_git_repo():
            return False, "Not a Git repository"
        
        try:
            # Check if remote exists
            result = subprocess.run(
                ["git", "remote", "get-url", remote],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Remote exists, update it
                subprocess.run(
                    ["git", "remote", "set-url", remote, url],
                    cwd=self.repo_path,
                    check=True
                )
                return True, f"Remote '{remote}' updated"
            else:
                # Remote doesn't exist, add it
                subprocess.run(
                    ["git", "remote", "add", remote, url],
                    cwd=self.repo_path,
                    check=True
                )
                return True, f"Remote '{remote}' added"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to set remote URL: {e.stderr}"


class GitConfigManager:
    """Manage Git configuration securely."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize config manager.
        
        Args:
            config_file: Path to config file (default: ~/.openapi-generator/git_config.json)
        """
        if config_file is None:
            config_file = Path.home() / ".openapi-generator" / "git_config.json"
        
        self.config_file = config_file
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.key_file = self.config_file.parent / ".git_key.key"
        self._ensure_key()
    
    def _ensure_key(self):
        """Ensure encryption key exists."""
        if not self.key_file.exists():
            key = Fernet.generate_key()
            self.key_file.write_bytes(key)
            # Set restrictive permissions (Unix only)
            if os.name != 'nt':
                os.chmod(self.key_file, 0o600)
    
    def _get_key(self) -> bytes:
        """Get encryption key."""
        return self.key_file.read_bytes()
    
    def _encrypt(self, data: str) -> str:
        """Encrypt sensitive data."""
        key = self._get_key()
        f = Fernet(key)
        return f.encrypt(data.encode()).decode()
    
    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        try:
            key = self._get_key()
            f = Fernet(key)
            return f.decrypt(encrypted_data.encode()).decode()
        except Exception:
            return ""
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save Git configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if successful
        """
        try:
            # Encrypt sensitive fields
            secure_config = config.copy()
            if "personal_access_token" in secure_config:
                secure_config["personal_access_token"] = self._encrypt(secure_config["personal_access_token"])
            if "password" in secure_config:
                secure_config["password"] = self._encrypt(secure_config["password"])
            
            # Save to file
            self.config_file.write_text(json.dumps(secure_config, indent=2))
            
            # Set restrictive permissions (Unix only)
            if os.name != 'nt':
                os.chmod(self.config_file, 0o600)
            
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def load_config(self) -> Dict[str, Any]:
        """Load Git configuration.
        
        Returns:
            Configuration dictionary
        """
        if not self.config_file.exists():
            return {}
        
        try:
            config = json.loads(self.config_file.read_text())
            
            # Decrypt sensitive fields
            if "personal_access_token" in config:
                config["personal_access_token"] = self._decrypt(config["personal_access_token"])
            if "password" in config:
                config["password"] = self._decrypt(config["password"])
            
            return config
        except Exception:
            return {}
    
    def get_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """Get stored credentials.
        
        Returns:
            Tuple of (username, token/password)
        """
        config = self.load_config()
        username = config.get("username")
        token = config.get("personal_access_token") or config.get("password")
        return username, token
    
    def configure_credentials(self, username: str, token: str, save: bool = True) -> bool:
        """Configure Git credentials.
        
        Args:
            username: Git username
            token: Personal Access Token or password
            save: Whether to save to file
            
        Returns:
            True if successful
        """
        config = {
            "username": username,
            "personal_access_token": token
        }
        
        if save:
            return self.save_config(config)
        return True

