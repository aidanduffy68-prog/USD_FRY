# How to Push AI Ontology Implementation

## Quick Method (Run Script)

1. Open Terminal
2. Navigate to your project:
   ```bash
   cd "/Users/AidanMDuffy/Desktop/[GREENHOUSE & COMPANY]/trading view /cursor/USD_FRY"
   ```
3. Make script executable and run:
   ```bash
   chmod +x push_ai_ontology.sh
   ./push_ai_ontology.sh
   ```

## Manual Method (Copy-Paste)

Run these commands one by one in Terminal:

```bash
cd "/Users/AidanMDuffy/Desktop/[GREENHOUSE & COMPANY]/trading view /cursor/USD_FRY"
git remote set-url origin https://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@github.com/aidanduffy68-prog/ABC.git
git add -A
git commit -m "plotting and scheming"
git push origin main
```

## What's Being Pushed

- ✅ `nemesis/AI_THREAT_ONTOLOGY_SPEC.md` - Complete AI ontology specification
- ✅ `nemesis/AI_ONTOLOGY_INTEGRATION.md` - Implementation roadmap
- ✅ `nemesis/README.md` - Updated with AI positioning
- ✅ `AI_ONTOLOGY_UPGRADE.md` - Summary document
- ✅ `nemesis/ai_ontology/semantic_understanding.py` - LLM-based entity extraction
- ✅ `nemesis/ai_ontology/auto_classification.py` - Threat classification system
- ✅ `nemesis/ai_ontology/relationship_inference.py` - GNN relationship inference
- ✅ `nemesis/ai_ontology/__init__.py` - Module exports
- ✅ `nemesis/ai_ontology/requirements.txt` - Dependencies

## Troubleshooting

**If "not a git repository" error:**
```bash
git init
git remote add origin https://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@github.com/aidanduffy68-prog/ABC.git
git branch -M main
git add -A
git commit -m "plotting and scheming"
git push -u origin main
```

**If authentication fails:**
- Token may have expired, generate new one at: https://github.com/settings/tokens

