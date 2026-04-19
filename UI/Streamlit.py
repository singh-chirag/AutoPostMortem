import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="🔍 AutoPostMortem", layout="wide", page_icon="🚨")

st.title("🚨 AutoPostMortem")
st.caption("AI-powered incident analysis agent — auto-generates post-mortems")

# Sample incident loader
def load_sample_incident():
    return {
        "logs": """2024-01-15T14:23:01 ERROR Connection timeout to database-primary
2024-01-15T14:23:05 ERROR Retry attempt 1 failed
2024-01-15T14:23:15 CRITICAL Database failover initiated
2024-01-15T14:24:00 INFO Failover complete, now using database-replica""",
        "git_diff": """+++ b/src/database/connection.py
@@ -45,7 +45,7 @@ class DBConnection:
-    timeout = 30
+    timeout = 5  # Reduced for faster failover
     retry_attempts = 3""",
        "slack_json": json.dumps({
            "messages": [
                {"ts": "1705329781.001", "user": "U123", "text": "🚨 Seeing DB connection errors in prod!"},
                {"ts": "1705329845.002", "user": "U456", "text": "Rolling back the timeout change now"}
            ]
        })
    }

if st.sidebar.button("📦 Load Sample Incident"):
    sample = load_sample_incident()
    st.session_state.logs = sample['logs']
    st.session_state.diff = sample['git_diff']
    st.session_state.slack = sample['slack_json']

col1, col2, col3 = st.columns(3)
with col1:
    logs = st.text_area("📋 Server Logs", 
                       value=st.session_state.get('logs', ''), 
                       height=250,
                       placeholder="Paste raw server logs...")
with col2:
    diff = st.text_area("🔀 Git Diff", 
                       value=st.session_state.get('diff', ''),
                       height=250,
                       placeholder="Paste git diff output...")
with col3:
    slack = st.text_area("💬 Slack Thread (JSON)", 
                        value=st.session_state.get('slack', ''),
                        height=250,
                        placeholder='Paste Slack export JSON...')

if st.button("🔍 Analyze Incident", type="primary", use_container_width=True):
    if not logs and not diff:
        st.error("Please provide at least logs or git diff")
    else:
        with st.spinner("🤖 Running 5-node agent pipeline..."):
            try:
                # For HF Spaces: call functions directly instead of HTTP
                if os.getenv("HF_SPACE"):
                    from agent.graphs import graphs
                    initial_state = {
                        'raw_logs': logs, 'raw_diff': diff, 'slack_json': slack,
                        'parsed_events': [], 'timeline': [], 'root_cause_hypothesis': {},
                        'critique': '', 'final_report': {}, 'severity': 'P3'
                    }
                    result = graphs.invoke(initial_state)
                    report = result['final_report']
                else:
                    resp = requests.post("http://localhost:8000/analyze", 
                                       json={"logs": logs, "git_diff": diff, "slack_json": slack},
                                       timeout=120)
                    resp.raise_for_status()
                    report = resp.json()
                
                # Display results
                st.success("✅ Analysis complete!")
                
                col_a, col_b = st.columns([1, 3])
                with col_a:
                    st.metric("🎯 Severity", report.get('severity', 'N/A'))
                    st.metric("🎲 Confidence", report.get('confidence', 'N/A'))
                
                with col_b:
                    st.subheader("🔍 Root Cause")
                    st.info(report.get('root_cause', 'Not identified'))
                
                st.subheader("📚 Evidence")
                for ev in report.get('evidence', []):
                    st.markdown(f"• `{ev}`")
                
                st.subheader("🤔 Self-Critique Summary")
                st.warning(report.get('critique_summary', 'No critique available'))
                
                st.subheader("📅 Timeline")
                st.json(report.get('timeline_summary', {}))
                
                st.subheader("✅ Actionable Follow-ups")
                for i, task in enumerate(report.get('tasks', []), 1):
                    st.markdown(f"{i}. {task}")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.code("Tip: Make sure GROQ_API_KEY is set and backend is running")

st.markdown("---")
st.markdown("*Built with LangGraph + Google + FastAPI + Streamlit | [GitHub](https://github.com/singh-chirag/autopostmortem)*")













# import streamlit as st
# import requests
# import json
# import os

# # ---------------- PAGE CONFIG ----------------
# st.set_page_config(
#     page_title="AutoPostMortem",
#     page_icon="🚨",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# # ---------------- CSS (reuse your 500-line style) ----------------
# # 👉 KEEP your previous CSS EXACTLY (don’t rewrite it)
# # paste same CSS block here from ResearchMind

