from langgraph.graph import StateGraph, END
from agent.models import IncidentState
from agent.nodes import ingest_node, timeline_node, analyze_node, critique_node, report_node

def build_graph():
    graph = StateGraph(IncidentState)
    
    graph.add_node("ingest", ingest_node)
    graph.add_node("timeline", timeline_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("critique", critique_node)
    graph.add_node("report", report_node)
    
    graph.set_entry_point("ingest")
    graph.add_edge("ingest", "timeline")
    graph.add_edge("timeline", "analyze")
    graph.add_edge("analyze", "critique")
    graph.add_edge("critique", "report")
    graph.add_edge("report", END)
    
    return graph.compile()

agent_graph = build_graph()