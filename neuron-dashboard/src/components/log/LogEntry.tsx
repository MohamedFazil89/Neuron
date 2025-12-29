import { cn } from '@/lib/utils';
import type { LogEntry as LogEntryType } from '@/types/neuron';
import { format } from 'date-fns';

interface LogEntryProps {
  log: LogEntryType;
}

const severityColors: Record<string, string> = {
  info: 'text-muted-foreground',
  debug: 'text-chart-4',
  warning: 'text-chart-3',
  error: 'text-destructive',
};

const severityBadgeColors: Record<string, string> = {
  info: 'bg-muted text-muted-foreground',
  debug: 'bg-chart-4/20 text-chart-4',
  warning: 'bg-chart-3/20 text-chart-3',
  error: 'bg-destructive/20 text-destructive',
};

export const LogEntry = ({ log }: LogEntryProps) => {
  return (
    <div className={cn(
      'flex items-start gap-2 py-1.5 px-2 rounded hover:bg-muted/30',
      log.severity === 'error' && 'bg-destructive/5'
    )}>
      <span className="text-muted-foreground shrink-0">
        {format(log.timestamp, 'HH:mm:ss')}
      </span>
      <span className={cn(
        'px-1.5 py-0.5 rounded text-xs shrink-0',
        severityBadgeColors[log.severity]
      )}>
        {log.severity.toUpperCase()}
      </span>
      {log.agent && (
        <span className="text-primary shrink-0">[{log.agent}]</span>
      )}
      <span className={cn(severityColors[log.severity])}>
        {log.message}
      </span>
    </div>
  );
};
