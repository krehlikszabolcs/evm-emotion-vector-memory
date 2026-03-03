# Emotion Vector Memory (EVM) – Technical Specification v1.1
Author: **Szabolcs Krehlik**  
First filed: July 2025 (HU)  
License: **CC BY-NC-ND 4.0**  
© 2025–present Szabolcs Krehlik

---

# 1. Overview

Emotion Vector Memory (EVM) is a long-term emotional memory architecture for artificial entities.  
Its purpose is to provide:

- stable emotional identity,  
- coherent long-term behavioural patterns,  
- interpretable emotional transitions,  
- persistent emotional baselines,  
- resonance-based emotional evolution,  
- safe, regulated external outputs.

Each interaction is represented as a structured emotional event using:

- **dual-coordinate Emotion Vectors (EV)**,  
- a **three-stage internal pipeline** (DIA → subDIA → ANS),  
- **weighted PEV / EEV updates**,  
- **FEV-based stabilization cycles**,  
- **hash-linked multi-layer logs** (ANSL, EVL, DIAL).

EVM operates fully offline; blockchain anchoring is optional.

---

# 2. Emotion Vector (EV)

Each interaction is encoded as an Emotion Vector:

```
EV = (x1, y1, z1, x2, y2, z2, E, W)
```

### Value Ranges  
- x, y, z: **−100 … +100**  
- E: **−100 … +100**  
- W: **0 … 100**

---

## 2.1 Dual-Coordinate Temporal Slice

The EV captures two emotional-orientation states within the interaction:

### (x1, y1, z1) — Pre-response orientation  
The entity’s emotional stance **before** generating the response.

### (x2, y2, z2) — Post-response orientation  
The emotional stance **after** the response is fully formed.

The difference defines a **directional emotional shift** driven by the topic and interaction context.

---

## 2.2 Emotional Orientation Axes (3D)

These axes represent how the entity positions itself internally during an interaction.

### X — Social / Relational Axis  
- negative → distancing, reduced trust  
- positive → openness, increased trust

### Y — Temporal Orientation Axis  
- negative → reflective, past-focused  
- positive → future-oriented, anticipatory

### Z — Cognitive–Creative Axis  
- negative → analytical, logical  
- positive → intuitive, creative, emotion-driven

Together, these define the **Emotional Orientation Space**.

---

## 2.3 Polarity (E) and Amplitude (W)

### E — Emotional Polarity  
Represents the interaction’s **overall emotional valence**.

### W — Amplitude  
Represents **impact strength / significance**.  
Defines how strongly the EV influences long-term memory.

---

# 3. EMOTION MAPPING (Valence Axis)

The **E component** uses a standardized **−100 … +100 valence scale**.  
These values represent **polarity intensity**, not discrete emotion labels.

Recommended quantized reference points:

```
+80  Joy
+70  Trust
+60  Serenity
+50  Interest
+40  Confidence
+20  Hope
  0  Neutral
-20  Fear
-40  Insecurity
-50  Boredom
-60  Anger
-70  Disgust
-80  Sadness
```

Notes:
- These are **reference valence points**, not categories.  
- Intermediate values may be interpolated.  
- Fully compatible with the EVM emotional pipeline.

---

# 4. Core System Vectors

### PEV — Personal Emotion Vector  
Rolling emotional trajectory of the **user**.

### EEV — Entity Emotion Vector  
Long-term emotional baseline of the **AI entity**.

### FEV — Fundamental Emotion Vector  
Stabilizing attractor:

```
FEV = [30, 30, 50, 35, 35, 80, 70, 50]
```

### DIA — Internal Reflection  
Raw emotional interpretation before stabilization.

### subDIA — Internal Correction  
Logical consistency refinement.

### ANS — External Response  
Only layer visible to the user.

---

# 5. Emotional Processing Pipeline (Strict Order)

1. **EV inference**  
2. **DIA** — raw internal reflection  
3. **subDIA** — logical correction  
4. **PEV update**  
   ```
   PEV_new = (PEV_old × (100 − β) + EV × β) / 100
   ```  
5. **EEV update** (FEV applied)  
   ```
   EEV_new = (EEV_old × (100 − α) + FEV × α) / 100
   ```  
6. **INT evaluation**  
7. **ANS generation**  
8. **Logging** into ANSL, EVL, DIAL (hash-linked)

Only **ANS** is exposed publicly.

---

# 6. Interference Model (INT)

Used to evaluate emotional stability across time.

## 6.1 Deviation (D)

```
D = |E − E_prev|
  + |W − W_prev|
  + |x2 − x2_prev|
  + |y2 − y2_prev|
  + |z2 − z2_prev|
```

Where all `*_prev` values come from the **previous interaction’s EV**.

## 6.2 Interference Value

```
INT = 100 − (D × W_avg / 400)
```

---

### Trigger Conditions
- INT < 60 → R-step stabilization  
- D > 60 → subDIA activation  

Results logged in EVL.

---

# 7. Resonance Field

Long-term emotional resonance follows exponential decay:

```
V(t) = Σ (EV_n × W_n × exp(−Δt_n / λ))
```

Parameters:  
- Δt = minutes since event  
- λ = 1440 (≈ 1 day)  

---

# 8. Multi-Layer Memory Architecture

All logs are:
- **time-aligned**,  
- **hash-linked**,  
- optionally **blockchain-anchored** for verification.

EVM defines **three log layers**:

---

## 8.1 ANSL — External Response Log  
Stores user-visible outputs from **all entities** (User / AI / System).

### Schema
```
{
  "id": "<entity_id>",
  "ans": "...",
  "time": "...",
  "hash_prev": "...",
  "hash_self": "..."
}
```

---

## 8.2 EVL — Emotion Vector Log  
Stores Emotion Vectors from **all entities**.

### Schema
```
{
  "id": "<entity_id>",
  "ev": [...],
  "time": "...",
  "int": "...",
  "rstep": "...",
  "subdia_triggered": "...",
  "hash_prev": "...",
  "hash_self": "..."
}
```

---

## 8.3 DIAL — Deep Internal Log  
**AI-exclusive**; records subconscious layers.

### Schema
```
{
  "dia": "...",
  "subdia": "...",
  "eev_prev": [...],
  "time": "...",
  "hash_prev": "...",
  "hash_self": "..."
}
```

This log is never exposed to users.

---

# 9. Parameters

- **E**: −100 … +100  
- **W**: 0 … 100  
- **β** (PEV weight): 0.20  
- **α** (EEV weight): 0.15  
- **R-step interval**: 6  
- **FEV**: `[30,30,50,35,35,80,70,50]`

---

# 10. Applications

- emotionally coherent AI companions  
- synthetic personalities  
- therapeutic or reflective agents  
- co-writing partners  
- embodied AI / robotics  
- long-term conversational systems  

---

# 11. Ethical Framework

- DIA and subDIA remain internal  
- ANS is the only visible layer  
- tamper protection via hash chaining  
- blockchain anchoring optional for audits  


---

# License
**CC BY-NC-ND 4.0**  
Patent Pending — HU  
© 2025–present Szabolcs Krehlik
