import { cn } from '@/lib/utils';
import type { Agent } from '@/types/neuron';
import { RefreshCw, Power, Bot, Code, Palette, Eye, Wrench, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useNeuron } from '@/context/NeuronContext';

interface AgentCardProps {
  agent: Agent;
  compact?: boolean;
}

const agentIcons = {
  architect: Bot,
  backend: Code,
  frontend: Palette,
  reviewer: Eye,
  patcher: Wrench,
  verifier: CheckCircle,
};

const statusColors = {
  idle: 'bg-muted-foreground/20 text-muted-foreground',
  working: 'bg-primary/20 text-primary',
  waiting: 'bg-accent/20 text-accent',
  failed: 'bg-destructive/20 text-destructive',
};

const statusDotColors = {
  idle: 'bg-muted-foreground',
  working: 'bg-primary animate-pulse',
  waiting: 'bg-accent',
  failed: 'bg-destructive',
};

export const AgentCard = ({ agent, compact = false }: AgentCardProps) => {
  const { toggleAgentEnabled, retryAgent } = useNeuron();
  const Icon = agentIcons[agent.type];

  if (compact) {
    return (
      <div className={cn(
        'flex items-center gap-3 p-2 rounded-lg',
        agent.status === 'failed' && 'bg-destructive/10 border border-destructive/30'
      )}>
        <div className={cn('w-2 h-2 rounded-full', statusDotColors[agent.status])} />
        <Icon className="w-4 h-4 text-muted-foreground" />
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium truncate">{agent.name}</p>
          <p className="text-xs text-muted-foreground truncate">{agent.currentAction}</p>
        </div>
        {agent.status === 'working' && (
          <span className="text-xs text-muted-foreground">{agent.lastResponseTime.toFixed(1)}s</span>
        )}
      </div>
    );
  }

  return (
    <div className={cn(
      'p-4 rounded-xl border bg-card transition-all',
      agent.status === 'failed' 
        ? 'border-destructive/50 bg-destructive/5' 
        : 'border-border hover:border-primary/30'
    )}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={cn(
            'w-10 h-10 rounded-lg flex items-center justify-center',
            statusColors[agent.status]
          )}>
            <Icon className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-medium">{agent.name}</h3>
            <div className="flex items-center gap-2">
              <span className={cn('w-2 h-2 rounded-full', statusDotColors[agent.status])} />
              <span className="text-xs text-muted-foreground capitalize">{agent.status}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1">
          {agent.status === 'failed' && (
            <Button 
              variant="ghost" 
              size="icon" 
              className="h-8 w-8"
              onClick={() => retryAgent(agent.id)}
            >
              <RefreshCw className="w-4 h-4" />
            </Button>
          )}
          <Button 
            variant="ghost" 
            size="icon" 
            className={cn('h-8 w-8', !agent.enabled && 'text-muted-foreground')}
            onClick={() => toggleAgentEnabled(agent.id)}
          >
            <Power className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
        {agent.currentAction}
      </p>

      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>Response: {agent.lastResponseTime.toFixed(1)}s</span>
        <span>Tokens: {agent.tokenUsage.toLocaleString()}</span>
      </div>
    </div>
  );
};
