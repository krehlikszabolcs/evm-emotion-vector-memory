# Emotion Vector Memory (EVM)

Emotion Vector Memory (EVM) is a model-agnostic identity continuity and interaction telemetry standard for long-term AI systems.

**Author:** Szabolcs Krehlik (ORCID: 0009-0003-8623-7876)  
**© 2025–present. All rights reserved.**  
**Patent status:** Filing in preparation / Patent pending

## License and Commercial Use

This repository and the EVM specification are released under:  
**Creative Commons Attribution–NonCommercial–NoDerivatives 4.0 International (CC BY-NC-ND 4.0)**

**Commercial implementation, SaaS deployment, production integration, enterprise usage, and derivative architectural systems are expressly reserved and require a separate written agreement.**  
See: [COMMERCIAL_LICENSE_REQUIRED.md](COMMERCIAL_LICENSE_REQUIRED.md) and [PATENT_NOTICE.md](PATENT_NOTICE.md)

## Official Specification (Canonical / Normative)

The canonical normative specification is published on Zenodo:

**EVM v2.1 — Unified Directed Vector Identity Standard**  
https://zenodo.org/records/18664771

GitHub content is provided for visibility and reference implementation examples. The Zenodo DOI release remains the authoritative standard.

## What EVM Defines (v2.1)

EVM defines a closed directed vector interaction ontology:

- Each interaction generates exactly one directed vector segment: **EVᵢ = (x1,y1,z1,g1,e1,w1) → (x2,y2,z2,g2,e2,w2)**
- Dual-track identity separation: **PEV (human trajectory)** and **EEV (AI entity trajectory)**
- **FEV envelope constraint** with boundary recovery to prevent fixation
- Deterministic logging and reconstructability
- Interoperability extensions via **Appendix A**, including:
  - default distance metric
  - extractor determinism requirements
  - Canonical Identity Snapshot (**CIS**) export format

## Repository Contents

- `docs/` — standard mirror excerpts, Appendix A, CIS examples, integration notes
- `reference/` — minimal reference implementation and demo scripts (non-intrusive side-module)
- `.github/` — issue templates and contribution guidance

## Quick Start (Conceptual)

1. Extract **entry endpoint** from user message.
2. Generate model response (EVM does not interfere).
3. Extract **exit endpoint** from the model response.
4. Update:
   - PEV from entry endpoint
   - EEV from exit endpoint (FEV-bounded + recovery)
5. Append EV to an append-only EV log
6. Export CIS snapshots for portability/audit

See: [docs/INTEGRATION_QUICKSTART.md](docs/INTEGRATION_QUICKSTART.md)

## Citation

If you use or reference EVM academically, please cite the Zenodo DOI release.  
See: [CITATION.cff](CITATION.cff)

## Contact

For collaboration or licensing:  
Szabolcs Krehlik — ORCID: 0009-0003-8623-7876  
Email: szabolcs.krehlik@gmail.com  
X: @KrehlikSzabolcs
