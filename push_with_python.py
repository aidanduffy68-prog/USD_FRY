#!/usr/bin/env python3
"""
Python script to push AI Ontology implementation to GitHub
Alternative to bash script if terminal has issues
"""

import subprocess
import os
import sys

def run_command(cmd, description):
    """Run a git command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print('='*60)
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def main():
    # Change to project directory
    project_dir = "/Users/AidanMDuffy/Desktop/[GREENHOUSE & COMPANY]/trading view /cursor/USD_FRY"
    
    print(f"Changing to directory: {project_dir}")
    os.chdir(project_dir)
    print(f"Current directory: {os.getcwd()}")
    
    # Check if .git exists
    if not os.path.exists(".git"):
        print("⚠️  .git folder not found. Initializing repository...")
        if not run_command("git init", "Initialize git repository"):
            return
        if not run_command("git branch -M main", "Set branch to main"):
            return
    
    # Set remote
    remote_url = "https://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@github.com/aidanduffy68-prog/ABC.git"
    run_command(f"git remote set-url origin {remote_url}", "Set remote URL")
    
    # Stage files
    if not run_command("git add -A", "Stage all files"):
        return
    
    # Show status
    print("\nFiles to be committed:")
    run_command("git status --short", "Show git status")
    
    # Commit
    if not run_command('git commit -m "plotting and scheming"', "Commit changes"):
        print("⚠️  Nothing to commit (files may already be committed)")
    
    # Push
    if not run_command("git push origin main", "Push to GitHub"):
        print("⚠️  Trying with -u flag...")
        run_command("git push -u origin main", "Push with upstream")
    
    print("\n✅ Done! Check GitHub to verify push was successful.")

if __name__ == "__main__":
    main()

