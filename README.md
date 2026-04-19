           
# ⚙️ AutoPostMortem  
### AI-Powered Incident Analysis Agent

AutoPostMortem is an **AI-driven incident analysis system** that automatically generates **engineering post-mortems** from logs, git diffs, and Slack conversations.

It transforms raw debugging data into **structured, actionable reports** — saving hours of manual analysis.

---

## 🚀 Live Demo  
👉 (https://autopostmortem-3.onrender.com)

---

## 🧠 What It Does

### 🔹 Input
- Server logs  
- Git diffs  
- Optional Slack export  

### 🔹 Output
- 📌 Root Cause Analysis  
- 🕒 Incident Timeline  
- ⚠️ Severity Score (P0–P3)  
- ✅ Actionable Follow-up Tasks  
- 📄 Full Engineering Post-Mortem  

---

## 🏗️ Architecture

**LangGraph Multi-Agent Pipeline:**

### 🔹 Nodes Explained

- **Ingest Node**  
  Cleans and structures raw inputs (logs, diffs, Slack)

- **Timeline Node**  
  Reconstructs sequence of events

- **Analyze Node**  
  Identifies root cause and contributing factors

- **Self-Critique Node**  
  Challenges the hypothesis to reduce hallucinations

- **Report Node**  
  Generates final structured post-mortem

---

## 🧩 Tech Stack

- 🧠 **LangGraph** – Agent orchestration  
- 🤖 **Google Gemini (Flash Lite)** – LLM inference  
- ⚡ **FastAPI** – Backend API  
- 🎨 **Streamlit** – UI  
- ☁️ **Hugging Face Spaces** – Deployment  

---

## ⚙️ Key Design Decisions

- ✅ **Self-Critique Layer**
  - Validates root cause before final output  
  - Reduces hallucinations  

- ✅ **Single Responsibility Nodes**
  - Each agent does one job  
  - Clean, modular pipeline  

- ✅ **Deterministic Flow**
  - Graph-based execution (not chaotic agent loops)  

- ✅ **Zero-Cost Stack**
  - Fully open-source components  
  - No paid APIs required (optional Gemini usage)

---

