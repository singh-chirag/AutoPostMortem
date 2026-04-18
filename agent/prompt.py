ANALYZE_PROMPT = """You are a senior SRE analyzing a production incident.

TIMELINE OF EVENTS: {timeline}

Your task:
1. Identify the most likely root cause
2. List supporting evidence (with source: logs/diff/slack)
3. Estimate confidence: HIGH/MEDIUM/LOW
4. Describe the blast radius (what was affected)

Respond ONLY as JSON:
{{
  "root_cause": "...",
  "evidence": ["..."],
  "confidence": "HIGH",
  "blast_radius": "..."
}}"""

CRITIQUE_PROMPT = """A previous analysis concluded:
ROOT CAUSE: {root_cause}
EVIDENCE: {evidence}

Your job: Act as a skeptical senior engineer.
- What alternative explanations exist?
- What evidence is missing or ambiguous?
- Could this be a symptom, not the root cause?
- What would you need to be MORE confident?

Be honest. If the analysis is solid, say so briefly."""