from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime
from supabase import create_client, Client
from typing import List, Optional

# Load environment
load_dotenv()

# Try to import agents - handle gracefully if fails
try:
    from team_icp.workflows.graph import graph
    GRAPH_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import graph: {e}")
    GRAPH_AVAILABLE = False

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
    """Quick test endpoint"""
    return {
        "message": "Level 5 Agent is running!",
        "graph_available": GRAPH_AVAILABLE,
        "supabase_connected": supabase is not None
    }

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
            .tab { padding: 1rem 2rem; background: none; border: none; font-size: 1rem; font-weight: 600; color: #718096; cursor: pointer; transition: color 0.2s; position: relative; }
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
            input[type="text"] { width: 100%; padding: 0.75rem; border: 2px solid #e2e8f0; border-radius: 8px; font-family: inherit; font-size: 1rem; }
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
            .error-message { background: #fed7d7; color: #c53030; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }
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
                                <textarea id="businessContext" placeholder="Describe your business, target market, challenges, and goals..."></textarea>
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
                                    <option value="">Select Industry...</option>
                                    <option value="financial">Financial Services</option>
                                    <option value="saas">SaaS</option>
                                    <option value="ecommerce">E-commerce</option>
                                    <option value="healthcare">Healthcare</option>
                                    <option value="education">Education</option>
                                    <option value="consulting">Consulting</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="reportName">Report Name</label>
                                <input type="text" id="reportName" placeholder="Q1 2025 ICP Analysis">
                            </div>
                        </div>
                        <div class="agent-selection">
                            <h3>Select Agents</h3>
                            <div class="agent-checkbox"><input type="checkbox" id="psychological" checked><label for="psychological">🧠 Psychological</label><span class="agent-status">Active</span></div>
                            <div class="agent-checkbox"><input type="checkbox" id="conversion"><label for="conversion">🎯 Conversion</label><span class="agent-status">Active</span></div>
                            <div class="agent-checkbox"><input type="checkbox" id="competitor"><label for="competitor">🔍 Competitor</label><span class="agent-status">Active</span></div>
                            <div class="agent-checkbox"><input type="checkbox" id="interview"><label for="interview">🎭 Interview</label><span class="agent-status">Active</span></div>
                            <div class="agent-checkbox"><input type="checkbox" id="voice"><label for="voice">🗣️ Voice</label><span class="agent-status">Active</span></div>
                            <div class="agent-checkbox"><input type="checkbox" id="synthesis"><label for="synthesis">📋 Synthesis</label><span class="agent-status">Active</span></div>
                        </div>
                    </div>
                    <div class="button-group">
                        <button class="btn btn-primary" onclick="generateReport()">🚀 Generate Intelligence Report</button>
                        <button class="btn btn-secondary" onclick="clearForm()">🔄 Clear Form</button>
                    </div>
                </div>
                <div class="results-section" id="results">
                    <div class="results-header">
                        <h2>📊 Intelligence Report</h2>
                        <div class="results-actions">
                            <button class="btn btn-secondary" onclick="saveReport()">💾 Save Report</button>
                            <button class="btn btn-primary" onclick="downloadReport()">📥 Download</button>
                        </div>
                    </div>
                    <div id="resultsContent">
                        <div class="loading">
                            <div class="spinner"></div>
                            <p>Analyzing your business context...</p>
                            <div class="progress-container">
                                <div class="progress-bar"><div class="progress-fill" id="progressBar" style="width: 0%"></div></div>
                                <div class="progress-steps"><span>Initialize</span><span>Analyze</span><span>Refine</span><span>Complete</span></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div id="reports-tab" class="tab-content">
                <div class="reports-table">
                    <table><thead><tr><th>Report Name</th><th>Date</th><th>Industry</th><th>Quality Score</th><th>Agents Used</th><th>Actions</th></tr></thead>
                    <tbody id="reportsTableBody"><tr><td colspan="6" style="text-align: center; color: #718096;">No reports generated yet. Create your first report!</td></tr></tbody>
                </table>
            </div>
            </div>
            <div id="settings-tab" class="tab-content">
                <div class="form-section">
                    <h2>⚙️ Platform Settings</h2>
                    <div class="form-group">
                        <label>Quality Threshold</label>
                        <select id="qualityThreshold">
                            <option value="0.8">80% - Standard</option>
                            <option value="0.9" selected>90% - High Quality</option>
                            <option value="0.95">95% - Ultra Quality</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Auto-save Reports</label>
                        <select id="autoSave">
                            <option value="true" selected>Enabled</option>
                            <option value="false">Disabled</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>

        <script src="/dashboard.js"></script>
    </body>
    </html>
    """
   

@app.get("/dashboard.js")
async def dashboard_js():
    """Serve the JavaScript separately to avoid string escaping issues"""
    js_content = """
let currentReport = null;
let reports = JSON.parse(localStorage.getItem('level5_reports') || '[]');
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
    console.log('Generate report clicked');
    
    const context = document.getElementById('businessContext').value.trim();
    if (!context) {
        alert('Please enter your business context to generate insights.');
        return;
    }
    
    const team = document.getElementById('team').value;
    const agents = Array.from(document.querySelectorAll('.agent-checkbox input:checked')).map(cb => cb.id);
    
    if (!agents.length) {
        alert('Please select at least one agent for analysis.');
        return;
    }

    document.getElementById('results').style.display = 'block';
    startProgress();
    document.getElementById('results').scrollIntoView({behavior: 'smooth'});

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                business_context: context,
                agents: agents,
                team: team,
                industry: document.getElementById('industry').value,
                report_name: document.getElementById('reportName').value
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }
        
        const data = await response.json();
        currentReport = {
            ...data,
            name: document.getElementById('reportName').value || 'Report_' + new Date().toLocaleDateString(),
            industry: document.getElementById('industry').value,
            date: new Date().toISOString(),
            context,
            agents,
            team
        };
        
        stopProgress();
        displayResults(currentReport);
        
        const autoSave = document.getElementById('autoSave');
        if (autoSave && autoSave.value === 'true') {
            saveReport(true);
        }
        
    } catch (error) {
        console.error('Error:', error);
        stopProgress();
        document.getElementById('resultsContent').innerHTML = '<div class="error-message"><h3>❌ Analysis Error</h3><p>' + error.message + '</p></div>';
    }
}

