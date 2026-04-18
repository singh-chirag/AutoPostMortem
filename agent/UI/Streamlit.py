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
st.markdown("*Built with LangGraph + Groq + FastAPI + Streamlit | [GitHub](https://github.com/yourusername/autopostmortem)*")