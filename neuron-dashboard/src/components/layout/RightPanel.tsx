import { useNeuron } from '@/context/NeuronContext';
import { AgentCard } from '@/components/agents/AgentCard';
import { MetricsCard } from '@/components/metrics/MetricsCard';
import { Activity, Gauge } from 'lucide-react';

export const RightPanel = () => {
  const { agents, metrics } = useNeuron();

  const workingAgents = agents.filter(a => a.status === 'working').length;
  const totalAgents = agents.length;

  return (
    <aside className="w-80 bg-card border-l border-border flex flex-col overflow-hidden">
      {/* Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-border">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-primary" />
          <span className="font-medium text-sm">Live Activity</span>
        </div>
        <span className="text-xs text-muted-foreground">
          {workingAgents}/{totalAgents} agents active
        </span>
      </div>

      {/* Agent Activity */}
      <div className="flex-1 overflow-auto p-4 space-y-3">
        <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
          Agent Status
        </h3>
        {agents.map(agent => (
          <AgentCard key={agent.id} agent={agent} compact />
        ))}
      </div>

      {/* Metrics Summary */}
      <div className="border-t border-border p-4">
        <div className="flex items-center gap-2 mb-3">
          <Gauge className="w-4 h-4 text-muted-foreground" />
          <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            Usage Metrics
          </span>
        </div>
        <MetricsCard metrics={metrics} compact />
      </div>
    </aside>
  );
};
