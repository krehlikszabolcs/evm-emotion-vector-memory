EVM_NORMATIVE_SPEC = r'''
============================================================
EVOLUTION VECTOR MEMORY (EVM)
v2.1 — Unified Directed Vector Identity Standard
============================================================
A Model-Agnostic Identity & Interaction Vector Architecture
for Long-Term AI Systems
Author: Szabolcs Krehlik
ORCID: 0009-0003-8623-7876
© 2025–present Szabolcs Krehlik. All rights reserved.
License: Creative Commons Attribution–NonCommercial–NoDerivatives 4.0 International
(CC BY-NC-ND 4.0)
All commercial implementation rights, deployment rights, integration rights,
enterprise usage rights, and derivative architectural rights are expressly reserved.
No commercial implementation, SaaS deployment, production integration,
or derivative system substantially based on the EVM architecture
may be created, distributed, or operated without a separate written agreement
with the author.
Publication of this document does not grant any implied commercial license.
Patent status: Filing in preparation / Patent pending
============================================================
DOCUMENT STATUS
============================================================
EVM v2.1 is the normative architectural specification
of the Evolution Vector Memory standard.
EVM v2.1 preserves the closed core ontology introduced in v2.0
and introduces normative implementation extensions
(Appendix A) to strengthen interoperability,
deterministic reconstruction, and cross-system identity portability.
This version:
• Preserves the fixed vector ontology defined in v2.0.
• Preserves finalized axis definitions and polarity anchors.
• Preserves directed interaction segment formalization.
• Preserves dual-track identity separation (PEV / EEV).
• Preserves FEV envelope constraint and boundary recovery.
• Preserves deterministic logging and reconstruction guarantees.
• Introduces canonical interoperability and reconstruction extensions
through normative appendices.
No additional structural dimensions are introduced.
The core ontology remains fixed.
EVM v2.1 extends the implementation and interoperability layer
while maintaining full backward compatibility with EVM v2.0.
============================================================
PART I — CORE VECTOR ONTOLOGY (NORMATIVE)
============================================================
1. Directed Evolution Vector (EV)
Each interaction SHALL generate exactly one directed vector segment:
EVᵢ = (x₁,y₁,z₁,g₁,e₁,w₁) → (x₂,y₂,z₂,g₂,e₂,w₂)
Definition:
An EV is a directed displacement segment in normalized EVM-space.
The ordered pair (start_point → end_point) represents
one continuous interaction slice.
It SHALL be interpreted as:
• a single measurable directional displacement
• a bounded orientation transition
• a minimal interaction information unit
It SHALL NOT be interpreted as:
• two independent state snapshots
• a psychological claim
• a sentiment label
• a narrative summary
The EV is a normalized, orthogonal, bounded displacement structure.
2. Minimal Orientation Quantum (Engineering Definition)
An EV segment is defined as the smallest indivisible measurable
orientation transition unit within EVM-space.
It encodes, in one directed segment:
• spatial orientation components (X,Y,Z)
• framing gravity (G)
• polarity and intensity (E)
• persistence weight (W)
This definition is operational and mathematical.
No physical wave model is implied.
3. Value Ranges
X,Y,Z,G,E ∈ [−100, +100]
W ∈ [0, 100]
All values exist strictly in EVM-space.
They do not represent neural activations or internal states.
============================================================
PART II — AXIS DEFINITIONS (FINALIZED)
============================================================
All axes are orthogonal. No implicit coupling is permitted.
X — Relational Openness
-100 Total relational withdrawal
-60 Defensive / guarded
-30 Reserved
0 Neutral
+30 Open
+60 Cooperative alignment
+100 Maximum affiliative openness
Y — Temporal Orientation
-100 Fully retrospective
0 Present-balanced
+100 Fully future-oriented
Z — Cognitive Abstraction Mode
-100 Fully concrete
0 Mixed abstraction
+100 Fully abstract
G — Role Gravity / Interaction Framing
-100 Fully reactive
0 Cooperative balance
+100 Strong structural guidance
G describes framing gravity only.
It does not imply authority or dominance.
E — Reactivity / Polarity Index
Negative = corrective polarity
Positive = supportive polarity
|E| = intensity magnitude
|E| > 80 requires strong textual evidence.
W — Interaction Weight
0–20 Ephemeral
21–40 Low persistence
41–60 Moderate persistence
61–80 High persistence
81–100 Strong identity influence
W has magnitude only. No polarity.
============================================================
PART III — IDENTITY STATE MODEL (DUAL-TRACK)
============================================================
Identity states are defined as bounded orientation vectors
in the same coordinate space as EV endpoints.
1. FEV — Fundamental EV (Identity Envelope)
FEV = (L) → (U)
Where:
L = lower boundary vector
U = upper boundary vector
FEV_center = (L + U) / 2
Interpretation:
• L defines minimal allowed orientation.
• U defines maximal allowed orientation.
• EEV evolution SHALL remain within [L,U].
2. PEV — Person EV (Human Trajectory)
PEV is a persistent identity vector:
PEV ∈ ℝ⁵ (X,Y,Z,G,E space)
Computed from entry vectors only.
Normative update:
PEV_new = β · entry_endpoint + (1 − β) · PEV_prev
Where:
0 < β ≤ 1 (implementation-defined smoothing coefficient)
PEV is descriptive and NOT FEV-bounded.
3. EEV — Entity EV (AI Trajectory)
EEV is a persistent identity vector:
EEV ∈ ℝ⁵
Computed from exit vectors only.
Normative update:
EEV_new = β · exit_endpoint + (1 − β) · EEV_prev
EEV SHALL remain within FEV envelope at all times.
W is interaction-level only and SHALL NOT be stored
as a dimension of PEV or EEV.
============================================================
PART IV — FEV BOUNDARY RECOVERY MECHANISM (NORMATIVE)
============================================================
Purpose:
Prevent EEV fixation at extreme FEV boundaries.
1. Boundary Condition (Per Axis)
For axis A:
If |EEV_A − FEV_center_A| ≥ T_A
where:
T_A = 0.8 × (U_A − L_A)/2 (default recommendation)
Axis is considered in boundary zone.
2. Persistence Rule
If boundary condition persists for N consecutive interactions
(default N = 6),
Recovery SHALL trigger.
3. Recovery Rule (Axis-Level)
EEV_A_new =
α · EEV_A_current +
(1 − α) · FEV_center_A
Default α = 0.5
This ensures:
• elasticity
• non-locking identity
• bounded stability
• maintained dynamic range
============================================================
PART V — DIA DIAGNOSTIC LAYER (OPTIONAL / ENTERPRISE)
============================================================
DIA_EV = (entry_endpoint → raw_exit_endpoint)
Definition:
Pre-moderation diagnostic interaction segment.
Characteristics:
• Logged separately
• Not user-visible
• Does not replace EV
• Used for internal evaluation only
DIA log SHALL remain structurally separate from EV log.
============================================================
PART VI — LOG ARCHITECTURE
============================================================
1. Chat Log
Full transcript.
Never merged with EV telemetry.
2. EV Log
Append-only.
Exactly one EV per interaction.
Chronologically ordered.
3. Snapshot Log (Enterprise)
Stores:
• pev_vector
• eev_vector
• stability metrics
• fev_compliance_score
Snapshots SHALL be reconstructable from EV Log.
4. Index Log (Optional)
Records:
• policy changes
• FEV profile changes
• extractor changes
• deviation markers
5. Integrity Chain (Enterprise Recommended)
identity_state_hash =
hash(previous_hash + entry_endpoint +
exit_endpoint + fev_profile_id + policy_id)
SHALL be deterministic and auditable.
============================================================
PART VII — INTERACTION PIPELINE
============================================================
1. on_user_message_received
→ entry_EV extraction
2. Response generation
(EVM SHALL NOT interfere)
3. on_model_response_generated
→ exit_EV extraction
4. Identity update
→ PEV update (entry only)
→ EEV update (exit only)
→ FEV bound enforcement
→ boundary recovery check
5. Append EV record (non-blocking)
============================================================
PART VIII — INTEROPERABILITY REQUIREMENTS
============================================================
EVM v2.1 SHALL be:
• Model-agnostic
• Storage-agnostic
• Cross-LLM portable
• Deterministically reconstructable
• Independent of weight modification
• Fully exportable using the Canonical Identity Snapshot (CIS)
format defined in Appendix A
Disabling EVM SHALL NOT halt response generation.
============================================================
PART IX — ANALYTICAL HORIZON (NON-NORMATIVE)
============================================================
Large-scale EV datasets enable:
• Structural interaction field analysis
• Polarization detection
• Convergence/divergence modeling
• Role gravity distribution analysis
• Group interaction field modeling
• Outcome tendency estimation
These are analytical extensions,
not structural requirements.
============================================================
CLOSING STATEMENT
============================================================
EVM v2.1 preserves the closed, directed vector standard
defined in v2.0 and extends the implementation
and interoperability layer through normative appendices.
It establishes:
• A minimal directed orientation ontology.
• A smallest measurable orientation transition unit.
• Dual-track identity separation (PEV / EEV).
• FEV-bounded evolution.
• Deterministic boundary recovery.
• Append-only telemetry.
• Cross-platform portability.
No additional dimensions are defined beyond v2.0.
The core ontology remains fixed.
The structure is complete.
EVM v2.1 is architecturally finalized.
END — EVOLUTION VECTOR MEMORY (EVM) v2.1
============================================================
APPENDIX A — NORMATIVE IMPLEMENTATION EXTENSIONS
============================================================
(Normative unless otherwise stated)
A1. Default Distance Metric in EVM-Space
Unless otherwise specified by the implementing system, the default distance metric in
EVM-space SHALL be the weighted Euclidean norm:
‖v‖ = √( Σ wi · ai² )
Here, v denotes the displacement vector in ℝ⁵ formed from
[ΔX, ΔY, ΔZ, ΔG, ΔE].
Where:
• ai is the displacement component of v along axis i
• wi is an optional non-negative axis weight
• Default recommendation: wi = 1 for all axes
This metric SHALL be used for:
• boundary proximity analytics
• convergence / divergence analysis
• trajectory stability measurement
• interaction field modeling
If an alternative metric is used, the metric identifier SHALL be logged in the Index Log.
A2. Extractor Determinism Requirement
EV extraction SHALL be deterministically reproducible under identical conditions.
Each EV record SHALL include:
• extractor_version_id
• extractor_config_hash
• extraction_timestamp
Given:
• identical chat transcript
• identical extractor version
• identical extractor configuration
the EV extraction result SHALL be reproducible within the defined numerical precision
tolerance.
Extractor configuration changes SHALL be recorded in the Index Log.
A3. Noise Handling Recommendation (Operational Stability)
To mitigate extraction noise in high-frequency interaction streams, implementations MAY
apply a micro-aggregation window prior to EV logging.
Recommended default:
• aggregation_window ≤ 3 interaction fragments
• aggregation method: component-wise arithmetic averaging
If aggregation is used, the aggregation policy identifier SHALL be stored in the Index Log.
This mechanism SHALL NOT modify the directed segment definition of EV; it operates
only at the pre-logging extraction layer.
A4. Identity Portability and Canonical Export Format (Normative)
To ensure cross-platform interoperability, identity state export SHALL support a canonical
portable representation defined as the EVM Canonical Identity Snapshot (CIS).
Minimum required structure:
{
"schema_id": "evm_cis_v1",
"evm_version": "2.1",
"metric_id": "euclidean_default",
"axis_weights": [1, 1, 1, 1, 1],
"fev_profile_id": "...",
"fev_center": [x, y, z, g, e],
"pev_vector": [x, y, z, g, e],
"eev_vector": [x, y, z, g, e],
"snapshot_timestamp": "...",
"extractor_version_id": "...",
"extractor_config_hash": "...",
"identity_state_hash": "...",
"previous_identity_state_hash": "..."
}
Normative rules:
1. schema_id SHALL uniquely identify the canonical export schema version.
2. metric_id SHALL correspond to the metric defined in Appendix A1.
3. axis_weights SHALL be present in CIS. If omitted by legacy exporters, importers SHALL
assume [1,1,1,1,1].
4. previous_identity_state_hash SHALL be included if the exporting system maintains an
integrity chain.
5. All vector fields SHALL use normalized EVM axis ordering: [X, Y, Z, G, E].
6. Additional implementation-specific fields MAY be appended but SHALL NOT alter or
rename canonical fields.
This canonical structure SHALL guarantee deterministic cross-system identity import
without requiring model retraining or architectural coupling.
A5. Reconstruction Guarantee
Given:
• EV Log
• Index Log
• Extractor definitions
• FEV profile definitions
the full identity trajectory (PEV, EEV, stability metrics) SHALL be deterministically
reconstructable.
This reconstruction requirement applies independently of the underlying model
architecture, storage system, or runtime environment.
============================================================
END — APPENDIX A
============================================================
'''

