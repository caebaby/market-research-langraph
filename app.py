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
from Team_ICP.agents.psychological import Level5PsychologicalAgent

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
        agent = Level5PsychologicalAgent()
        
        # Create goal
        goal = {
            "description": "Extract deep psychological insights",
            "context": request.business_context,
            "type": "psychological_analysis"
        }
        
        # Run analysis
        result = await agent.pursue_goal(goal)
        
        # Extract the analysis
        analysis = ""
        if result["results"]:
            analysis = result["results"][0].get("analysis", "No analysis found")
        
        return {
            "analysis": analysis,
            "success_score": result["success_score"],
            "execution_time": result["execution_time"],
            "memory_patterns_used": result["metrics"]["tasks_completed"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
async def test():
    """Quick test endpoint"""
    return {"message": "Level 5 Agent is running!"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
