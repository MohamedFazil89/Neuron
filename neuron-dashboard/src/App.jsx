import React, { useState, useEffect } from 'react';
import { Activity, AlertCircle, CheckCircle2, Clock, Code, Zap, ChevronDown, ChevronRight, Play, RotateCcw, GitBranch, FileCode, Settings, TrendingUp, Loader2 } from 'lucide-react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

export default function NeuronDashboard() {
  const [expandedActivity, setExpandedActivity] = useState(null);
  const [showAgents, setShowAgents] = useState(false);
  const [data, setData] = useState({
    hasProject: false,
    project: null,
    projects: [],
    metrics: {
      tokensUsed: 0,
      apiCalls: 0,
      estimatedCost: 0,
      avgTaskTime: 0,
      agentFailureRate: 0,
    },
    activities: [],
    agents: [],
    systemStatus: 'offline',
    lastAction: 'Never',
  });

  const fetchState = async () => {
    try {
      const [stateRes, agentsRes, projectsRes, healthRes] = await Promise.all([
        fetch(`${API_BASE_URL}/dashboard-state`),
        fetch(`${API_BASE_URL}/agents/status`),
        fetch(`${API_BASE_URL}/list-projects`),
        fetch(`${API_BASE_URL}/health`).catch(() => ({ ok: false }))
      ]);

      const stateData = await stateRes.json();
      const agentsData = await agentsRes.json();
      const projectsData = await projectsRes.json();

      if (stateData.status === 'success') {
        const activities = stateData.features ? stateData.features.map((f, i) => ({
          id: i,
          request: f.feature,
          status: 'success',
          filesChanged: f.files?.length || 0,
          duration: "N/A",
          timestamp: f.timestamp || "Just now",
          agents: ["Orchestrator"],
          files: f.files || [],
          safetyChecks: ["Verified"]
        })).reverse() : [];

        setData(prev => ({
          ...prev,
          hasProject: stateData.has_project,
          project: stateData.project,
          projects: projectsData.data || [],
          metrics: stateData.metrics || prev.metrics,
          activities: activities,
          agents: agentsData.agents || prev.agents,
          systemStatus: healthRes.ok ? 'online' : 'offline',
          lastAction: activities.length > 0 ? activities[0].timestamp : 'Never'
        }));
      }
      setLoading(false);
    } catch (err) {
      console.error('Fetch error:', err);
      setError('Could not connect to Neuron backend');
      setLoading(false);
    }
  };

  const handleSetProject = async (projectPath) => {
    try {
      const res = await fetch(`${API_BASE_URL}/set-project`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_path: projectPath })
      });
      const result = await res.json();
      if (result.status === 'success') {
        fetchState();
      } else {
        alert('Error: ' + result.message);
      }
    } catch (err) {
      alert('Failed to set project');
    }
  };

  useEffect(() => {
    fetchState();
    const interval = setInterval(fetchState, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleAnalyze = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/analyze`);
      const result = await res.json();
      if (result.status === 'success') {
        alert('Project analyzed successfully!');
        fetchState();
      } else {
        alert('Error: ' + result.message);
      }
    } catch (err) {
      alert('Failed to connect to backend');
    }
  };

  const handleAction = async (prompt) => {
    const feature = prompt || window.prompt("Enter feature or bug fix description:");
    if (!feature) return;

    try {
      const res = await fetch(`${API_BASE_URL}/build-and-save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feature })
      });
      const result = await res.json();
      if (result.status === 'success') {
        alert('Action completed successfully!');
        fetchState();
      } else {
        alert('Error: ' + result.message);
      }
    } catch (err) {
      alert('Failed to connect to backend');
    }
  };

  if (loading && !data.project) {
    return (
      <div className="neuron-dashboard flex items-center justify-center min-h-screen">
        <Loader2 className="animate-spin text-blue-500 w-12 h-12" />
        <span className="ml-3 text-xl font-medium">Connecting to Neuron Engine...</span>
      </div>
    );
  }

  if (error && !data.project) {
    return (
      <div className="neuron-dashboard flex flex-col items-center justify-center min-h-screen">
        <AlertCircle className="text-red-500 w-16 h-16 mb-4" />
        <h2 className="text-2xl font-bold mb-2">{error}</h2>
        <p className="text-gray-400 mb-6 text-center max-w-md">Make sure Neuron-Core is running and accessible on port 8000.</p>
        <button onClick={fetchState} className="neuron-upgrade-btn">Retry Connection</button>
      </div>
    );
  }

  return (
    <div className="neuron-dashboard">
      <div className="neuron-container neuron-space-y-6">

        {/* Header with System Status */}
        <div className="neuron-header">
          <div>
            <h1>Neuron</h1>
            <p className="neuron-subtitle">AI Code Orchestrator</p>
          </div>

          <div className="neuron-status-cards">
            <div className="neuron-status-card">
              <div className="neuron-status-indicator">
                <div className={`neuron-pulse-dot ${data.systemStatus === 'online' ? 'neuron-bg-emerald' : 'bg-red-500'}`}></div>
                <span className="neuron-status-label">Engine {data.systemStatus.toUpperCase()}</span>
              </div>
              <div className="neuron-status-sublabel">Local Server: 0.0.0.0:8000</div>
            </div>

            <div className="neuron-status-card">
              <div className="neuron-status-sublabel">Last action</div>
              <div className="neuron-status-label">{data.lastAction}</div>
            </div>
          </div>
        </div>

        {/* Usage & Upgrade */}
        <div className="neuron-usage-card">
          <div className="neuron-usage-header">
            <div>
              <div className="neuron-usage-stats">{data.metrics.tokensUsed.toLocaleString()} tokens</div>
              <div className="neuron-usage-details">Usage this session · Cost: ${data.metrics.estimatedCost.toFixed(4)}</div>
            </div>
            <button className="neuron-upgrade-btn">Settings</button>
          </div>

          <div className="neuron-progress-bar">
            <div className="neuron-progress-fill" style={{ width: `${Math.min((data.metrics.tokensUsed / 1000000) * 100, 100)}%` }}></div>
          </div>
        </div>

        {/* Project Context & Actions Grid */}
        <div className="neuron-grid-3">

          {/* Project Context */}
          <div className="neuron-card">
            <h2 className="neuron-card-header">
              <Code className="neuron-icon neuron-text-blue" />
              Project Context
            </h2>

            <div className="neuron-space-y-3">
              <div>
                <div className="neuron-context-label">Select Project</div>
                <select
                  className="neuron-project-select"
                  value={data.project?.path || ""}
                  onChange={(e) => handleSetProject(e.target.value)}
                >
                  <option value="" disabled>Choose a project...</option>
                  {data.projects.map(p => (
                    <option key={p.path} value={p.path}>{p.name}</option>
                  ))}
                </select>
                <div className="neuron-context-path">{data.project?.path || "No project selected"}</div>
              </div>

              <div>
                <button
                  className="neuron-secondary-btn w-full"
                  onClick={() => {
                    const path = window.prompt("Enter new project path:");
                    if (path) handleSetProject(path);
                  }}
                >
                  <GitBranch className="neuron-icon" />
                  Add Project Path
                </button>
              </div>

              <div>
                <div className="neuron-context-label">Detected Stack</div>
                <div style={{ marginTop: '0.5rem' }} className="neuron-space-y-1">
                  {data.hasProject ? (
                    <>
                      <div className="neuron-tech-stack-item">
                        <div className="neuron-tech-dot neuron-bg-cyan"></div>
                        {data.project?.name}
                      </div>
                    </>
                  ) : (
                    <div className="neuron-tech-stack-item text-gray-500 italic">
                      Please set an active project
                    </div>
                  )}
                </div>
              </div>

              <div className="neuron-divider">
                <div className="neuron-health-indicator">
                  <CheckCircle2 className="neuron-icon neuron-text-emerald" />
                  <span className="neuron-health-text">System Ready</span>
                </div>
                <div className="neuron-health-subtext">Backend connection active</div>
              </div>
            </div>
          </div>

          {/* Action Center */}
          <div className="neuron-card">
            <h2 className="neuron-card-header">
              <Zap className="neuron-icon neuron-text-yellow" />
              Action Center
            </h2>

            <div className="neuron-action-grid">
              <button className="neuron-action-btn" onClick={() => handleAction()}>
                <div className="neuron-action-title">Build Project</div>
                <div className="neuron-action-desc">Create new features</div>
              </button>

              <button className="neuron-action-btn" onClick={() => handleAction()}>
                <div className="neuron-action-title">Add Feature</div>
                <div className="neuron-action-desc">Extend functionality</div>
              </button>

              <button className="neuron-action-btn" onClick={handleAnalyze}>
                <div className="neuron-action-title">Analyze Project</div>
                <div className="neuron-action-desc">Find issues & improvements</div>
              </button>

              <button className="neuron-action-btn" onClick={() => handleAction("Fix all current lint errors and bugs")}>
                <div className="neuron-action-title">Fix Bugs</div>
                <div className="neuron-action-desc">Auto-detect & repair</div>
              </button>
            </div>

            <div className="neuron-secondary-actions">
              <button className="neuron-secondary-btn">
                <Play className="neuron-icon" />
                Replay Last
              </button>
              <button className="neuron-secondary-btn">
                <RotateCcw className="neuron-icon" />
                Undo Last
              </button>
            </div>
          </div>
        </div>

        {/* Activity Timeline */}
        <div className="neuron-card">
          <div className="neuron-timeline-header">
            <h2 className="neuron-card-header" style={{ marginBottom: 0 }}>
              <Activity className="neuron-icon neuron-text-purple" />
              Activity Timeline
            </h2>
            <button className="neuron-view-all">View all →</button>
          </div>

          <div>
            {data.activities.length > 0 ? (
              data.activities.map((activity) => (
                <div key={activity.id} className="neuron-activity-item">
                  <div
                    className="neuron-activity-header"
                    onClick={() => setExpandedActivity(expandedActivity === activity.id ? null : activity.id)}
                  >
                    <div className="neuron-activity-main">
                      <div className="neuron-activity-content">
                        {activity.status === 'success' && <CheckCircle2 className="neuron-icon neuron-text-emerald" />}
                        {activity.status === 'warning' && <AlertCircle className="neuron-icon neuron-text-yellow" />}
                        <div style={{ flex: 1 }}>
                          <div className="neuron-activity-title">{activity.request}</div>
                          <div className="neuron-activity-meta">
                            <span>
                              <FileCode style={{ width: '0.75rem', height: '0.75rem' }} />
                              {activity.filesChanged} files
                            </span>
                            <span>
                              <Clock style={{ width: '0.75rem', height: '0.75rem' }} />
                              {activity.duration}
                            </span>
                            <span>{activity.timestamp}</span>
                          </div>
                        </div>
                      </div>
                      <div style={{ color: '#94a3b8' }}>
                        {expandedActivity === activity.id ?
                          <ChevronDown className="neuron-icon" /> :
                          <ChevronRight className="neuron-icon" />
                        }
                      </div>
                    </div>
                  </div>

                  {expandedActivity === activity.id && (
                    <div className="neuron-activity-details">
                      <div className="neuron-detail-section">
                        <div className="neuron-detail-label">Files Modified</div>
                        <div className="neuron-tag-list">
                          {activity.files.length > 0 ? activity.files.map((file, idx) => (
                            <span key={idx} className="neuron-tag">{file}</span>
                          )) : <span className="text-gray-500 text-xs">No files recorded</span>}
                        </div>
                      </div>

                      <div className="neuron-detail-section">
                        <div className="neuron-detail-label">Agents Involved</div>
                        <div className="neuron-tag-list">
                          {activity.agents.map((agent, idx) => (
                            <span key={idx} className="neuron-tag neuron-agent-tag">{agent}</span>
                          ))}
                        </div>
                      </div>

                      <div className="neuron-detail-section">
                        <div className="neuron-detail-label">Safety Checks</div>
                        <div>
                          {activity.safetyChecks.map((check, idx) => (
                            <div key={idx} className="neuron-check-item">
                              <CheckCircle2 style={{ width: '0.75rem', height: '0.75rem' }} className="neuron-text-emerald" />
                              <span>{check}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500 italic">
                No activity recorded for this project yet
              </div>
            )}
          </div>
        </div>

        {/* Agent Visibility (Collapsible) */}
        <div className="neuron-collapsible">
          <button
            className="neuron-collapsible-header"
            onClick={() => setShowAgents(!showAgents)}
          >
            <h2 className="neuron-card-header" style={{ marginBottom: 0 }}>
              <TrendingUp className="neuron-icon neuron-text-indigo" />
              Agent System
            </h2>
            {showAgents ?
              <ChevronDown className="neuron-icon" /> :
              <ChevronRight className="neuron-icon" />
            }
          </button>

          {showAgents && (
            <div className="neuron-collapsible-content">
              <div className="neuron-agent-grid">
                {data.agents.map((agent, idx) => (
                  <div key={idx} className="neuron-agent-card">
                    <div className="neuron-agent-header">
                      <div
                        className="neuron-agent-status-dot"
                        style={{ background: agent.status === 'active' ? '#10b981' : '#64748b' }}
                      ></div>
                      <span className="neuron-agent-name">{agent.name}</span>
                    </div>
                    <div className="neuron-agent-last-run">{agent.currentAction}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Safety & Control Footer */}
        <div className="neuron-footer">
          <div className="neuron-footer-info">
            <div className="neuron-footer-item">
              Mode:
              <span className="neuron-footer-value">Preview Only</span>
            </div>
            <div className="neuron-footer-item">
              Max files:
              <span className="neuron-footer-value">15 per action</span>
            </div>
            <div className="neuron-footer-item">
              Rollback:
              <span className="neuron-footer-value" style={{ color: '#10b981' }}>Available</span>
            </div>
          </div>
          <button className="neuron-settings-btn">
            <Settings className="neuron-icon" />
            Settings
          </button>
        </div>

      </div>
    </div>
  );
}