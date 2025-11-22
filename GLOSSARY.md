# GH Systems Glossary
**Mapping Greek Mythology to Engineering Domains**

This glossary maps the product/marketing names (Greek gods) to their engineering implementations. Use this when onboarding new engineers or debugging issues.

---

## Core Components

### **Hades** → `behavioral_profiling/` or `hades/`
**Product Name:** Hades (God of the Underworld)  
**Engineering Domain:** Behavioral Profiling Engine  
**Purpose:** Analyzes individual threat actor behavior, generates risk scores, predicts off-ramps  
**Key Files:**
- `hades/behavioral_profiler.py` - Core profiling logic
- `hades/risk_scorer.py` - Risk score calculation
- `nemesis/ai_ontology/behavioral_signature.py` - AI-powered signature generation

**What it does:**
- Profiles individual actors (wallets, individuals, organizations)
- Generates behavioral signatures from transaction patterns
- Calculates risk scores and flight risk indicators
- Predicts off-ramp locations and timing preferences

---

### **Echo** → `coordination_detection/` or `echo/`
**Product Name:** Echo (Nymph who repeats sounds)  
**Engineering Domain:** Coordination Detection Engine  
**Purpose:** Detects coordination networks, facilitator rings, multi-actor operations  
**Key Files:**
- `echo/coordination_detector.py` - Core coordination detection
- `echo/network_mapper.py` - Network graph generation
- `nemesis/ai_ontology/relationship_inference.py` - AI-powered relationship inference

**What it does:**
- Detects coordination between multiple actors
- Maps facilitator networks
- Identifies coordination rings and clusters
- Surfaces hidden relationships

---

### **Nemesis** → `targeting_engine/` or `nemesis/`
**Product Name:** Nemesis (Goddess of Retribution)  
**Engineering Domain:** Pre-emptive Targeting Engine  
**Purpose:** Generates executable targeting packages with confidence scores  
**Key Files:**
- `nemesis/compilation_engine.py` - Core compilation logic
- `nemesis/ai_ontology/predictive_modeling.py` - Risk propensity modeling
- `nemesis/ai_ontology/threat_dossier_generator.py` - Dossier generation

**What it does:**
- Compiles intelligence into targeting packages
- Generates risk propensity assessments (mobilization index, volatility score)
- Creates threat dossiers
- Produces executable intelligence with confidence scores

---

### **Hypnos** → `long_term_memory/` or `hypnos/`
**Product Name:** Hypnos (God of Sleep)  
**Engineering Domain:** Long-Term Memory & Pattern Consolidation  
**Purpose:** Maintains persistent intelligence graph, consolidates patterns, tracks dormant threats  
**Key Files:**
- `hypnos/memory_engine.py` - Core memory system
- `hypnos/pattern_consolidator.py` - Pattern consolidation
- `hypnos/dormant_threat_tracker.py` - Dormant threat tracking

**What it does:**
- Maintains long-term intelligence graph
- Consolidates patterns across time
- Tracks dormant threats that may re-emerge
- Provides foundation for Hades/Echo/Nemesis

---

## System Architecture

### **ABC (Adversarial Behavior Compiler)**
**Product Name:** ABC  
**Engineering Domain:** Core compilation engine  
**Purpose:** Orchestrates Hades, Echo, and Nemesis to compile intelligence  
**Key Files:**
- `nemesis/compilation_engine.py` - Main compilation logic
- `nemesis/ai_ontology/integration_layer.py` - AI ontology integration

**What it does:**
- Ingests vendor feeds (Chainalysis, TRM, Chaos)
- Orchestrates Hades (profiling), Echo (coordination), Nemesis (targeting)
- Compiles intelligence into actionable packages
- Generates cryptographic receipts

---

## Data Flow

```
Raw Telemetry (Vendor Feeds)
    ↓
[ABC Compilation Engine]
    ↓
[Hades] → Behavioral Profiling
    ↓
[Echo] → Coordination Detection
    ↓
[Nemesis] → Targeting Packages
    ↓
[Hypnos] → Long-Term Memory
    ↓
Output: Targeting Packages + Cryptographic Receipts
```

---

## Quick Reference

| Product Name | Engineering Path | Purpose |
|--------------|------------------|---------|
| **Hades** | `hades/` or `behavioral_profiling/` | Behavioral profiling, risk scoring |
| **Echo** | `echo/` or `coordination_detection/` | Coordination detection, network mapping |
| **Nemesis** | `nemesis/` or `targeting_engine/` | Targeting packages, threat dossiers |
| **Hypnos** | `hypnos/` or `long_term_memory/` | Long-term memory, pattern consolidation |
| **ABC** | `nemesis/compilation_engine.py` | Core compilation orchestrator |

---

## Debugging Guide

**Issue: Risk scores seem wrong**
→ Check `hades/` or `behavioral_profiling/` components

**Issue: Missing coordination relationships**
→ Check `echo/` or `coordination_detection/` components

**Issue: Targeting packages not generating**
→ Check `nemesis/` or `targeting_engine/` components

**Issue: Patterns not persisting**
→ Check `hypnos/` or `long_term_memory/` components

**Issue: Compilation failing**
→ Check `nemesis/compilation_engine.py` and integration layer

---

*GH Systems — Compiling behavioral bytecode so lawful actors win the economic battlefield.*

