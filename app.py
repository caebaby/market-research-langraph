from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime
from supabase import create_client, Client
from typing import List, Optional

# Load environment
load_dotenv()

# Import agents - COMMENTED OUT FOR NOW since it's causing import errors
from Team_ICP.workflows.graph import graph

app = FastAPI(title="Level 5 ICP Intelligence")

# Supabase client
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
    """Quick test endpoint"""
    return {"message": "Level 5 Agent is running!"}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enterprise Intelligence Platform</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #2d3748; line-height: 1.6; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .header-content { max-width: 1400px; margin: 0 auto; padding: 0 2rem; display: flex; justify-content: space-between; align-items: center; }
            .header h1 { font-size: 2.5rem; display: flex; align-items: center; gap: 1rem; }
            .header-stats { display: flex; gap: 2rem; }
            .stat { text-align: center; }
            .stat-value { font-size: 1.5rem; font-weight: bold; }
            .stat-label { font-size: 0.875rem; opacity: 0.9; }
            .container { max-width: 1400px; margin: 0 auto; padding: 2rem; }
            .tabs { display: flex; gap: 1rem; margin-bottom: 2rem; border-bottom: 2px solid #e2e8f0; }
            .tab { padding: 1rem 2rem; background: none; border: none; font-size: 1rem; font-weight: 600; color: #718096; cursor: pointer; transition: color 0.2s; }
            .tab.active { color: #667eea; }
            .tab.active::after { content: ''; position: absolute; bottom: -2px; left: 0; right: 0; height: 2px; background: #667eea; }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            .form-section { background: white; border-radius: 12px; padding: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 2rem; }
            .form-section h2 { font-size: 1.5rem; margin-bottom: 1.5rem; color: #2d3748; }
            .form-grid { display: grid; grid-template-columns: 1fr 300px; gap: 2rem; }
            .form-group { margin-bottom: 1.5rem; }
            .form-group label { display: block; font-weight: 600; margin-bottom: 0.5rem; color: #4a5568; }
            textarea { width: 100%; min-height: 200px; padding: 1rem; border: 2px solid #e2e8f0; border-radius: 8px; font-family: inherit; font-size: 1rem; resize: vertical; transition: border-color 0.2s; }
            textarea:focus { outline: none; border-color: #667eea; }
            select { width: 100%; padding: 0.75rem; border: 2px solid #e2e8f0; border-radius: 8px; font-family: inherit; font-size: 1rem; background: white; cursor: pointer; }
            .agent-selection { background: #f7fafc; padding: 1.5rem; border-radius: 8px; }
            .agent-selection h3 { font-size: 1.1rem; margin-bottom: 1rem; color: #2d3748; }
            .agent-checkbox { display: flex; align-items: center; padding: 0.75rem; margin-bottom: 0.5rem; background: white; border-radius: 6px; cursor: pointer; transition: all 0.2s; }
            .agent-checkbox:hover { background: #edf2f7; }
            .agent-checkbox input { margin-right: 0.75rem; width: 18px; height: 18px; cursor: pointer; }
            .agent-checkbox label { cursor: pointer; flex: 1; font-weight: 500; }
            .agent-status { font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 4px; background: #48bb78; color: white; }
            .agent-status.inactive { background: #cbd5e0; }
            .button-group { display: flex; gap: 1rem; margin-top: 2rem; }
            .btn { padding: 0.75rem 2rem; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 0.5rem; }
            .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); }
            .btn-secondary { background: #e2e8f0; color: #4a5568; }
            .results-section { background: white; border-radius: 12px; padding: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: none; margin-bottom: 2rem; }
            .results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 2px solid #e2e8f0; }
            .results-actions { display: flex; gap: 1rem; }
            .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
            .metric-card { background: #f7fafc; padding: 1.5rem; border-radius: 8px; text-align: center; }
            .metric-value { font-size: 2rem; font-weight: bold; color: #667eea; }
            .metric-label { font-size: 0.875rem; color: #718096; margin-top: 0.25rem; }
            .analysis-section { margin-bottom: 2rem; padding: 1.5rem; background: #f7fafc; border-radius: 8px; }
            .analysis-section h3 { font-size: 1.25rem; margin-bottom: 1rem; color: #2d3748; display: flex; align-items: center; gap: 0.5rem; }
            .analysis-content { line-height: 1.8; color: #4a5568; white-space: pre-wrap; }
            .hitl-controls { display: flex; gap: 1rem; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; }
            .hitl-btn { padding: 0.5rem 1rem; border: none; border-radius: 6px; font-size: 0.875rem; font-weight: 600; cursor: pointer; transition: all 0.2s; }
            .approve-btn { background: #48bb78; color: white; }
            .improve-btn { background: #ed8936; color: white; }
            .reject-btn { background: #f56565; color: white; }
            .reports-table { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
            .reports-table table { width: 100%; border-collapse: collapse; }
            .reports-table th { background: #f7fafc; padding: 1rem; text-align: left; font-weight: 600; color: #4a5568; border-bottom: 2px solid #e2e8f0; }
            .reports-table td { padding: 1rem; border-bottom: 1px solid #e2e8f0; }
            .reports-table tr:hover { background: #f7fafc; }
            .view-report-btn { padding: 0.25rem 0.75rem; background: #667eea; color: white; border: none; border-radius: 4px; font-size: 0.875rem; cursor: pointer; }
            .loading { text-align: center; padding: 3rem; }
            .spinner { width: 50px; height: 50px; border: 4px solid #e2e8f0; border-top: 4px solid #667eea; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            .progress-container { margin-top: 1rem; }
            .progress-bar { width: 100%; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }
            .progress-fill { height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); transition: width 0.3s ease; }
            .progress-steps { display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.75rem; color: #718096; }
            @media (max-width: 1024px) { .form-grid { grid-template-columns: 1fr; } .header-content { flex-direction: column; gap: 1rem; } }
            @media (max-width: 768px) { .container { padding: 1rem; } .metrics-grid { grid-template-columns: 1fr; } .button-group { flex-direction: column; } .btn { width: 100%; justify-content: center; } }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <h1>🧠 Enterprise Intelligence Platform</h1>
                <div class="header-stats">
                    <div class="stat"><div class="stat-value" id="totalReports">0</div><div class="stat-label">Reports</div></div>
                    <div class="stat"><div class="stat-value" id="avgQuality">0%</div><div class="stat-label">Avg Quality</div></div>
                    <div class="stat"><div class="stat-value" id="activeAgents">0/6</div><div class="stat-label">Active Agents</div></div>
                </div>
            </div>
        </div>

        <div class="container">
            <div class="tabs">
                <button class="tab active" onclick="switchTab('generate')">🚀 Generate</button>
                <button class="tab" onclick="switchTab('reports')">📊 Reports</button>
                <button class="tab" onclick="switchTab('settings')">⚙️ Settings</button>
            </div>

            <div id="generate-tab" class="tab-content active">
                <div class="form-section">
                    <h2>🎯 Business Intelligence Analysis</h2>
                    <div class="form-grid">
                        <div>
                            <div class="form-group">
                                <label for="businessContext">Business Context</label>
                                <textarea id="businessContext" placeholder="Describe your business..."></textarea>
                            </div>
                            <div class="form-group">
                                <label for="team">Team</label>
                                <select id="team">
                                    <option value="icp">ICP Team</option>
                                    <option value="sales">Sales Team (Coming Soon)</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="industry">Industry</label>
                                <select id="industry">
                                    <option value="">Select...</option>
                                    <option value="financial">Financial</option>
                                    <option value="saas">SaaS</option>
                                    <option value="ecommerce">E-commerce</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="reportName">Report Name</label>
                                <input type="text" id="reportName" placeholder="Q1 2025 ICP">
                            </div>
                        </div>
                        <div class="agent-selection">
                            <h3>Select Agents</h3>
                            <div class="agent-checkbox"><input type="checkbox" id="psychological"><label for="psychological">🧠 Psychological</label><span class="agent-status">Active</span></div>
                            <div class="agent-checkbox"><input type="checkbox" id="conversion"><label for="conversion">🎯 Conversion</label><span class="agent-status">Active</span></div>
                            <div class="agent-checkbox"><input type="checkbox" id="competitor"><label for="competitor">🔍 Competitor</label><span class="agent-status">Active</span></div>
                            <div class="agent-checkbox"><input type="checkbox" id="interview"><label for="interview">🎭 Interview</label><span class="agent-status">Active</span></div>
                            <div class="agent-checkbox"><input type="checkbox" id="voice"><label for="voice">🗣️ Voice</label><span class="agent-status">Active</span></div>
                            <div class="agent-checkbox"><input type="checkbox" id="synthesis"><label for="synthesis">📋 Synthesis</label><span class="agent-status">Active</span></div>
                        </div>
                    </div>
                    <div class="button-group">
                        <button class="btn btn-primary" onclick="generateReport()">🚀 Generate</button>
                        <button class="btn btn-secondary" onclick="clearForm()">🔄 Clear</button>
                    </div>
                </div>
                <div class="results-section" id="results">
                    <div class="results-header">
                        <h2>📊 Intelligence Report</h2>
                        <div class="results-actions">
                            <button class="btn btn-secondary" onclick="saveReport()">💾 Save</button>
                            <button class="btn btn-primary" onclick="downloadReport()">📥 Download</button>
                        </div>
                    </div>
                    <div id="resultsContent">
                        <div class="loading">
                            <div class="spinner"></div>
                            <p>Analyzing...</p>
                            <div class="progress-container">
                                <div class="progress-bar"><div class="progress-fill" id="progressBar"></div></div>
                                <div class="progress-steps"><span>Start</span><span>Analyze</span><span>Refine</span><span>Done</span></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div id="reports-tab" class="tab-content">
                <div class="reports-table">
                    <table><thead><tr><th>Name</th><th>Date</th><th>Industry</th><th>Quality</th><th>Agents</th><th>Actions</th></tr></thead>
                    <tbody id="reportsTableBody"><tr><td colspan="6">No reports yet.</td></tr></tbody>
                </table>
            </div>
            </div>
            <div id="settings-tab" class="tab-content">
                <div class="form-section">
                    <h2>⚙️ Settings</h2>
                    <div class="form-group">
                        <label>Quality Threshold</label>
                        <select id="qualityThreshold"><option value="0.9" selected>90%</option></select>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let currentReport = null;
            let reports = JSON.parse(localStorage.getItem('reports') || '[]');
            let progressInterval = null;

            updateStats();

            function switchTab(tab) {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
                event.target.classList.add('active');
                document.getElementById(tab + '-tab').classList.add('active');
                if (tab === 'reports') loadReports();
            }

            async function generateReport() {
                const context = document.getElementById('businessContext').value.trim();
                if (!context) return alert('Enter context');
                const team = document.getElementById('team').value;
                const agents = Array.from(document.querySelectorAll('.agent-checkbox input:checked')).map(cb => cb.id);
                if (!agents.length) return alert('Select at least one agent');

                document.getElementById('results').style.display = 'block';
                startProgress();
                document.getElementById('results').scrollIntoView({behavior: 'smooth'});

                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({business_context: context, agents: agents, team: team, industry: document.getElementById('industry').value, report_name: document.getElementById('reportName').value})
                    });
                    if (!response.ok) throw new Error('Failed');
                    const data = await response.json();
                    currentReport = {...data, name: document.getElementById('reportName').value || `Report_${new Date().toLocaleDateString()}`, industry: document.getElementById('industry').value, date: new Date().toISOString(), context, agents, team};
                    stopProgress();
                    displayResults(currentReport);
                } catch (error) {
                    stopProgress();
                    document.getElementById('resultsContent').innerHTML = `<div style="text-align:center;padding:2rem;color:#e53e3e;"><h3>❌ Error</h3><p>${error.message}</p></div>`;
                }
            }

            function displayResults(data) {
                const score = (data.success_score * 100).toFixed(1);
                let sections = '';
                data.agents.forEach(agent => sections += `<div class="analysis-section"><h3>${agent.charAt(0).toUpperCase() + agent.slice(1)}</h3><div class="analysis-content">${data.analysis[agent] || 'Pending'}</div><div class="hitl-controls"><button class="hitl-btn approve-btn" onclick="hitlAction('${agent}', 'approve')">✓</button><button class="hitl-btn improve-btn" onclick="hitlAction('${agent}', 'improve')">↻</button><button class="hitl-btn reject-btn" onclick="hitlAction('${agent}', 'reject')">✗</button></div></div>`);
                document.getElementById('resultsContent').innerHTML = `
                    <div class="metrics-grid">
                        <div class="metric-card"><div class="metric-value">${score}%</div><div class="metric-label">Quality</div></div>
                        <div class="metric-card"><div class="metric-value">${data.agents.length}</div><div class="metric-label">Agents</div></div>
                        <div class="metric-card"><div class="metric-value">Level 5</div><div class="metric-label">Tier</div></div>
                    </div>
                    ${sections}
                    <div style="margin-top:2rem;padding-top:1rem;border-top:1px solid #e2e8f0;color:#718096;">Generated by ${data.agent} • ${new Date(data.timestamp).toLocaleString()}</div>
                `;
            }

            function startProgress() {
                let progress = 0;
                const bar = document.getElementById('progressBar');
                progressInterval = setInterval(() => {progress += 15; if (progress > 90) progress = 90; bar.style.width = progress + '%';}, 500);
            }

            function stopProgress() {
                if (progressInterval) {clearInterval(progressInterval); document.getElementById('progressBar').style.width = '100%'; setTimeout(() => document.getElementById('progressBar').style.width = '0%', 1000);}
            }

            function saveReport() {
                if (currentReport) {reports.unshift(currentReport); localStorage.setItem('reports', JSON.stringify(reports)); updateStats(); alert('Saved');}
            }

            function downloadReport() {
                if (currentReport) {
                    const content = `ENTERPRISE REPORT\n${currentReport.name}\n${new Date(currentReport.date).toLocaleString()}\nQuality: ${(currentReport.success_score*100).toFixed(1)}%\nAgents: ${currentReport.agents.join(', ')}\n\nCONTEXT:\n${currentReport.context}\n\nANALYSIS:\n${Object.entries(currentReport.analysis).map(([k,v])=>`${k}: ${v}`).join('\\n')}\n\n---\nLevel 5 System`;
                    const blob = new Blob([content], {type: 'text/plain'});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a'); a.href = url; a.download = `Report_${new Date().toISOString().split('T')[0]}.txt`; document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
                }
            }

            function loadReports() {
                const tbody = document.getElementById('reportsTableBody');
                tbody.innerHTML = reports.length ? reports.map((r,i)=>`<tr><td>${r.name}</td><td>${new Date(r.date).toLocaleDateString()}</td><td>${r.industry||'N/A'}</td><td>${(r.success_score*100).toFixed(1)}%</td><td>${r.agents.join(', ')}</td><td><button onclick="viewReport(${i})">View</button></td></tr>`).join('') : '<tr><td colspan="6">No reports</td></tr>';
            }

            function viewReport(index) {currentReport = reports[index]; displayResults(currentReport); document.getElementById('results').style.display='block'; switchTab('generate'); document.getElementById('results').scrollIntoView({behavior:'smooth'});}

            function updateStats() {
                document.getElementById('totalReports').textContent = reports.length;
                if (reports.length) document.getElementById('avgQuality').textContent = (reports.reduce((s,r)=>s+r.success_score,0)/reports.length*100).toFixed(1)+'%';
                document.getElementById('activeAgents').textContent = `${reports.length ? reports[0].agents.length : 0}/6`;
            }

            function clearForm() {document.getElementById('businessContext').value=''; document.getElementById('team').value='icp'; document.getElementById('industry').value=''; document.getElementById('reportName').value=''; document.getElementById('results').style.display='none'; currentReport=null;}

            function hitlAction(agent, action) {
                alert(`${action.charAt(0).toUpperCase() + action.slice(1)} ${agent} analysis`);
                // Placeholder for Supabase HITL storage
            }
        </script>
    </body>
    </html>
    """
from fastapi import Request

@app.post("/analyze")
async def analyze(request: Request):
    data = await request.json()
    business_context = data.get("business_context")
    agents = data.get("agents", [])
    team = data.get("team")
    industry = data.get("industry")
    report_name = data.get("report_name")
    
    results = {}
    overall_score = 0.0
    for agent in agents:
        state = {"task": f"{agent} analysis", "context": business_context, "new_data": True, "team": team}
        result = await graph.ainvoke(state)
        results[agent] = result["result"]
        overall_score = max(overall_score, result["quality_score"])
    if supabase:
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
    return {
        "analysis": results,
        "success_score": overall_score,
        "agent": f"{team} Platform",
        "timestamp": datetime.now().isoformat()
    }
