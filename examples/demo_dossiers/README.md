# Demo Threat Dossiers

**These are demonstration artifacts, not operational intelligence.**

These threat dossiers are AI-generated examples for demonstration purposes. They showcase the capability of the ABC compilation engine but are not real operational intelligence.

## Purpose

- **Demonstration**: Show how ABC compiles intelligence into threat dossiers
- **Testing**: Validate dossier generation templates and formats
- **Documentation**: Provide examples for integration partners

## Structure

- `THREAT_DOSSIER_NASA_001.md` - Example federal AI security dossier
- `THREAT_DOSSIER_DOD_DHS_002.md` - Example multi-agency dossier
- `THREAT_DOSSIER_ALPHA_47.md` - Example crypto threat actor dossier

## Operational Intelligence

Real operational threat dossiers are stored in the Hypnos database, not in markdown files in the repository. The dossier generator (`nemesis/ai_ontology/threat_dossier_generator.py`) creates dossiers on-demand from the intelligence graph.

## Templates

The dossier generation templates and scripts are in:
- `nemesis/ai_ontology/threat_dossier_generator.py` - Dossier generator
- `nemesis/threat_profiles/` - Template files (if any)

---

*GH Systems — Compiling behavioral bytecode so lawful actors win the economic battlefield.*

