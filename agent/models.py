from typing import TypedDict, List, Optional

class IncidentState(TypedDict):
    raw_logs: str
    raw_diff: str
    slack_json: str
    parsed_events: List[dict]
    timeline: List[dict]
    root_cause_hypothesis: dict
    critique: str
    final_report: dict
    severity: str  # P0/P1/P2/P3