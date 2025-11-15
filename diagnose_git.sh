#!/bin/bash
# Diagnose Git Repository Status

echo "=== Current Directory ==="
pwd

echo ""
echo "=== Checking for .git folder ==="
if [ -d ".git" ]; then
    echo "✅ .git folder exists"
else
    echo "❌ .git folder NOT found"
    echo "This directory is not a git repository"
fi

echo ""
echo "=== Checking git status ==="
git status 2>&1

echo ""
echo "=== Checking remote ==="
git remote -v 2>&1

echo ""
echo "=== Checking for AI ontology files ==="
if [ -f "nemesis/AI_THREAT_ONTOLOGY_SPEC.md" ]; then
    echo "✅ AI_THREAT_ONTOLOGY_SPEC.md exists"
else
    echo "❌ AI_THREAT_ONTOLOGY_SPEC.md NOT found"
fi

if [ -d "nemesis/ai_ontology" ]; then
    echo "✅ ai_ontology directory exists"
    ls -la nemesis/ai_ontology/
else
    echo "❌ ai_ontology directory NOT found"
fi

echo ""
echo "=== All files in nemesis/ ==="
ls -la nemesis/ 2>&1 | head -20

