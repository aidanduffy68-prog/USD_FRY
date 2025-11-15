#!/bin/bash
cd "/Users/AidanMDuffy/Desktop/[GREENHOUSE & COMPANY]/trading view /cursor/USD_FRY"

echo "Checking git remote..."
git remote -v

echo ""
echo "Checking if repository exists..."
curl -s -o /dev/null -w "%{http_code}" https://api.github.com/repos/aidanduffy68-prog/ABC

echo ""
echo ""
echo "The token needs 'repo' scope. Make sure when you generated it, you checked 'repo' (full control)."

