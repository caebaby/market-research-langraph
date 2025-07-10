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

@app.get("/dashboard")
async def client_dashboard():
    """Professional client dashboard for report generation"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Market Intelligence Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f8fafc;
                color: #1e293b;
                line-height: 1.6;
            }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 0;
                text-align: center;
                border-radius: 12px;
                margin-bottom: 30px;
            }
            .header h1 { font-size: 2.5rem; margin-bottom: 10px; font-weight: 700; }
            .header p { font-size: 1.1rem; opacity: 0.9; }
            .form-section { 
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            .form-section h2 { 
                color: #334155;
                margin-bottom: 20px;
                font-size: 1.5rem;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .form-group { margin-bottom: 25px; }
            .form-group label { 
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #475569;
            }
            textarea { 
                width: 100%;
                padding: 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                font-family: inherit;
                resize: vertical;
                min-height: 250px;
                transition: border-color 0.2s;
            }
            textarea:focus { 
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            .action-buttons { 
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
            }
            .btn { 
                padding: 15px 30px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }
            .btn-primary { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .btn-primary:hover { 
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            }
            .btn-secondary { 
                background: #f1f5f9;
                color: #475569;
                border: 2px solid #e2e8f0;
            }
            .btn-secondary:hover { 
                background: #e2e8f0;
                transform: translateY(-1px);
            }
            .result-section { 
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
                overflow: hidden;
                margin-top: 30px;
                display: none;
            }
            .result-header { 
                background: #1e293b;
                color: white;
                padding: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .result-content { 
                padding: 30px;
                max-height: 600px;
                overflow-y: auto;
            }
            .loading { 
                text-align: center;
                padding: 40px;
                color: #667eea;
            }
            .loading-spinner { 
                border: 4px solid #f3f4f6;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            .progress-bar { 
                width: 100%;
                height: 6px;
                background: #f1f5f9;
                border-radius: 3px;
                overflow: hidden;
                margin: 20px 0;
            }
            .progress-fill { 
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2);
                border-radius: 3px;
                transition: width 0.3s ease;
            }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            .status-indicator { 
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .status-ready { background: #dcfce7; color: #166534; }
            .status-processing { background: #fef3c7; color: #92400e; }
            .status-complete { background: #dbeafe; color: #1e40af; }
            .features-grid { 
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .feature-card { 
                background: white;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                border: 1px solid #e2e8f0;
            }
            .feature-card h3 { 
                color: #334155;
                margin-bottom: 15px;
                font-size: 1.2rem;
            }
            .feature-card ul { 
                list-style: none;
                padding: 0;
            }
            .feature-card li { 
                padding: 5px 0;
                color: #64748b;
                position: relative;
                padding-left: 20px;
            }
            .feature-card li::before { 
                content: "✓";
                position: absolute;
                left: 0;
                color: #10b981;
                font-weight: bold;
            }
            .download-btn { 
                background: #10b981;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                text-decoration: none;
                font-size: 14px;
                font-weight: 600;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }
            .download-btn:hover { 
                background: #059669;
                transform: translateY(-1px);
            }
            @media (max-width: 768px) {
                .container { padding: 15px; }
                .header { padding: 30px 20px; }
                .header h1 { font-size: 2rem; }
                .form-section { padding: 25px; }
                .action-buttons { flex-direction: column; }
                .btn { width: 100%; justify-content: center; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 Market Intelligence Dashboard</h1>
                <p>5-Agent Psychology + Conversion Intelligence System</p>
                <span class="status-indicator status-ready">System Ready</span>
            </div>

            <div class="form-section">
                <h2>🎯 Business Intelligence Analysis</h2>
                <div class="form-group">
                    <label for="businessContext">Business Context & Background</label>
                    <textarea id="businessContext" placeholder="Describe your business, target market, current challenges, and what you're trying to achieve...

Include:
• Business type and industry
• Target customer demographics
• Current marketing challenges
• Revenue goals and growth objectives
• Any specific pain points or opportunities you're aware of
• Competitive landscape insights
• Customer feedback or voice of customer data"></textarea>
                </div>
                
                <div class="action-buttons">
                    <button class="btn btn-primary" onclick="generateReport()">
                        🚀 Generate Intelligence Report
                    </button>
                    <button class="btn btn-secondary" onclick="clearForm()">
                        🔄 Clear Form
                    </button>
                </div>
            </div>

            <div class="features-grid">
                <div class="feature-card">
                    <h3>🧠 Deep Psychology Analysis</h3>
                    <ul>
                        <li>Identity & contradiction patterns</li>
                        <li>Unconscious belief systems</li>
                        <li>Jungian archetype analysis</li>
                        <li>Voice of customer extraction</li>
                    </ul>
                </div>
                <div class="feature-card">
                    <h3>🎯 Conversion Intelligence</h3>
                    <ul>
                        <li>Ad testing hypotheses</li>
                        <li>Psychological triggers</li>
                        <li>Offer positioning strategy</li>
                        <li>Campaign optimization</li>
                    </ul>
                </div>
                <div class="feature-card">
                    <h3>🎭 Interview Simulations</h3>
                    <ul>
                        <li>Psychological depth interviews</li>
                        <li>Sales intelligence extraction</li>
                        <li>Authentic conversation patterns</li>
                        <li>Objection & desire mapping</li>
                    </ul>
                </div>
                <div class="feature-card">
                    <h3>🚀 Campaign Synthesis</h3>
                    <ul>
                        <li>Complete implementation strategy</li>
                        <li>Multi-channel campaign design</li>
                        <li>Conversion optimization framework</li>
                        <li>Performance tracking metrics</li>
                    </ul>
                </div>
            </div>

            <div id="resultSection" class="result-section">
                <div class="result-header">
                    <h3>📊 Intelligence Report</h3>
                    <div>
                        <span id="statusIndicator" class="status-indicator status-processing">Processing</span>
                        <button class="download-btn" onclick="downloadReport()" style="margin-left: 15px;">
                            📥 Download Report
                        </button>
                    </div>
                </div>
                <div id="resultContent" class="result-content">
                    <div class="loading" id="loadingState">
                        <div class="loading-spinner"></div>
                        <div>Generating comprehensive intelligence report...</div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="progressFill"></div>
                        </div>
                        <div id="progressText">Initializing 5-agent system...</div>
                    </div>
                </div>
            </div>
        </div>

        <script>
        let currentReport = null;
        let progressInterval = null;

        async function generateReport() {
            const businessContext = document.getElementById('businessContext').value.trim();
            
            if (!businessContext) {
                alert('Please enter your business context before generating the report.');
                return;
            }

            // Show result section and start loading
            document.getElementById('resultSection').style.display = 'block';
            document.getElementById('loadingState').style.display = 'block';
            document.getElementById('statusIndicator').textContent = 'Processing';
            document.getElementById('statusIndicator').className = 'status-indicator status-processing';
            
            // Start progress animation
            startProgressAnimation();
            
            const startTime = Date.now();
            
            try {
                const response = await fetch('/research', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        business_context: businessContext,
                        research_type: 'comprehensive',
                        output_format: 'psychology_report'
                    })
                });
                
                const data = await response.json();
                const endTime = Date.now();
                const duration = ((endTime - startTime) / 1000).toFixed(1);
                
                // Stop progress animation
                stopProgressAnimation();
                
                // Display results
                displayResults(data, duration);
                
            } catch (error) {
                console.error('Error:', error);
                stopProgressAnimation();
                displayError(error.message);
            }
        }

        function startProgressAnimation() {
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            const stages = [
                'Initializing 5-agent system...',
                'Deep psychological analysis...',
                'Conversion intelligence extraction...',
                'Customer interview simulation...',
                'Sales intelligence gathering...',
                'Campaign synthesis...',
                'Finalizing comprehensive report...'
            ];
            
            let progress = 0;
            let stageIndex = 0;
            
            progressInterval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 95) progress = 95;
                
                progressFill.style.width = progress + '%';
                
                if (progress > (stageIndex + 1) * 12 && stageIndex < stages.length - 1) {
                    stageIndex++;
                    progressText.textContent = stages[stageIndex];
                }
            }, 1000);
        }

        function stopProgressAnimation() {
            if (progressInterval) {
                clearInterval(progressInterval);
                progressInterval = null;
            }
            document.getElementById('progressFill').style.width = '100%';
        }

        function displayResults(data, duration) {
            document.getElementById('loadingState').style.display = 'none';
            document.getElementById('statusIndicator').textContent = 'Complete';
            document.getElementById('statusIndicator').className = 'status-indicator status-complete';
            
            // Store report for download
            currentReport = data;
            
            // Format and display results
            const formattedReport = formatReport(data, duration);
            document.getElementById('resultContent').innerHTML = formattedReport;
            
            // Scroll to results
            document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth' });
        }

        function displayError(errorMessage) {
            document.getElementById('loadingState').style.display = 'none';
            document.getElementById('statusIndicator').textContent = 'Error';
            document.getElementById('statusIndicator').className = 'status-indicator';
            document.getElementById('statusIndicator').style.background = '#fecaca';
            document.getElementById('statusIndicator').style.color = '#dc2626';
            
            document.getElementById('resultContent').innerHTML = `
                <div style="text-align: center; padding: 40px; color: #dc2626;">
                    <h3>❌ Analysis Error</h3>
                    <p>Error: ${errorMessage}</p>
                    <p style="margin-top: 20px; color: #64748b;">Please try again or contact support if the issue persists.</p>
                </div>
            `;
        }

        function formatReport(data, duration) {
            const report = data.report || data.formatted_report || JSON.stringify(data, null, 2);
            const qualityScore = data.quality_score ? (data.quality_score * 100).toFixed(1) : 'N/A';
            const confidenceScore = data.confidence_score ? (data.confidence_score * 100).toFixed(1) : 'N/A';
            
            return `
                <div style="margin-bottom: 30px; padding: 20px; background: #f8fafc; border-radius: 8px;">
                    <h3 style="color: #1e293b; margin-bottom: 15px;">📊 Analysis Summary</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                        <div><strong>Processing Time:</strong> ${duration}s</div>
                        <div><strong>Quality Score:</strong> ${qualityScore}%</div>
                        <div><strong>Confidence:</strong> ${confidenceScore}%</div>
                        <div><strong>System:</strong> 5-Agent Intelligence</div>
                    </div>
                </div>
                
                <div style="background: #ffffff; padding: 25px; border-radius: 8px; border: 1px solid #e2e8f0;">
                    <pre style="white-space: pre-wrap; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14px; line-height: 1.6; color: #334155;">${report}</pre>
                </div>
            `;
        }

        function downloadReport() {
            if (!currentReport) {
                alert('No report available to download.');
                return;
            }
            
            const reportContent = currentReport.report || currentReport.formatted_report || JSON.stringify(currentReport, null, 2);
            const blob = new Blob([reportContent], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `intelligence-report-${new Date().toISOString().split('T')[0]}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        function clearForm() {
            document.getElementById('businessContext').value = '';
            document.getElementById('resultSection').style.display = 'none';
            currentReport = null;
        }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
