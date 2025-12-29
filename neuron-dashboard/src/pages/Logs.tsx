import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { LogEntry } from '@/components/log/LogEntry';
import { useNeuron } from '@/context/NeuronContext';
import { ScrollText, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { LogSeverity } from '@/types/neuron';

const Logs = () => {
  const { logs } = useNeuron();
  const [filter, setFilter] = useState<LogSeverity | 'all'>('all');

  const filteredLogs = filter === 'all' 
    ? logs 
    : logs.filter(l => l.severity === filter);

  const severities: (LogSeverity | 'all')[] = ['all', 'info', 'warning', 'error', 'debug'];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <ScrollText className="w-6 h-6 text-primary" />
              <h1 className="text-2xl font-bold">Logs</h1>
            </div>
            <p className="text-muted-foreground mt-1">
              View structured logs from all agents
            </p>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-muted-foreground" />
            {severities.map(sev => (
              <Button
                key={sev}
                variant={filter === sev ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setFilter(sev)}
                className="capitalize"
              >
                {sev}
                {sev !== 'all' && (
                  <Badge variant="outline" className="ml-2 text-xs">
                    {logs.filter(l => l.severity === sev).length}
                  </Badge>
                )}
              </Button>
            ))}
          </div>
        </div>

        {/* Logs list */}
        <div className="p-4 rounded-xl bg-card border border-border font-mono text-sm">
          {filteredLogs.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No logs to display</p>
          ) : (
            <div className="space-y-1">
              {filteredLogs.map(log => (
                <LogEntry key={log.id} log={log} />
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Logs;