# # ---------------- STEP CARD (REUSED COMPONENT) ----------------
# def step_card(num, title, state, desc=""):
#     status_map = {
#         "waiting": ("WAITING", "status-waiting"),
#         "running": ("● RUNNING", "status-running"),
#         "done": ("✓ DONE", "status-done"),
#     }
#     label, cls = status_map[state]
#     card_cls = {"running": "active", "done": "done"}.get(state, "")

#     st.markdown(f"""
#     <div class="step-card {card_cls}">
#         <div class="step-header">
#             <span class="step-num">{num}</span>
#             <span class="step-title">{title}</span>
#             <span class="step-status {cls}">{label}</span>
#         </div>
#         <div style="font-size:0.82rem;color:#706860;">{desc}</div>
#     </div>
#     """, unsafe_allow_html=True)

# # ---------------- SESSION STATE ----------------
# for key in ("results", "running", "done"):
#     if key not in st.session_state:
#         st.session_state[key] = {} if key == "results" else False

# # ---------------- HERO ----------------
# st.markdown("""
# <div class="hero">
#     <div class="hero-eyebrow">Incident Intelligence System</div>
#     <h1>Auto<span>PostMortem</span></h1>
#     <p class="hero-sub">
#         AI agents analyze logs, diffs, and Slack threads to generate
#         structured incident reports with root cause and action items.
#     </p>
# </div>
# <div class="divider"></div>
# """, unsafe_allow_html=True)

# # ---------------- LAYOUT ----------------
# col_input, col_space, col_pipeline = st.columns([5, 0.5, 4])

# with col_input:
#     st.markdown('<div class="input-card">', unsafe_allow_html=True)

#     logs = st.text_area("📋 Logs", height=200)
#     diff = st.text_area("🔀 Git Diff", height=200)
#     slack = st.text_area("💬 Slack JSON", height=200)

#     run_btn = st.button("⚡ Run Incident Analysis", use_container_width=True)

#     st.markdown('</div>', unsafe_allow_html=True)

# # ---------------- PIPELINE UI ----------------
# with col_pipeline:
#     st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)

#     r = st.session_state.results

#     def s(step):
#         steps = ["ingest", "timeline", "analyze", "critique", "report"]
#         if step in r:
#             return "done"
#         if st.session_state.running:
#             for k in steps:
#                 if k not in r:
#                     return "running" if k == step else "waiting"
#         return "waiting"

#     step_card("01", "Ingest", s("ingest"), "Parse logs & inputs")
#     step_card("02", "Timeline", s("timeline"), "Build event sequence")
#     step_card("03", "Analyze", s("analyze"), "Find root cause")
#     step_card("04", "Critique", s("critique"), "Validate reasoning")
#     step_card("05", "Report", s("report"), "Generate final output")

# # ---------------- RUN PIPELINE ----------------
# if run_btn:
#     st.session_state.results = {}
#     st.session_state.running = True
#     st.session_state.done = False
#     st.rerun()

# if st.session_state.running and not st.session_state.done:

#     results = {}

#     try:
#         if os.getenv("HF_SPACE"):
#             from agent.graphs import graphs

#             state = {
#                 'raw_logs': logs,
#                 'raw_diff': diff,
#                 'slack_json': slack,
#                 'parsed_events': [],
#                 'timeline': [],
#                 'root_cause_hypothesis': {},
#                 'critique': '',
#                 'final_report': {},
#                 'severity': 'P3'
#             }

#             result = graphs.invoke(state)

#             # simulate steps
#             results["ingest"] = "done"
#             results["timeline"] = "done"
#             results["analyze"] = "done"
#             results["critique"] = "done"
#             results["report"] = result["final_report"]

#         else:
#             resp = requests.post(
#                 "http://localhost:8000/analyze",
#                 json={"logs": logs, "git_diff": diff, "slack_json": slack}
#             )
#             data = resp.json()

#             results = {
#                 "ingest": "done",
#                 "timeline": "done",
#                 "analyze": "done",
#                 "critique": "done",
#                 "report": data
#             }

#         st.session_state.results = results
#         st.session_state.running = False
#         st.session_state.done = True
#         st.rerun()

#     except Exception as e:
#         st.error(str(e))
#         st.session_state.running = False

# # ---------------- RESULTS ----------------
# r = st.session_state.results

# if r and "report" in r:
#     report = r["report"]

#     st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

#     st.markdown(f"""
#     <div class="report-panel">
#         <div class="panel-label orange">Root Cause</div>
#         {report.get("root_cause")}
#     </div>
#     """, unsafe_allow_html=True)

#     st.markdown(f"""
#     <div class="feedback-panel">
#         <div class="panel-label green">Critique</div>
#         {report.get("critique_summary")}
#     </div>
#     """, unsafe_allow_html=True)