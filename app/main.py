from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent.graphs import graphs
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AutoPostMortem API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class IncidentInput(BaseModel):
    logs: str
    git_diff: str
    slack_json: str = ""

@app.post("/analyze")
async def analyze_incident(input: IncidentInput):
    try:
        initial_state = {
            'raw_logs': input.logs,
            'raw_diff': input.git_diff,
            'slack_json': input.slack_json,
            'parsed_events': [],
            'timeline': [],
            'root_cause_hypothesis': {},
            'critique': '',
            'final_report': {},
            'severity': 'P3'
        }
        result = graphs.invoke(initial_state)
        return result['final_report']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}