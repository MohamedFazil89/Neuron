import React, { useState } from 'react';
import { Activity, AlertCircle, CheckCircle2, Clock, Code, Zap, ChevronDown, ChevronRight, Play, RotateCcw, GitBranch, FileCode, Settings, TrendingUp } from 'lucide-react';
import './App.css'; // Make sure you import the CSS file

export default function NeuronDashboard() {
  const [expandedActivity, setExpandedActivity] = useState(null);
  const [showAgents, setShowAgents] = useState(false);

  const activities = [
    {
      id: 1,
      request: "Add user authentication to API",
      status: "success",
      filesChanged: 8,
      duration: "2m 34s",
      timestamp: "2 minutes ago",
      agents: ["Architect", "Builder", "Auditor"],
      files: ["auth.js", "middleware/auth.js", "routes/user.js"],
      safetyChecks: ["No secrets exposed", "Tests passed", "Backward compatible"]
    },
    {
      id: 2,
      request: "Fix database connection pooling issue",
      status: "success",
      filesChanged: 3,
      duration: "1m 12s",
      timestamp: "15 minutes ago",
      agents: ["Patcher", "Auditor"],
      files: ["db/config.js", "db/pool.js"],
      safetyChecks: ["Performance improved 40%", "No breaking changes"]
    },
    {
      id: 3,
      request: "Build admin dashboard component",
      status: "warning",
      filesChanged: 12,
      duration: "4m 01s",
      timestamp: "1 hour ago",
      agents: ["Architect", "Builder"],
      files: ["components/AdminDash.jsx", "styles/admin.css"],
      safetyChecks: ["Manual review suggested", "Large component created"]
    }
  ];

  const agents = [
    { name: "Orchestrator", status: "active", lastRun: "2 min ago" },
    { name: "Architect", status: "idle", lastRun: "2 min ago" },
    { name: "Builder", status: "idle", lastRun: "2 min ago" },
    { name: "Auditor", status: "active", lastRun: "2 min ago" },
    { name: "Patcher", status: "idle", lastRun: "15 min ago" }
  ];

  return (
    <div className="neuron-dashboard">
      <div className="neuron-container neuron-space-y-6">
        
        {/* Header with System Status */}
        <div className="neuron-header">
          <div>
            <h1>Neuron</h1>
            <p className="neuron-subtitle">TaskMaster Pro</p>
          </div>
          
          <div className="neuron-status-cards">
            <div className="neuron-status-card">
              <div className="neuron-status-indicator">
                <div className="neuron-pulse-dot"></div>
                <span className="neuron-status-label">Engine Online</span>
              </div>
              <div className="neuron-status-sublabel">Standard Engine</div>
            </div>
            
            <div className="neuron-status-card">
              <div className="neuron-status-sublabel">Last action</div>
              <div className="neuron-status-label">2 minutes ago</div>
            </div>
          </div>
        </div>

        {/* Usage & Upgrade */}
        <div className="neuron-usage-card">
          <div className="neuron-usage-header">
            <div>
              <div className="neuron-usage-stats">47 / 100 actions</div>
              <div className="neuron-usage-details">Free Plan · Resets in 12 days</div>
            </div>
            <button className="neuron-upgrade-btn">Upgrade Plan</button>
          </div>
          
          <div className="neuron-progress-bar">
            <div className="neuron-progress-fill" style={{width: '47%'}}></div>
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
                <div className="neuron-context-label">Project</div>
                <div className="neuron-context-value">TaskMaster Pro</div>
                <div className="neuron-context-path">/home/user/projects/taskmaster</div>
              </div>
              
              <div>
                <div className="neuron-context-label">Tech Stack</div>
                <div style={{marginTop: '0.5rem'}} className="neuron-space-y-1">
                  <div className="neuron-tech-stack-item">
                    <div className="neuron-tech-dot neuron-bg-cyan"></div>
                    React + Tailwind
                  </div>
                  <div className="neuron-tech-stack-item">
                    <div className="neuron-tech-dot neuron-bg-green"></div>
                    Node.js + Express
                  </div>
                  <div className="neuron-tech-stack-item">
                    <div className="neuron-tech-dot neuron-bg-orange"></div>
                    PostgreSQL
                  </div>
                </div>
              </div>
              
              <div className="neuron-divider">
                <div className="neuron-health-indicator">
                  <CheckCircle2 className="neuron-icon neuron-text-emerald" />
                  <span className="neuron-health-text">Low Risk</span>
                </div>
                <div className="neuron-health-subtext">Project health is good</div>
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
              <button className="neuron-action-btn">
                <div className="neuron-action-title">Build Project</div>
                <div className="neuron-action-desc">Create new features</div>
              </button>
              
              <button className="neuron-action-btn">
                <div className="neuron-action-title">Add Feature</div>
                <div className="neuron-action-desc">Extend functionality</div>
              </button>
              
              <button className="neuron-action-btn">
                <div className="neuron-action-title">Analyze Project</div>
                <div className="neuron-action-desc">Find issues & improvements</div>
              </button>
              
              <button className="neuron-action-btn">
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
            <h2 className="neuron-card-header" style={{marginBottom: 0}}>
              <Activity className="neuron-icon neuron-text-purple" />
              Activity Timeline
            </h2>
            <button className="neuron-view-all">View all →</button>
          </div>
          
          <div>
            {activities.map((activity) => (
              <div key={activity.id} className="neuron-activity-item">
                <div 
                  className="neuron-activity-header"
                  onClick={() => setExpandedActivity(expandedActivity === activity.id ? null : activity.id)}
                >
                  <div className="neuron-activity-main">
                    <div className="neuron-activity-content">
                      {activity.status === 'success' && <CheckCircle2 className="neuron-icon neuron-text-emerald" />}
                      {activity.status === 'warning' && <AlertCircle className="neuron-icon neuron-text-yellow" />}
                      <div style={{flex: 1}}>
                        <div className="neuron-activity-title">{activity.request}</div>
                        <div className="neuron-activity-meta">
                          <span>
                            <FileCode style={{width: '0.75rem', height: '0.75rem'}} />
                            {activity.filesChanged} files
                          </span>
                          <span>
                            <Clock style={{width: '0.75rem', height: '0.75rem'}} />
                            {activity.duration}
                          </span>
                          <span>{activity.timestamp}</span>
                        </div>
                      </div>
                    </div>
                    <div style={{color: '#94a3b8'}}>
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
                        {activity.files.map((file, idx) => (
                          <span key={idx} className="neuron-tag">{file}</span>
                        ))}
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
                            <CheckCircle2 style={{width: '0.75rem', height: '0.75rem'}} className="neuron-text-emerald" />
                            <span>{check}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div className="neuron-detail-actions">
                      <button className="neuron-detail-btn">
                        <GitBranch style={{width: '0.75rem', height: '0.75rem'}} />
                        View Diff
                      </button>
                      <button className="neuron-detail-btn">
                        <Play style={{width: '0.75rem', height: '0.75rem'}} />
                        Replay Action
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Agent Visibility (Collapsible) */}
        <div className="neuron-collapsible">
          <button 
            className="neuron-collapsible-header"
            onClick={() => setShowAgents(!showAgents)}
          >
            <h2 className="neuron-card-header" style={{marginBottom: 0}}>
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
                {agents.map((agent, idx) => (
                  <div key={idx} className="neuron-agent-card">
                    <div className="neuron-agent-header">
                      <div 
                        className="neuron-agent-status-dot" 
                        style={{background: agent.status === 'active' ? '#10b981' : '#64748b'}}
                      ></div>
                      <span className="neuron-agent-name">{agent.name}</span>
                    </div>
                    <div className="neuron-agent-last-run">Last: {agent.lastRun}</div>
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
              <span className="neuron-footer-value" style={{color: '#10b981'}}>Available</span>
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