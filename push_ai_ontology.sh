#!/bin/bash
# Push AI Ontology Implementation to GitHub
set -e  # Exit on error
set -x  # Show commands as they run

echo "Starting push process..."

# Navigate to project directory
cd "/Users/AidanMDuffy/Desktop/[GREENHOUSE & COMPANY]/trading view /cursor/USD_FRY" || {
    echo "❌ Failed to change directory"
    exit 1
}

echo "Current directory: $(pwd)"

# Check if .git exists
if [ ! -d ".git" ]; then
    echo "⚠️  .git folder not found. Initializing repository..."
    git init
    git branch -M main
fi

# Set remote with token
echo "Setting remote URL..."
git remote set-url origin https://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@github.com/aidanduffy68-prog/ABC.git || {
    echo "⚠️  Remote already exists, updating..."
    git remote add origin https://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@github.com/aidanduffy68-prog/ABC.git 2>/dev/null || true
}

# Stage all changes
echo "Staging files..."
git add -A

# Show what will be committed
echo "Files to be committed:"
git status --short

# Commit
echo "Committing changes..."
git commit -m "plotting and scheming" || {
    echo "⚠️  Nothing to commit (files may already be committed)"
}

# Push to main
echo "Pushing to GitHub..."
git push origin main || {
    echo "❌ Push failed. Trying with -u flag..."
    git push -u origin main
}

echo "✅ AI Ontology implementation pushed successfully!"

