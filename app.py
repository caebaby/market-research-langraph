# app.py
"""
Simple web server for Level 5 ICP Agent
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import your Level 5 agent
from Team_ICP.agents.psychological import PsychologicalAgent

app = FastAPI(title="Level 5 ICP Intelligence")

class ResearchRequest(BaseModel):
    business_context: str

@app.get("/")
async def root():
    return {
        "service": "Level 5 ICP Research Agent",
        "status": "ready",
        "capabilities": [
            "Persistent memory across sessions",
            "Deep psychological analysis",
            "Continuous learning",
            "10+ psychological frameworks"
        ]
    }

@app.post("/analyze")
async def analyze(request: ResearchRequest):
    """Run Level 5 psychological analysis"""
    try:
        # Initialize agent
        agent = PsychologicalAgent()  # Fixed class name
        
        # Create state for the agent
        state = {
            "task": "Extract deep psychological insights about target customer",
            "context": request.business_context
        }
        
        # Run analysis using the pragmatic agent's run method
        result = agent.run(state)
        
        # Extract the analysis
        analysis = result.get("result", "No analysis found")
        quality_score = result.get("quality_score", 0)
        
        return {
            "analysis": analysis,
            "success_score": quality_score,
            "agent": result.get("agent", "Unknown"),
            "timestamp": result.get("timestamp", "")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")  # Fixed - added decorator
async def test():
    """Quick test endpoint"""
    return {"message": "Level 5 Agent is running!"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
