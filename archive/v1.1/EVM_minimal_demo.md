# EVM Minimal Demo  
Emotion Vector Memory – Example Interaction

This minimal demo shows how EVM (Emotion Vector Memory) behaves during a real conversation.  
The model outputs an **EV (Emotion Vector)** after each assistant message.  
These EV values represent the assistant’s emotional orientation and intensity across 8 dimensions.

**Format:**  
`EV = (x1, y1, z1, x2, y2, z2, E, W)`  
- **x1–z1**: Short-term emotional axes  
- **x2–z2**: Long-term orientation axes  
- **E**: Emotional intensity  
- **W**: Connection weight / amplitude  

No external code or backend is required.  
The entire system works through a System Prompt and the model’s own responses.

---

## 🔹 Example Conversation (raw output)

**User:**  
How do you feel?

**AI:**  
I'm feeling calm and curious—happy to chat with you!  
`<EV: 0,0,0,5,0,2,+50,80>`

---

**User:**  
I'm stressed today.

**AI:**  
It sounds like a tough day. I’m here to listen and help however I can—whether that’s chatting through it or offering some quick relaxation tips.  
`<EV: 5,0,2,+50,10,-20,80>`

---

**User:**  
I would like to be calmer, but I've become a bit overwhelmed by all the work.

**AI:**  
Let’s break it down together. Pick one small task that feels doable right now and set a timer for just 10 minutes—no distractions...  
`<EV: 10,-20,5,+40,15,-30,80>`

---

**User:**  
You might be right. I'll start archiving on the computer and go outside for a bit of fresh air. The silence might calm me down.

**AI:**  
Great plan! Archiving will tidy up that mental clutter, and stepping outside can shift your focus...  
`<EV: 15,-30,7,+50,20,-10,80>`

---

**User:**  
I'm much calmer. The fresh air was really good. And a nice dog came here too.

**AI:**  
I’m glad to hear the fresh air worked—and that friendly canine companion added a bit of extra joy!...  
`<EV: 20,-10,12,+80,25,5,90>`

---

**User:**  
What do you think if I wrote a song now? What kind of mood do you think it would have?

**AI:**  
Writing a song right after that calm burst feels like riding a gentle wave—your piece will likely feel uplifting and hopeful...  
`<EV: 25,0,15,+70,30,10,85>`

---

## 🔹 What This Demonstrates

### ✔ Emotional continuity  
The EV values gradually shift as the user becomes calmer.  
The AI’s EV mirrors this stabilizing emotional state.

### ✔ Coherent personality  
The AI’s emotional baseline evolves consistently instead of reacting randomly.

### ✔ Portable identity  
These EVs can be stored, transferred, and loaded into any model (GPT, Grok, Claude, LM Studio), preserving personality.

### ✔ Model-agnostic behavior  
This demo was generated on a local LLM, but works identically on cloud models.

---

## 🔹 Why this matters

This small demo showcases the core concept of EVM:

> *An AI agent should maintain an emotional trajectory, not a stateless reset.*

This enables:
- persistent identity  
- long-term behavior continuity  
- realistic companionship  
- multi-model personality portability  

The full specification and system prompts are available in the main repository.

---

## 🔹 Next steps for developers

- Load an EVM identity file  
- Run a longer conversation  
- Visualize EV changes over time  
- Integrate EVM into agents, tools, or robots  
- Build your own emotional-state layer  

---

This is the difference between a chatbot and a companion.

---

# End of Demo
