#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Environment Cleanup Script

This script helps clean up packages in your global Python environment by:
1. Comparing global packages with your virtual environment
2. Identifying project-specific packages that can be safely removed
3. Preserving essential development tools (Jupyter, IPython, etc.)
4. Creating a backup before any changes
5. Providing a dry-run mode to preview changes
"""

import subprocess
import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Set console encoding for Windows compatibility
if sys.platform == 'win32':
    try:
        # Try to set UTF-8 encoding for Windows console
        os.system('chcp 65001 >nul 2>&1')
    except:
        pass


# Essential development tools to keep (even if in venv)
ESSENTIAL_TOOLS = {
    'jupyter', 'jupyterlab', 'ipython', 'ipykernel', 'notebook',
    'pip', 'setuptools', 'wheel', 'pipx', 'black', 'pytest', 
    'flake8', 'mypy', 'autopep8'
}

# Core system packages that should NEVER be removed
CORE_PACKAGES = {
    'pip', 'setuptools', 'wheel'
}


def get_packages(venv_path=None):
    """Get installed packages from either global or venv environment."""
    if venv_path:
        python_exe = Path(venv_path) / 'Scripts' / 'python.exe'
        if not python_exe.exists():
            raise FileNotFoundError(f"Virtual environment not found at {venv_path}")
        cmd = [str(python_exe), '-m', 'pip', 'list', '--format=json']
    else:
        cmd = [sys.executable, '-m', 'pip', 'list', '--format=json']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        packages = json.loads(result.stdout)
        return {pkg['name'].lower(): pkg['version'] for pkg in packages}
    except subprocess.CalledProcessError as e:
        print(f"Error getting packages: {e.stderr}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing package list: {e}")
        return {}


def load_requirements(requirements_file='requirements.txt'):
    """Load packages from requirements.txt."""
    req_file = Path(requirements_file)
    if not req_file.exists():
        return set()
    
    packages = set()
    with open(req_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract package name (remove version specifiers)
                pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].split('[')[0].strip()
                packages.add(pkg_name.lower())
    return packages


def identify_project_dependencies(global_packages, venv_packages, requirements):
    """Identify packages that are likely project dependencies."""
    project_deps = set()
    
    # Packages that are in requirements.txt
    for req in requirements:
        if req in global_packages:
            project_deps.add(req)
    
    # Packages that are in venv but also in global (likely project deps)
    common_packages = set(global_packages.keys()) & set(venv_packages.keys())
    for pkg in common_packages:
        if pkg not in ESSENTIAL_TOOLS:
            project_deps.add(pkg)
    
    return project_deps


def identify_safe_to_remove(global_packages, venv_packages, requirements):
    """Identify packages safe to remove from global environment."""
    safe_to_remove = set()
    keep = set()
    
    project_deps = identify_project_dependencies(global_packages, venv_packages, requirements)
    
    for pkg_name in global_packages:
        pkg_lower = pkg_name.lower()
        
        # Always keep core packages
        if pkg_lower in CORE_PACKAGES:
            keep.add(pkg_name)
            continue
        
        # Keep essential development tools
        if pkg_lower in ESSENTIAL_TOOLS:
            keep.add(pkg_name)
            continue
        
        # If it's a project dependency and also in venv, safe to remove from global
        if pkg_name in project_deps:
            if pkg_lower in venv_packages:
                safe_to_remove.add(pkg_name)
                continue
        
        # If it's in requirements.txt (project dependency), safe to remove if in venv
        if pkg_lower in requirements:
            if pkg_lower in venv_packages:
                safe_to_remove.add(pkg_name)
    
    return safe_to_remove, keep


def create_backup(global_packages, backup_file):
    """Create a backup of global packages."""
    backup_path = Path(backup_file)
    with open(backup_path, 'w') as f:
        for pkg_name, version in sorted(global_packages.items()):
            f.write(f"{pkg_name}=={version}\n")
    print(f"[OK] Backup created: {backup_file}")
    return backup_path.exists()


def uninstall_packages(packages, dry_run=True):
    """Uninstall packages from global environment."""
    if not packages:
        print("No packages to uninstall.")
        return
    
    if dry_run:
        print("\n" + "="*60)
        print("DRY RUN - No packages will be uninstalled")
        print("="*60)
        for pkg in sorted(packages):
            print(f"  Would uninstall: {pkg}")
        print(f"\nTotal packages to uninstall: {len(packages)}")
        return
    
    print(f"\nUninstalling {len(packages)} packages...")
    cmd = [sys.executable, '-m', 'pip', 'uninstall', '-y'] + list(packages)
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n[OK] Successfully uninstalled {len(packages)} packages")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Error during uninstallation: {e}")
        sys.exit(1)


def main():
    """Main cleanup function."""
    print("Global Environment Cleanup Script")
    print("="*60)
    
    # Check if venv exists
    venv_path = Path(__file__).parent / 'venv'
    if not venv_path.exists():
        print("\n[WARNING] Virtual environment not found at './venv'")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
        venv_packages = {}
    else:
        print(f"\n[OK] Found virtual environment at: {venv_path}")
        venv_packages = get_packages(venv_path)
        print(f"  Packages in venv: {len(venv_packages)}")
    
    # Get global packages
    print("\n[OK] Analyzing global environment...")
    global_packages = get_packages()
    print(f"  Packages in global: {len(global_packages)}")
    
    # Load requirements
    requirements = load_requirements()
    if requirements:
        print(f"[OK] Loaded {len(requirements)} packages from requirements.txt")
    
    # Identify safe to remove
    safe_to_remove, keep = identify_safe_to_remove(
        global_packages, venv_packages, requirements
    )
    
    # Display results
    print("\n" + "="*60)
    print("ANALYSIS RESULTS")
    print("="*60)
    print(f"\nTotal packages in global: {len(global_packages)}")
    print(f"Packages to keep: {len(keep)}")
    print(f"Packages safe to remove: {len(safe_to_remove)}")
    
    if safe_to_remove:
        print("\n\nPackages safe to remove from global environment:")
        print("-" * 60)
        for pkg in sorted(safe_to_remove):
            version = global_packages.get(pkg, 'unknown')
            in_venv = "[OK]" if pkg.lower() in venv_packages else "[--]"
            print(f"  {in_venv} {pkg:<30} {version}")
    
    if not safe_to_remove:
        print("\n[OK] No packages identified for removal. Your global environment looks clean!")
        return
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"global_packages_backup_{timestamp}.txt"
    
    print("\n" + "="*60)
    print("BACKUP & UNINSTALL OPTIONS")
    print("="*60)
    
    # Dry run first
    print("\n1. DRY RUN (Preview only - no changes):")
    uninstall_packages(safe_to_remove, dry_run=True)
    
    # Ask for confirmation
    print("\n" + "="*60)
    response = input("\nCreate backup and uninstall these packages? (y/N): ")
    
    if response.lower() != 'y':
        print("\nAborted. No packages were uninstalled.")
        return
    
    # Create backup
    print("\nCreating backup...")
    if create_backup(global_packages, backup_file):
        print(f"   Backup saved to: {backup_file}")
        print("   You can restore packages with: pip install -r " + backup_file)
    
    # Final confirmation
    print("\n" + "="*60)
    print(f"[WARNING] About to uninstall {len(safe_to_remove)} packages from global environment")
    final_confirm = input("Type 'yes' to confirm: ")
    
    if final_confirm.lower() != 'yes':
        print("\nAborted. No packages were uninstalled.")
        return
    
    # Uninstall
    uninstall_packages(safe_to_remove, dry_run=False)
    
    print("\n" + "="*60)
    print("[OK] Cleanup complete!")
    print(f"[OK] Backup saved to: {backup_file}")
    print("\nTip: Always use virtual environments for projects to avoid this in the future!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        sys.exit(1)

