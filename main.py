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

@app.get("/test")
async def test_page():
    """Direct test page for Level 10 agent"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Level 10 Agent Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            textarea { width: 100%; height: 300px; margin: 10px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; font-family: Arial, font-size: 14px; }
            button { padding: 15px 30px; background: #007cba; color: white; border: none; cursor: pointer; border-radius: 5px; font-size: 16px; margin: 10px 0; }
            button:hover { background: #005a85; }
            #result { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 5px; white-space: pre-wrap; max-height: 600px; overflow-y: auto; font-size: 12px; }
            .loading { color: #007cba; font-weight: bold; }
            .success { color: #28a745; }
            .error { color: #dc3545; font-weight: bold; }
            .metrics { background: #e9ecef; padding: 15px; border-radius: 5px; margin: 10px 0; font-weight: bold; }
            .quick-tests { margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Level 10 Hybrid Agent Test</h1>
            <p>Test your hybrid agent with different business contexts to verify quality and isolation</p>
            
            <div class="quick-tests">
                <h4>Test Instructions:</h4>
                <p>Enter your business context below and click "Run Level 10 Analysis" to test the agent quality and session isolation.</p>
            </div>
            
            <h3>Business Context:</h3>
            <textarea id="context" placeholder="Enter your comprehensive business context here...

Include:
- Business type and target market
- Main customer pain points
- Voice of customer quotes
- Current solution gaps
- Customer demographics and psychographics"></textarea>
            
            <button onclick="runTest()">🧪 Run Level 10 Analysis</button>
            
            <div id="result"></div>
        </div>
        
        <script>
        async function runTest() {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '⏳ Running Level 10 Agent Analysis... (30-60 seconds)\\n\\nProcessing comprehensive ICP research with Eugene Schwartz frameworks...';
            resultDiv.className = 'loading';
            
            const startTime = Date.now();
            
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
                const endTime = Date.now();
                const duration = ((endTime - startTime) / 1000).toFixed(1);
                
                resultDiv.className = 'success';
                
                // Extract key metrics if available
                let metricsHtml = '';
                if (data.quality_score !== undefined) {
                    metricsHtml = `
                    <div class="metrics">
                        📊 Quality Score: ${(data.quality_score * 100).toFixed(1)}%
                        🎯 Confidence: ${(data.confidence_score * 100).toFixed(1)}%
                        ⏱️ Processing Time: ${duration}s
                        🧠 Memory Patterns: ${data.memory_context?.successful_patterns?.length || 0}
                        📝 Session ID: ${data.session_id || 'N/A'}
                    </div>`;
                }
                
                resultDiv.innerHTML = `✅ Level 10 Agent Analysis Completed!
                
${metricsHtml}

🔍 Full Results:
${JSON.stringify(data, null, 2)}`;
                
            } catch (error) {
                const endTime = Date.now();
                const duration = ((endTime - startTime) / 1000).toFixed(1);
                
                resultDiv.className = 'error';
                resultDiv.innerHTML = `❌ Error after ${duration}s: ${error.message}
                
💡 This might be a timeout issue. Check the Railway logs - your agent may have completed processing successfully.
                
🔍 Common causes:
- Long processing time (normal for comprehensive analysis)
- Network timeout (results may still be generated)
- Memory/resource limits

Try a shorter business context or check Railway logs for actual completion.`;
            }
        }
        </script>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