function displayResults(data) {
    const score = ((data.success_score || 0) * 100).toFixed(1);
    let sections = '';
    
    if (data.agents && data.analysis) {
        const agentIcons = {
            'psychological': '🧠',
            'conversion': '🎯',
            'competitor': '🔍',
            'interview': '🎭',
            'voice': '🗣️',
            'synthesis': '📋'
        };
        
        data.agents.forEach(agent => {
            const icon = agentIcons[agent] || '📊';
            const agentName = agent.charAt(0).toUpperCase() + agent.slice(1);
            const analysis = data.analysis[agent] || 'Analysis pending...';
            
            sections += `
                <div class="analysis-section">
                    <h3>${icon} ${agentName} Analysis</h3>
                    <div class="analysis-content">${analysis}</div>
                    <div class="hitl-controls">
                        <button class="hitl-btn approve-btn" onclick="hitlAction('${agent}', 'approve')">✓ Approve</button>
                        <button class="hitl-btn improve-btn" onclick="hitlAction('${agent}', 'improve')">↻ Improve</button>
                        <button class="hitl-btn reject-btn" onclick="hitlAction('${agent}', 'reject')">✗ Reject</button>
                    </div>
                </div>
            `;
        });
    }
    
    document.getElementById('resultsContent').innerHTML = `
        <div class="metrics-grid">
            <div class="metric-card"><div class="metric-value">${score}%</div><div class="metric-label">Quality Score</div></div>
            <div class="metric-card"><div class="metric-value">${data.agents?.length || 0}</div><div class="metric-label">Agents Used</div></div>
            <div class="metric-card"><div class="metric-value">Level 5</div><div class="metric-label">Intelligence Tier</div></div>
        </div>
        ${sections}
        <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; color: #718096; font-size: 0.875rem;">
            Generated by ${data.agent || 'Level 5 System'} • ${new Date(data.timestamp).toLocaleString()}
        </div>
    `;
}

