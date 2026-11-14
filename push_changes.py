#!/usr/bin/env python3
"""Helper script to commit and push changes to GitHub"""
import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

try:
    # Configure git if needed
    subprocess.run(['git', 'config', 'user.email', 'deployment@ecommerce.local'], check=False)
    subprocess.run(['git', 'config', 'user.name', 'Deploy Bot'], check=False)
    
    # Stage all changes
    result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
    print(f"git add: {result.stdout}{result.stderr}")
    
    # Commit
    result = subprocess.run(['git', 'commit', '-m', 'Fix: Update root endpoint and improve CSRF/security settings'], capture_output=True, text=True)
    print(f"git commit: {result.stdout}{result.stderr}")
    
    # Push to main
    result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
    print(f"git push: {result.stdout}{result.stderr}")
    
    print("\n✓ Changes pushed successfully!")
    sys.exit(0)
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
