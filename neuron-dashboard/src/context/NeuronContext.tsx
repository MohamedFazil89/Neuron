import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { Agent, Task, Project, LogEntry, UsageMetrics, FileChange } from '@/types/neuron';

interface NeuronContextType {
  agents: Agent[];
  tasks: Task[];
  activeProject: Project | null;
  logs: LogEntry[];
  fileChanges: FileChange[];
  metrics: UsageMetrics;
  setActiveProject: (project: Project) => void;
  toggleAgentEnabled: (agentId: string) => void;
  retryAgent: (agentId: string) => void;
  startTask: () => void;
  pauseTask: () => void;
  abortTask: () => void;
}

const NeuronContext = createContext<NeuronContextType | undefined>(undefined);

export const useNeuron = () => {
  const context = useContext(NeuronContext);
  if (!context) {
    throw new Error('useNeuron must be used within a NeuronProvider');
  }
  return context;
};

// Mock data for demonstration
const mockAgents: Agent[] = [
  { id: '1', name: 'Architect', type: 'architect', status: 'idle', currentAction: 'Awaiting instructions', lastResponseTime: 0, tokenUsage: 0, enabled: true },
  { id: '2', name: 'Backend Agent', type: 'backend', status: 'working', currentAction: 'Generating API endpoints for user authentication', lastResponseTime: 1.2, tokenUsage: 4521, enabled: true },
  { id: '3', name: 'Frontend Agent', type: 'frontend', status: 'waiting', currentAction: 'Waiting for backend schema', lastResponseTime: 0.8, tokenUsage: 2103, enabled: true },
  { id: '4', name: 'Code Reviewer', type: 'reviewer', status: 'idle', currentAction: 'Queue empty', lastResponseTime: 0, tokenUsage: 0, enabled: true },
  { id: '5', name: 'File Patcher', type: 'patcher', status: 'working', currentAction: 'Applying changes to src/api/auth.ts', lastResponseTime: 0.3, tokenUsage: 892, enabled: true },
  { id: '6', name: 'Verifier', type: 'verifier', status: 'idle', currentAction: 'Awaiting patches', lastResponseTime: 0, tokenUsage: 0, enabled: true },
];

const mockProject: Project = {
  id: '1',
  name: 'neuron-core',
  localPath: '/home/dev/projects/neuron-core',
  gitBranch: 'feature/multi-agent',
  workspaceMode: 'safe',
  coreStatus: 'running',
  activeTask: {
    id: 't1',
    name: 'Implement User Authentication',
    description: 'Add JWT-based authentication with refresh tokens',
    status: 'implementing',
    triggerSource: 'ui',
    agents: ['Backend Agent', 'Frontend Agent', 'File Patcher'],
    filesTouched: ['src/api/auth.ts', 'src/components/Login.tsx', 'src/hooks/useAuth.ts'],
    timeElapsed: 127,
    startedAt: new Date(Date.now() - 127000),
  },
  lastActiveAt: new Date(),
};

const mockLogs: LogEntry[] = [
  { id: 'l1', timestamp: new Date(), severity: 'info', agent: 'Backend Agent', message: 'Starting endpoint generation for /api/auth/login' },
  { id: 'l2', timestamp: new Date(Date.now() - 5000), severity: 'info', agent: 'Architect', message: 'Task breakdown complete: 4 subtasks identified' },
  { id: 'l3', timestamp: new Date(Date.now() - 12000), severity: 'warning', agent: 'File Patcher', message: 'File src/api/auth.ts already exists, creating backup' },
  { id: 'l4', timestamp: new Date(Date.now() - 20000), severity: 'info', agent: 'Frontend Agent', message: 'Waiting for backend schema definition' },
  { id: 'l5', timestamp: new Date(Date.now() - 35000), severity: 'error', agent: 'Verifier', message: 'Type check failed: Property "token" missing in type' },
];

const mockFileChanges: FileChange[] = [
  { path: 'src/api/auth.ts', type: 'modified', isWorkspace: true, diff: '+export const login = async...' },
  { path: 'src/components/Login.tsx', type: 'created', isWorkspace: true },
  { path: 'src/hooks/useAuth.ts', type: 'created', isWorkspace: true },
  { path: 'package.json', type: 'skipped', isWorkspace: false },
];

const mockMetrics: UsageMetrics = {
  tokensUsed: 12847,
  apiCalls: 23,
  estimatedCost: 0.38,
  avgTaskTime: 145,
  agentFailureRate: 0.02,
  retryCount: 1,
};

export const NeuronProvider = ({ children }: { children: ReactNode }) => {
  const [agents, setAgents] = useState<Agent[]>(mockAgents);
  const [tasks] = useState<Task[]>(mockProject.activeTask ? [mockProject.activeTask] : []);
  const [activeProject, setActiveProject] = useState<Project | null>(mockProject);
  const [logs] = useState<LogEntry[]>(mockLogs);
  const [fileChanges] = useState<FileChange[]>(mockFileChanges);
  const [metrics] = useState<UsageMetrics>(mockMetrics);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setAgents(prev => prev.map(agent => ({
        ...agent,
        tokenUsage: agent.status === 'working' ? agent.tokenUsage + Math.floor(Math.random() * 50) : agent.tokenUsage,
        lastResponseTime: agent.status === 'working' ? Math.random() * 2 : agent.lastResponseTime,
      })));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const toggleAgentEnabled = (agentId: string) => {
    setAgents(prev => prev.map(agent =>
      agent.id === agentId ? { ...agent, enabled: !agent.enabled } : agent
    ));
  };

  const retryAgent = (agentId: string) => {
    setAgents(prev => prev.map(agent =>
      agent.id === agentId && agent.status === 'failed'
        ? { ...agent, status: 'working', currentAction: 'Retrying...' }
        : agent
    ));
  };

  const startTask = () => {
    // Implementation would trigger task execution
  };

  const pauseTask = () => {
    // Implementation would pause current task
  };

  const abortTask = () => {
    // Implementation would abort current task
  };

  return (
    <NeuronContext.Provider
      value={{
        agents,
        tasks,
        activeProject,
        logs,
        fileChanges,
        metrics,
        setActiveProject,
        toggleAgentEnabled,
        retryAgent,
        startTask,
        pauseTask,
        abortTask,
      }}
    >
      {children}
    </NeuronContext.Provider>
  );
};
