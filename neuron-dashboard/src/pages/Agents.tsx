import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { AgentGrid } from '@/components/agents/AgentGrid';
import { useNeuron } from '@/context/NeuronContext';
import { Bot } from 'lucide-react';

const Agents = () => {
  const { agents } = useNeuron();
  
  const workingCount = agents.filter(a => a.status === 'working').length;
  const failedCount = agents.filter(a => a.status === 'failed').length;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <Bot className="w-6 h-6 text-primary" />
              <h1 className="text-2xl font-bold">Agents</h1>
            </div>
            <p className="text-muted-foreground mt-1">
              Monitor and control your AI agent fleet
            </p>
          </div>

          <div className="flex items-center gap-4 text-sm">
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              {workingCount} active
            </span>
            {failedCount > 0 && (
              <span className="flex items-center gap-2 text-destructive">
                <span className="w-2 h-2 rounded-full bg-destructive" />
                {failedCount} failed
              </span>
            )}
          </div>
        </div>

        {/* Agent grid */}
        <AgentGrid />
      </div>
    </DashboardLayout>
  );
};

export default Agents;
