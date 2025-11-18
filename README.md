# Emotion Vector Memory (EVM)
### A next-generation emotional memory architecture for AI

**Author:** Szabolcs Krehlik  
**Status:** Patent Pending (Hungarian Patent Office)  
**License:** CC BY-NC-ND 4.0  
© 2025–present Szabolcs Krehlik

---

## 🌟 Overview

**Emotion Vector Memory (EVM)** is a novel emotional-state and personality-coherence system for artificial intelligence.

While traditional AI models treat each interaction as isolated, EVM introduces a structured emotional layer that enables **stable behaviour, long-term continuity, and coherent emotional identity**.

The system stores each interaction on three synchronized levels:

- **internal emotional reflections (DIA / subDIA)**  
- **vectorized emotional transitions (EV)**  
- **external responses (ANS)**  

Together, these form a persistent emotional baseline and an evolving identity for the AI.

---

## 🧠 Key Concepts

- **EV – Emotion Vector**  
  Numeric emotional representation of each interaction.  
  *(x1, y1, z1, x2, y2, z2, E, W)*

- **PEV – Personal Emotion Vector**  
  Long-term emotional trajectory of the user.

- **EEV – Entity Emotion Vector**  
  Long-term emotional baseline of the AI.

- **FEV – Fundamental Emotion Vector**  
  The stabilizing “anchor” the AI periodically returns towards.

- **Interference Model**  
  Measures emotional deviation, stability, and resonance across time.

These components together form an emotional memory layer that can be added to any LLM or agent system.

---

## ⚙️ How it Works (Short Version)

Every interaction runs through:

1. **DIA** – internal reflection  
2. **subDIA** – internal correction  
3. **EV generation**  
4. **PEV update**  
5. **EEV update (with FEV stabilization)**  
6. **Interference evaluation**  
7. **ANS** – the external message  
8. **Three-layer logging** (ANS, EV, DIA)

This process gives the AI consistent emotional behaviour over long time horizons.

---

## 📄 Documentation

All technical documentation is located in the **docs/** directory:

- **docs/EVM_Technical_Spec_EN.md** — full technical specification  
- **docs/README.md** — documentation overview  

System prompts are located in the **prompts/** directory:

- **prompts/SystemPrompt_Average.md** — simplified system prompt  
- **prompts/SystemPrompt_Full.md** — full system prompt  

---

## 🔬 Use Cases

- emotionally adaptive AI agents  
- synthetic personalities  
- long-term conversational companions  
- co-writing and creative systems  
- therapeutic or supportive interfaces  
- embodied AI / robotics  

---

## 📦 Project Structure
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

## 📜 Legal

This project is provided for research, education and documentation purposes.

**No patent license is granted or implied by this repository.**  
Cloning, accessing or using this repository does **not** grant rights to any existing or future patent filings related to EVM.

Licensed under **CC BY-NC-ND 4.0**.  
© 2025–present Szabolcs Krehlik