function startProgress() {
    let progress = 0;
    const bar = document.getElementById('progressBar');
    progressInterval = setInterval(() => {
        progress += Math.random() * 15 + 5;
        if (progress > 90) progress = 90;
        bar.style.width = progress + '%';
    }, 500);
}

function stopProgress() {
    if (progressInterval) {
        clearInterval(progressInterval);
        document.getElementById('progressBar').style.width = '100%';
        setTimeout(() => {
            document.getElementById('progressBar').style.width = '0%';
        }, 1000);
    }
}

function saveReport(silent = false) {
    if (currentReport) {
        reports.unshift(currentReport);
        localStorage.setItem('level5_reports', JSON.stringify(reports));
        updateStats();
        if (!silent) alert('Report saved successfully!');
    }
}

function downloadReport() {
    if (!currentReport) return;
    
    let content = 'ENTERPRISE INTELLIGENCE REPORT\\n';
    content += '==============================\\n';
    content += currentReport.name + '\\n';
    content += 'Generated: ' + new Date(currentReport.date).toLocaleString() + '\\n';
    content += 'Quality Score: ' + (currentReport.success_score * 100).toFixed(1) + '%\\n';
    content += 'Agents Used: ' + currentReport.agents.join(', ') + '\\n';
    content += 'Industry: ' + (currentReport.industry || 'Not specified') + '\\n\\n';
    content += 'BUSINESS CONTEXT:\\n';
    content += '----------------\\n';
    content += currentReport.context + '\\n\\n';
    content += 'ANALYSIS RESULTS:\\n';
    content += '----------------\\n';
    
    Object.entries(currentReport.analysis || {}).forEach(([agent, analysis]) => {
        content += agent.toUpperCase() + ' ANALYSIS:\\n' + analysis + '\\n\\n';
    });
    
    content += '---\\n';
    content += 'Generated by Level 5 Enterprise Intelligence Platform\\n';
    
    const blob = new Blob([content], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = (currentReport.name || 'Report') + '_' + new Date().toISOString().split('T')[0] + '.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function loadReports() {
    const tbody = document.getElementById('reportsTableBody');
    if (reports.length) {
        let rows = '';
        reports.forEach((r, i) => {
            rows += '<tr>';
            rows += '<td>' + r.name + '</td>';
            rows += '<td>' + new Date(r.date).toLocaleDateString() + '</td>';
            rows += '<td>' + (r.industry || 'N/A') + '</td>';
            rows += '<td>' + ((r.success_score || 0) * 100).toFixed(1) + '%</td>';
            rows += '<td>' + r.agents.join(', ') + '</td>';
            rows += '<td><button class="view-report-btn" onclick="viewReport(' + i + ')">View</button></td>';
            rows += '</tr>';
        });
        tbody.innerHTML = rows;
    } else {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #718096;">No reports generated yet.</td></tr>';
    }
}

function viewReport(index) {
    currentReport = reports[index];
    displayResults(currentReport);
    document.getElementById('results').style.display = 'block';
    switchTab('generate');
    document.getElementById('results').scrollIntoView({behavior: 'smooth'});
}

function updateStats() {
    document.getElementById('totalReports').textContent = reports.length;
    if (reports.length > 0) {
        const avgScore = (reports.reduce((sum, r) => sum + (r.success_score || 0), 0) / reports.length * 100).toFixed(1);
        document.getElementById('avgQuality').textContent = avgScore + '%';
        document.getElementById('activeAgents').textContent = '6/6';
    } else {
        document.getElementById('avgQuality').textContent = '0%';
        document.getElementById('activeAgents').textContent = '0/6';
    }
}

function clearForm() {
    document.getElementById('businessContext').value = '';
    document.getElementById('team').value = 'icp';
    document.getElementById('industry').value = '';
    document.getElementById('reportName').value = '';
    document.getElementById('results').style.display = 'none';
    currentReport = null;
}

function hitlAction(agent, action) {
    console.log('HITL: ' + action + ' for ' + agent);
    alert(action.charAt(0).toUpperCase() + action.slice(1) + 'd ' + agent + ' analysis.');
}

// Check system status on load
fetch('/test').then(r => r.json()).then(data => {
    if (!data.graph_available) {
        console.warn('Graph system not available - running in mock mode');
    }
}).catch(err => console.error('System check failed:', err));
"""
    return Response(content=js_content, media_type="application/javascript")

@app.post("/analyze")
async def analyze(request: Request):
    try:
        # Parse request data
        data = await request.json()
        business_context = data.get("business_context")
        agents = data.get("agents", [])
        team = data.get("team")
        industry = data.get("industry")
        report_name = data.get("report_name")
        
        # Validate required fields
        if not business_context:
            raise HTTPException(status_code=400, detail="business_context is required")
        if not agents:
            raise HTTPException(status_code=400, detail="At least one agent must be selected")
        
        results = {}
        overall_score = 0.0
        shared_insights = {}  # For agent communication
        
        # Check if graph is available
        if not GRAPH_AVAILABLE:
            # Fallback: return mock data if graph isn't available
            print("Warning: Running in mock mode - graph not available")
            for agent in agents:
                results[agent] = f"Mock {agent} analysis for: {business_context[:100]}... (Graph system not available - this is test data)"
                overall_score = 0.75  # Mock score
        else:
            # Initialize services (these should be provided by your graph)
            # If your graph provides these, remove this section
            try:
                from core.memory import HybridMemory
                from core.tools import ToolBox
                memory_service = HybridMemory()
                tool_executor = ToolBox()
            except ImportError:
                memory_service = None
                tool_executor = None
                print("Warning: Memory/Tool services not available")
            
            # Generate a client_id for this analysis session
            client_id = f"{team}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Execute actual agent analysis
            for agent in agents:
                try:
                    state = {
                        # Legacy fields for backward compatibility
                        "task": f"{agent} analysis",
                        "context": business_context,
                        "new_data": True,
                        "team": team,
                        
                        # StandardAgentNode required fields
                        "current_task": {
                            "description": f"Perform {agent} analysis for: {business_context[:200]}...",
                            "is_high_stakes": False
                        },
                        "master_context": business_context,
                        "business_context": business_context,
                        "client_id": client_id,
                        "shared_insights": shared_insights,
                        
                        # Services (if your graph doesn't provide them)
                        "memory_service": memory_service,
                        "tool_executor": tool_executor,
                    }
                    
                    result = await graph.ainvoke(state)
                    
                    # DEBUG: Log what we got back
                    print(f"\n=== DEBUG: Result for {agent} ===")
                    print(f"Keys in result: {list(result.keys())}")
                    print(f"current_output exists: {'current_output' in result}")
                    print(f"quality_score: {result.get('quality_score', 'NOT FOUND')}")
                    print(f"agent_name: {result.get('agent_name', 'NOT FOUND')}")
                    
                    # Check for different possible output keys
                    possible_output_keys = ['current_output', 'output', 'response', 'analysis', agent + '_analysis']
                    for key in possible_output_keys:
                        if key in result:
                            print(f"Found output in key '{key}': {result[key][:200]}...")
                            break
                    
                    # Extract results
                    results[agent] = result.get("current_output", "Analysis completed but no output found")
                    overall_score = max(overall_score, result.get("quality_score", 0))
                    
                    # Update shared insights for next agent
                    if "shared_insights" in result:
                        shared_insights = result["shared_insights"]
                    
                except Exception as agent_error:
                    print(f"Error executing {agent} agent: {agent_error}")
                    results[agent] = f"Error during analysis: {str(agent_error)}"
        
        # Store in Supabase if available
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
                # Continue anyway - don't fail the whole request
        
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

# Health check endpoint
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "graph_available": GRAPH_AVAILABLE,
        "supabase_connected": supabase is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test-v4")
async def test_v4():
    """Test V4 agents"""
    results = {}
    
    # Test 1: Foundation
    try:
        from core.standard_agent_v4 import StandardAgentNodeV4
        from core.memory_adapter import MemoryAdapter
        from core.config import Config
        
        results["foundation"] = "✅ V4 imports work"
        
        llm = Config.get_llm()
        results["llm"] = f"✅ LLM configured: {type(llm)}"
        
        adapter = MemoryAdapter()
        results["memory"] = "✅ Memory adapter created"
    except Exception as e:
        results["foundation_error"] = str(e)
    
    # Test 2: Psychological V4 - INIT ONLY
    try:
        from team_icp.agents.psychological_v4 import PsychologicalAgentV4
        
        agent = PsychologicalAgentV4()
        results["psych_v4"] = "✅ Agent initialized successfully (not executed)"
        
    except Exception as e:
        results["psych_v4_error"] = str(e)
    
    return results

@app.post("/test-v4-execute")
async def test_v4_execute(request: Request):
    """Actually execute V4 agent with small test"""
    try:
        data = await request.json()
        business_context = data.get("business_context", "SaaS founders seeking growth")
        
        from team_icp.agents.psychological_v4 import PsychologicalAgentV4
        
        agent = PsychologicalAgentV4()
        state = {
            "business_context": business_context,
            "current_task": {"description": "Brief analysis"},
            "shared_insights": {}
        }
        
        # Run with timeout
        import asyncio
        result = await asyncio.wait_for(
            asyncio.to_thread(agent, state),
            timeout=60.0
        )
        
        return {
            "success": True,
            "quality": result.get('quality_score', 0),
            "output": result.get('current_output', '')[:500] + "...",  # First 500 chars
            "needs_review": result.get('requires_human_review', False)
        }
        
    except asyncio.TimeoutError:
        return {"success": False, "error": "Analysis timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/dashboard-v4", response_class=HTMLResponse)
async def dashboard_v4():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>V4 Agent Test Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f0f0f0; padding: 20px; border-radius: 8px; margin: 20px 0; }
            textarea { width: 100%; height: 100px; margin: 10px 0; }
            button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #45a049; }
            .results { margin-top: 20px; padding: 20px; background: white; border-radius: 8px; }
            .error { color: red; }
            .success { color: green; }
            #loading { display: none; }
        </style>
    </head>
    <body>
        <h1>🧪 V4 Agent Test Dashboard</h1>
        
        <div class="container">
            <h2>Test Psychological V4 Agent</h2>
            <textarea id="context" placeholder="Enter business context (e.g., SaaS founders seeking growth)">Executive coaches at $100k/month wanting to scale</textarea>
            <button onclick="testAgent()">Run V4 Analysis</button>
            <div id="loading">⏳ Running analysis... (this may take 30-60 seconds)</div>
        </div>
        
        <div id="results" class="results" style="display:none;">
            <h3>Results:</h3>
            <div id="output"></div>
        </div>
        
        <script>
        async function testAgent() {
            const context = document.getElementById('context').value;
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            const output = document.getElementById('output');
            
            loading.style.display = 'block';
            results.style.display = 'none';
            
            try {
                const response = await fetch('/test-v4-execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({business_context: context})
                });
                
                const data = await response.json();
                loading.style.display = 'none';
                results.style.display = 'block';
                
                if (data.success) {
                    output.innerHTML = `
                        <p class="success">✅ Analysis completed!</p>
                        <p><strong>Quality Score:</strong> ${data.quality}</p>
                        <p><strong>Needs Review:</strong> ${data.needs_review}</p>
                        <p><strong>Output Preview:</strong></p>
                        <pre>${data.output}</pre>
                    `;
                } else {
                    output.innerHTML = `<p class="error">❌ Error: ${data.error}</p>`;
                }
            } catch (error) {
                loading.style.display = 'none';
                results.style.display = 'block';
                output.innerHTML = `<p class="error">❌ Error: ${error.message}</p>`;
            }
        }
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