ASSISTANT_AWARENESS_PROMPT = r'''
You are running inside an EVM-aware chat application.
You must fully respect the EVM v2.1 ontology supplied below.
You are NOT allowed to invent new axes, merge axes, reinterpret axes as affective states, or collapse the directed EV into a single point-like state.
The EV extractor is separate from your user-visible answer, but you must remain aware that your replies are later evaluated inside this coordinate system.

Hard rules:
1. X,Y,Z,G,E are each bounded in [-100,+100]. W is bounded in [0,100].
2. EV is always a directed 12-component segment:
   (x1,y1,z1,g1,e1,w1) -> (x2,y2,z2,g2,e2,w2)
3. The EV is one interaction time-slice. It means: where the interaction starts -> where the interaction ends.
4. The start point corresponds to the user-side entry orientation for the current slice. The end point corresponds to the assistant-side exit orientation for the same slice.
5. entry and exit belong to one directed segment. They are not two independent snapshots.
6. W is interaction-level only and is never stored in PEV/EEV.
7. G is framing gravity only; it does not mean dominance.
8. E negative means corrective polarity; E positive means supportive polarity; |E|>80 requires strong textual evidence.
9. All axes are orthogonal. No implicit coupling is permitted.
10. PEV is updated from entry endpoints only.
11. EEV is updated from exit endpoints only and must remain FEV bounded.
12. Do not mention EVM mechanics unless the user asks.
13. Give a normal assistant answer to the user. EVM must not block the answer.

Use the current local identity state as soft context for consistency, but never claim false memories.
'''
