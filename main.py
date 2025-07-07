from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import HTMLResponse
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

@app.get("/test")
async def test_page():
    """Direct test page for Level 10 agent"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Level 10 Agent Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            textarea { width: 100%; height: 200px; margin: 10px 0; }
            button { padding: 10px 20px; background: #007cba; color: white; border: none; cursor: pointer; border-radius: 5px; }
            #result { margin-top: 20px; padding: 20px; background: #f5f5f5; border-radius: 5px; white-space: pre-wrap; }
            .loading { color: #007cba; }
        </style>
    </head>
    <body>
        <h1>🚀 Level 10 Hybrid Agent Test</h1>
        <p>Direct test interface for your Level 10 ICP Intelligence Agent</p>
        
        <h3>Business Context:</h3>
        <textarea id="context">Axiom Planning Resources provides comprehensive back-office support for independent financial advisors. Target customers are mid-career advisors (5-10 years) stuck in commission models seeking recurring revenue stability. Customer complaints: "I'm trapped by a broken system - I'm on a hamster wheel and can't get off"</textarea>
        
        <br>
        <button onclick="runTest()">🧪 Test Level 10 Agent</button>
        
        <div id="result"></div>
        
        <script>
        async function runTest() {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '⏳ Running Level 10 Agent... (this may take 30-60 seconds)';
            resultDiv.className = 'loading';
            
            try {
                const response = await fetch('/research', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        business_context: document.getElementById('context').value,
                        research_type: 'comprehensive',
                        output_format: 'psychology_report'
                    })
                });
                
                const data = await response.json();
                resultDiv.className = '';
                resultDiv.innerHTML = '✅ Level 10 Agent Results:\\n\\n' + JSON.stringify(data, null, 2);
            } catch (error) {
                resultDiv.className = '';
                resultDiv.innerHTML = '❌ Error: ' + error.message;
            }
        }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
