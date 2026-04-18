from langchain_google_genai import ChatGoogleGenerativeAI as ChatGroq
from langchain_core.messages import HumanMessage
from agent.prompt import ANALYZE_PROMPT, CRITIQUE_PROMPT
from agent.models import IncidentState
import json, os, re
from datetime import datetime

llm = ChatGroq(model=os.getenv('MODEL_NAME', 'llama3-70b-8192'), temperature=0.1)

def ingest_node(state: IncidentState) -> IncidentState:
    """Parse and normalize all input sources into unified format"""
    parsed = []
    
    # Parse logs - extract timestamps & errors
    for line in state['raw_logs'].split('\n'):
        if 'ERROR' in line or 'Exception' in line:
            match = re.match(r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})', line)
            parsed.append({
                'timestamp': match.group(1) if match else datetime.now().isoformat(),
                'source': 'logs',
                'content': line.strip(),
                'type': 'error' if 'ERROR' in line else 'info'
            })
    
    # Parse git diff - extract changed files
    if state['raw_diff']:
        files = re.findall(r'^\+\+\+ b/(.+)$', state['raw_diff'], re.MULTILINE)
        for f in files:
            parsed.append({
                'timestamp': datetime.now().isoformat(),
                'source': 'git',
                'content': f'File modified: {f}',
                'type': 'code_change',
                'file': f
            })
    
    # Parse Slack JSON if provided
    if state['slack_json']:
        try:
            slack_data = json.loads(state['slack_json'])
            for msg in slack_data.get('messages', []):
                parsed.append({
                    'timestamp': msg.get('ts', ''),
                    'source': 'slack',
                    'content': msg.get('text', ''),
                    'user': msg.get('user', 'unknown'),
                    'type': 'communication'
                })
        except:
            pass
    
    return {**state, 'parsed_events': parsed}

def timeline_node(state: IncidentState) -> IncidentState:
    """Sort events chronologically with source attribution"""
    events = state['parsed_events']
    # Simple sort by timestamp string (improve with proper parsing in production)
    sorted_events = sorted(events, key=lambda x: x.get('timestamp', ''))
    return {**state, 'timeline': sorted_events}

def analyze_node(state: IncidentState) -> IncidentState:
    """Generate root cause hypothesis with evidence"""
    prompt = ANALYZE_PROMPT.format(
        timeline=json.dumps(state['timeline'][:20], indent=2)  # Limit context
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    
    try:
        result = json.loads(response.content)
    except:
        result = {
            "root_cause": "Analysis failed to parse",
            "evidence": [],
            "confidence": "LOW",
            "blast_radius": "Unknown"
        }
    
    return {**state, 'root_cause_hypothesis': result}

def critique_node(state: IncidentState) -> IncidentState:
    """Self-critique: challenge the hypothesis"""
    hyp = state['root_cause_hypothesis']
    prompt = CRITIQUE_PROMPT.format(
        root_cause=hyp.get('root_cause', ''),
        evidence=hyp.get('evidence', [])
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    return {**state, 'critique': response.content}

def report_node(state: IncidentState) -> IncidentState:
    """Assemble final structured post-mortem report"""
    hyp = state['root_cause_hypothesis']
    
    # Simple severity logic based on keywords
    severity = 'P3'
    content = str(state['timeline']) + str(hyp.get('blast_radius', ''))
    if any(kw in content.lower() for kw in ['outage', 'down', 'critical', 'p0']):
        severity = 'P0'
    elif any(kw in content.lower() for kw in ['error', 'failure', 'broken']):
        severity = 'P1'
    elif 'warning' in content.lower():
        severity = 'P2'
    
    final_report = {
        'root_cause': hyp.get('root_cause'),
        'evidence': hyp.get('evidence', []),
        'confidence': hyp.get('confidence'),
        'critique_summary': state['critique'][:500] + '...',
        'timeline_summary': f"{len(state['timeline'])} events processed",
        'severity': severity,
        'tasks': [
            f"Review and fix: {hyp.get('root_cause', 'identified issue')}",
            "Add monitoring alert for similar patterns",
            "Update runbook with resolution steps"
        ]
    }
    
    return {**state, 'final_report': final_report, 'severity': severity}