           
# AutoPostMortem > 
AI-powered incident analysis agent that auto-generates > 
engineering post-mortems from logs, git diffs & Slack threads. 
## Live Demo [Try it on Hugging Face Spaces](https://huggingface.co/...) 
## What it does Input: server logs + git diff + optional Slack export Output:
full post-mortem with root cause, timeline, severity score (P0–P3), and follow-up tasks
## Architecture 5-node LangGraph agent: Ingest → Timeline → Analyze → Self-Critique → Report ## Tech Stack - LangGraph (agentic orchestration) - Google API / gemini-flash-lite (LLM inference) - FastAPI + Streamlit - Deployed on Hugging Face Spaces 
## Key design decisions - Self-critique node challenges the root cause hypothesis before the final report is written - Each node has a single responsibility (clean state machine) - All open-source, zero cost to run 
## Run locally git clone ... && pip install -r requirements.txt GOOGLE_API_KEY=your_key streamlit run ui/streamlit_app.py
