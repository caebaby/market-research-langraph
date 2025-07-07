from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os

# Import your graph
from agent.graph import graph

app = FastAPI(title="Market Research Intelligence")

class ResearchRequest(BaseModel):
    business_context: str
    research_type: str = "comprehensive"
    output_format: str = "full_json"

@app.get("/research")
async def research_form():
    """Simple test form for research"""
    return {
        "message": "Level 10 Hybrid Agent Ready",
        "endpoints": {
            "POST /research": "Run research with JSON payload",
            "GET /": "Health check"
        },
        "test_payload": {
            "business_context": "Your business context here",
            "research_type": "comprehensive", 
            "output_format": "psychology_report"
        }
    }

@app.post("/research")
async def run_research(request: ResearchRequest):
    """Run sophisticated market research"""
    try:
        # Run your LangGraph workflow
        result = await graph.ainvoke({
            "business_context": request.business_context,
            "research_type": request.research_type,
            "output_format": request.output_format
        })
        
        # Return based on format
        if request.output_format == "psychology_report":
            return {"report": result.get("psychology_report", "")}
        elif request.output_format == "campaign_ready":
            return {"insights": result.get("campaign_insights", "")}
        else:
            return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "service": "Market Research Intelligence",
        "status": "ready",
        "endpoints": ["/research"]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
