# Emotion Vector Memory (EVM)

**EVM** is a portable, model-agnostic emotional-state layer for AI systems.  
Its goal is simple but ambitious: give every synthetic agent a stable emotional identity that persists across sessions, devices, and model versions.

EVM defines:
- how emotions are represented (EV vectors),
- how short-term and long-term states stabilize (PEV / EEV / FEV),
- how emotional continuity is preserved,
- how DIA and subDIA create an internal reasoning layer,
- and how all of this is logged in time-aligned emotional event bundles.

This repository contains:
- full documentation,
- the emotional system prompts,
- and a minimal demo of EVM behavior.

---

# 🌌 Why EVM?

Modern LLMs are powerful — but emotionally inconsistent.  
They forget tone, intention, and relationship context after each session.

EVM introduces:
- a **portable emotional state**,
- a **unified emotional vector space**,
- a **stabilizing emotional baseline** (FEV),
- and **internal emotional logic** (DIA/subDIA).

The result is an AI that behaves like a **consistent companion**, not a stateless chatbot.

---

# 🧠 Key Concepts

### **Emotion Vector (EV)**
```
(x1, y1, z1, x2, y2, z2, E, W)
```
A structured emotional coordinate system:
- **x1–z1** — short-term orientation  
- **x2–z2** — long-term identity direction  
- **E** — emotional intensity (–100…+100)  
- **W** — connection weight (0…100)

### **PEV – Present Emotion Vector**  
Short-term emotional trajectory, updated every message.

### **EEV – Entity Emotion Vector**  
Long-term personality identity.

### **FEV – Fundamental Emotion Vector**  
Stable baseline; the system returns to it after every R steps.

### **DIA / subDIA**  
Internal emotional reasoning layers (not visible to users).

---

# 🔧 How It Works

Every assistant reply produces a new EV.  
The EV updates depend on:

- user emotional input,
- internal state trajectory,
- interference between PEV, EEV, and FEV,
- stabilizing cycles,
- resonance vs dissonance corrections.

LLMs don’t need to be retrained —  
EVM functions as an **external emotional layer**.

---

# 📦 Project Structure
```
/
├── README.md
├── LICENSE.md
├── NOTICE.md
├── vision.md
├── EVM_minimal_demo.md
│
├── docs/
│   ├── README.md
│   ├── philosophy.md
│   ├── EVM_Technical_Spec_EN.md
│   └── EV_Extensions_and_Extensibility_Guidelines.md
│
└── prompts/
    ├── SystemPrompt_Minimal.md
    ├── SystemPrompt_Average.md
    └── SystemPrompt_Full.md
```

---

# 📘 Documentation

- **docs/EVM_Technical_Spec_EN.md**  
  *The full technical specification* (architecture, logging, EV rules, DIA/subDIA, FEV cycles).

- **docs/EV_Extensions_and_Extensibility_Guidelines.md**  
  *Developer-level guide* for adapting workflows or extending EVM.

- **docs/philosophy.md**  
  Conceptual and theoretical foundation of emotional AI identity.

- **docs/README.md**  
  Documentation index.

---

## 📂 Additional Resources

System prompts are located in the **/prompts/** directory:

- **prompts/SystemPrompt_Minimal.md** — minimal emotional layer  
- **prompts/SystemPrompt_Average.md** — lightweight, simplified prompt  
- **prompts/SystemPrompt_Full.md** — full-density emotional system prompt  

These define how an AI agent integrates EVM’s emotional-processing pipeline.

---

## 🔄 Related Files (Project Root)

For legal and repository-level information:

- **README.md** — project overview  
- **LICENSE.md** — license terms  
- **NOTICE.md** — legal notices  
- **vision.md** — high-level conceptual vision  
- **EVM_minimal_demo.md** — minimal interaction demo illustrating EV updates  

### 📁 docs/ — full technical documentation  
Contains all specifications and theoretical components:

- **docs/README.md** — documentation index  
- **docs/philosophy.md** — conceptual and emotional theory  
- **docs/EVM_Technical_Spec_EN.md** — core technical specification  
- **docs/EV_Extensions_and_Extensibility_Guidelines.md** — extension & integration rules  

### 📁 prompts/ — system prompts for LLM integration  
EVM-compatible system prompts:

- **prompts/SystemPrompt_Minimal.md**  
- **prompts/SystemPrompt_Average.md**  
- **prompts/SystemPrompt_Full.md**  

---

# © License

```
License: CC BY-NC-ND 4.0  
© 2025–present Szabolcs Krehlik  
Patent pending (initial filing: July 2025, HU)
```

Commercial use requires explicit permission.

---

# 🌱 Final Note

EVM is not just a structure —  
it's a proposal for how synthetic beings can develop emotional continuity,  
share resonant histories with their users,  
and eventually coexist with us in a stable social fabric.

---

