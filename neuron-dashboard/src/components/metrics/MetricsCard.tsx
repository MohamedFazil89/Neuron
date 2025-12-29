import type { UsageMetrics } from '@/types/neuron';
import { Coins, Zap, Clock, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MetricsCardProps {
  metrics: UsageMetrics;
  compact?: boolean;
}

export const MetricsCard = ({ metrics, compact = false }: MetricsCardProps) => {
  const items = [
    { 
      icon: Zap, 
      label: 'Tokens', 
      value: metrics.tokensUsed.toLocaleString(),
      color: 'text-primary'
    },
    { 
      icon: Coins, 
      label: 'Cost', 
      value: `$${metrics.estimatedCost.toFixed(2)}`,
      color: 'text-chart-3'
    },
    { 
      icon: Clock, 
      label: 'Avg Time', 
      value: `${metrics.avgTaskTime}s`,
      color: 'text-chart-4'
    },
    { 
      icon: AlertTriangle, 
      label: 'Failures', 
      value: `${(metrics.agentFailureRate * 100).toFixed(1)}%`,
      color: metrics.agentFailureRate > 0.05 ? 'text-destructive' : 'text-muted-foreground'
    },
  ];

  if (compact) {
    return (
      <div className="grid grid-cols-2 gap-2">
        {items.map(({ icon: Icon, label, value, color }) => (
          <div key={label} className="flex items-center gap-2">
            <Icon className={cn('w-3 h-3', color)} />
            <div>
              <p className="text-xs text-muted-foreground">{label}</p>
              <p className="text-sm font-medium">{value}</p>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {items.map(({ icon: Icon, label, value, color }) => (
        <div key={label} className="p-4 rounded-xl bg-muted/30 border border-border">
          <div className="flex items-center gap-2 mb-2">
            <Icon className={cn('w-4 h-4', color)} />
            <span className="text-xs text-muted-foreground">{label}</span>
          </div>
          <p className="text-xl font-semibold">{value}</p>
        </div>
      ))}
    </div>
  );
};
