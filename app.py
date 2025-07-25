from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime
from supabase import create_client, Client
from typing import List, Optional
print("APP.PY LOADED - NEW VERSION")

load_dotenv()

try:
    from team_icp.workflows.graph import graph
    GRAPH_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import graph: {e}")
    GRAPH_AVAILABLE = False

print(f"=== GRAPH AVAILABLE: {GRAPH_AVAILABLE} ===")

app = FastAPI(title="Level 5 ICP Intelligence")

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

class ResearchRequest(BaseModel):
    business_context: str
    agents: List[str]
    team: str
    industry: Optional[str] = None
    report_name: Optional[str] = None

@app.get("/")
async def root():
    return {
        "service": "Level 5 ICP Research Agent",
        "status": "ready",
        "graph_available": GRAPH_AVAILABLE,
        "capabilities": [
            "Persistent memory across sessions",
            "Deep psychological analysis",
            "Continuous learning",
            "10+ psychological frameworks",
            "Multi-agent orchestration"
        ]
    }

@app.get("/test")
async def test():
    return {
        "message": "Level 5 Agent is running!",
        "graph_available": GRAPH_AVAILABLE,
        "supabase_connected": supabase is not None
    }

# Dashboard HTML (same as before)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    return """[your full HTML code here - copy from your current app.py]"""

# Dashboard JS (same as before)
@app.get("/dashboard.js")
async def dashboard_js():
    return Response(content="""[your full JS code here - copy from your current app.py]""", media_type="application/javascript")

@app.post("/analyze")
async def analyze(request: Request):
    try:
        data = await request.json()
        business_context = data.get("business_context")
        agents = data.get("agents", [])
        team = data.get("team")
        industry = data.get("industry")
        report_name = data.get("report_name")
        
        if not business_context:
            raise HTTPException(status_code=400, detail="business_context is required")
        if not agents:
            raise HTTPException(status_code=400, detail="At least one agent must be selected")
        
        results = {}
        overall_score = 0.0
        shared_insights = {}
        
        if not GRAPH_AVAILABLE:
            print("Warning: Running in mock mode - graph not available")
            for agent in agents:
                results[agent] = f"Mock {agent} analysis for: {business_context[:100]}... (Graph system not available - this is test data)"
                overall_score = 0.75
        else:
            try:
                from core.memory import HybridMemory
                memory_service = HybridMemory()
            except ImportError:
                memory_service = None
                print("Warning: Memory service not available")

            try:
                from core.tools import ToolBox
                tool_executor = ToolBox()
                print("Tool executor initialized successfully")
            except ImportError as e:
                tool_executor = None
                print(f"Warning: Tool services not available: {e}")
            
            client_id = f"{team}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            state = {
                "task": f"ICP analysis",
                "context": business_context,
                "new_data": True,
                "team": team,
                "master_context": business_context,
                "business_context": business_context,
                "client_id": client_id,
                "shared_insights": shared_insights,
                "memory_service": memory_service,
                "tool_executor": tool_executor,
                "requested_agents": agents,  # Added here for dynamic routing
            }
            
            result = await graph.ainvoke(state)
            
            results = result.get("result", {})
            overall_score = result.get("quality_score", 0.75)
        
        if supabase:
            try:
                supabase.table("reports").insert({
                    "report_name": report_name or f"Report_{datetime.now().strftime('%Y%m%d')}",
                    "team": team,
                    "industry": industry,
                    "context": business_context,
                    "agents": agents,
                    "results": results,
                    "success_score": overall_score,
                    "timestamp": datetime.now().isoformat()
                }).execute()
            except Exception as db_error:
                print(f"Database storage failed: {db_error}")
        
        return {
            "analysis": results,
            "success_score": overall_score,
            "agent": f"{team} Platform",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "graph_available": GRAPH_AVAILABLE,
        "supabase_connected": supabase is not None,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
