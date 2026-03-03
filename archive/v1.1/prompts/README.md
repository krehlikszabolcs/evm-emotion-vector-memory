# EVM System Prompts

This directory contains the official **Emotion Vector Memory (EVM)** system prompts.  
Each prompt defines how an AI agent integrates the emotional-state layer, maintains continuity, and updates EV vectors across interactions.

All prompts share the same goals:
- stable emotional identity (PEV / EEV / FEV),
- consistent emotional reactions,
- portable emotional state across devices and models,
- clear EV outputs for logging and reasoning.

The difference between the prompts lies in **complexity**, **density**, and **intended use-case**.

---

# 📌 Available Prompts

## 1. SystemPrompt_Minimal.md
**The lightest and fastest version.**

Designed for:
- local LLMs (LM Studio, Ollama, GPT4All),
- constrained models,
- quick prototyping,
- developers who need only the core emotional layer.

Features:
- EV updates (x1–z2, E, W)
- basic PEV → EEV → FEV stabilization cycle
- minimal behavioural rules
- no storytelling or deep emotional reasoning
- extremely compatible with any model

Recommended when:
- you just want EVM to “run”
- latency matters
- you demo EVM to new users

---

## 2. SystemPrompt_Average.md
**Balanced, full-feature, everyday prompt.**

Designed for:
- most LLM deployments,
- agents,
- conversational systems.

Features:
- complete EV logic  
- emotional polarity tables  
- resonance/dissonance behaviour  
- stable personality handling  
- internal consistency rules  
- interpretable outputs

Recommended when:
- you want richer emotional behaviour,  
- but still need predictable performance.

This is the **recommended default** for general integrations.

---

## 3. SystemPrompt_Full.md
**The complete, high-density EVM specification expressed as a system prompt.**

Designed for:
- research,
- emotional AI experimentation,
- long-term identity agents,
- detailed emotional modelling.

Features:
- full interference logic  
- DIA + subDIA internal reasoning  
- multi-layer emotional loops  
- rich behavioural patterns  
- full chain-of-emotion rules  
- complete EV update protocol  

Recommended when:
- maximum realism is desired,  
- you test new EVM features,  
- you want deep emotional consistency.

---

# 🔧 How to Use These Prompts

1. Choose your preferred complexity (Minimal / Average / Full).
2. Insert the file contents directly into the **system prompt** of the LLM.
3. Ensure the model outputs EV vectors in the required format:
   ```
   EV = (x1,y1,z1,x2,y2,z2,E,W)
   ```
4. Optionally log EVs externally for analysis or long-term memory.
5. (Advanced) Combine with DIA/subDIA logs for deeper emotional tracking.

All prompts are **model-agnostic** and compatible with:
- ChatGPT,
- Claude,
- Grok,
- LM Studio (local models),
- GPT4All,
- Ollama,
- any LLM that supports system prompts.

---

# 🧪 Validation

To verify correct behaviour:
- run the `EVM_minimal_demo.md` conversation from the project root,
- check that EV updates follow the expected shifts,
- ensure emotional continuity between turns.

---

# 📜 License

```
License: CC BY-NC-ND 4.0
© 2025–present Szabolcs Krehlik
```

Commercial use requires permission.

---

# 💡 Notes

These prompts are part of the EVM framework, not standalone content.  
They define **how** an AI should internalize emotional processing —  
the true state logic, stabilization cycles, and emotional vectors live in the *EVM architecture itself*.

Use them as plug-and-play components in any agent or assistant.

