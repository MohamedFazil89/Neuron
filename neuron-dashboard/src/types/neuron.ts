// Neuron Dashboard Types

export type AgentStatus = 'idle' | 'working' | 'waiting' | 'failed';
export type TaskStatus = 'received' | 'analyzing' | 'implementing' | 'patching' | 'verifying' | 'completed' | 'failed';
export type CoreStatus = 'running' | 'idle' | 'error';
export type WorkspaceMode = 'safe' | 'live';
export type LogSeverity = 'info' | 'warning' | 'error' | 'debug';

export interface Agent {
  id: string;
  name: string;
  type: 'architect' | 'backend' | 'frontend' | 'reviewer' | 'patcher' | 'verifier';
  status: AgentStatus;
  currentAction: string;
  lastResponseTime: number;
  tokenUsage: number;
  enabled: boolean;
}

export interface Task {
  id: string;
  name: string;
  description: string;
  status: TaskStatus;
  triggerSource: 'cli' | 'ui' | 'api';
  agents: string[];
  filesTouched: string[];
  timeElapsed: number;
  startedAt: Date;
  completedAt?: Date;
}

export interface Project {
  id: string;
  name: string;
  localPath: string;
  gitBranch: string;
  workspaceMode: WorkspaceMode;
  coreStatus: CoreStatus;
  activeTask?: Task;
  lastActiveAt: Date;
}

export interface LogEntry {
  id: string;
  timestamp: Date;
  severity: LogSeverity;
  agent?: string;
  message: string;
  context?: Record<string, unknown>;
}

export interface FileChange {
  path: string;
  type: 'created' | 'modified' | 'skipped';
  isWorkspace: boolean;
  diff?: string;
}

export interface UsageMetrics {
  tokensUsed: number;
  apiCalls: number;
  estimatedCost: number;
  avgTaskTime: number;
  agentFailureRate: number;
  retryCount: number;
}

export interface User {
  id: string;
  email: string;
  lastActiveProjectId?: string;
}
