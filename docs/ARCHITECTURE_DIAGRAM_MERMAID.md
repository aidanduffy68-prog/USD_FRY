# Detailed Architecture Diagram (Mermaid)
**Local reference - not in main README**

This is the detailed Mermaid diagram showing the complete data flow. The main README uses the eye-catching custom image; this diagram provides the detailed technical flow for reference.

```mermaid
graph TD
    A[Raw Telemetry] -->|Ingest| B(Normalizer)
    B -->|Validation| C{Valid Data?}
    C -->|Yes| D[Hypnos DB]
    C -->|No| E[Dead Letter Queue]
    D -->|Async Job| F[Hades Profiler]
    F -->|Risk Score| G[API Output]
    D -->|Async Job| H[Echo Network]
    H -->|Coordination| G
    D -->|Async Job| I[Nemesis Targeting]
    I -->|Targeting Package| G
    G -->|Cryptographic Receipt| J[Bitcoin Blockchain]
    G -->|Settlement| K[Oracle Service]
    K -->|BTC| L[Vendor]
    
    classDef blackNode fill:#000000,stroke:#00ff00,stroke-width:2px,color:#ffffff
    classDef greenNode fill:#00ff00,stroke:#000000,stroke-width:2px,color:#000000
    classDef decisionNode fill:#1a1a1a,stroke:#00ff00,stroke-width:2px,color:#00ff00
    
    class A,B,D,F,H,I,G,J,K,L blackNode
    class E greenNode
    class C decisionNode
```

## Data Flow Description

1. **Raw Telemetry** - Vendor feeds (Chainalysis, TRM, Chaos, research feeds)
2. **Normalizer** - Data normalization and format standardization
3. **Validation** - Pydantic schema validation (compiler fails on bad data)
4. **Hypnos DB** - Long-term memory storage (validated data only)
5. **Dead Letter Queue** - Invalid data handling (error path)
6. **Hades Profiler** - Behavioral profiling and risk scoring (async)
7. **Echo Network** - Coordination detection (async)
8. **Nemesis Targeting** - Targeting package generation (async)
9. **API Output** - Compiled intelligence packages
10. **Bitcoin Blockchain** - Cryptographic receipts (OP_RETURN)
11. **Oracle Service** - Fiat-to-BTC conversion for government clients
12. **Vendor** - BTC settlement to intelligence providers

