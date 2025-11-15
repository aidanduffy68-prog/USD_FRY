#!/bin/bash
# Fix GitHub authentication

cd "/Users/AidanMDuffy/Desktop/[GREENHOUSE & COMPANY]/trading view /cursor/USD_FRY"

echo "Enter your GitHub Personal Access Token:"
read -s token

# Update remote URL with token embedded
git remote set-url origin https://${token}@github.com/aidanduffy68-prog/ABC.git

echo ""
echo "✅ Remote URL updated with token"
echo "Now try: git push origin main"

