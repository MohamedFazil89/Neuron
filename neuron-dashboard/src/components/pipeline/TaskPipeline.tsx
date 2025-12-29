import { cn } from '@/lib/utils';
import type { Task, TaskStatus } from '@/types/neuron';
import { useNeuron } from '@/context/NeuronContext';
import { 
  Inbox, 
  Search, 
  Code, 
  FileEdit, 
  CheckCircle, 
  XCircle,
  ShieldCheck,
  Clock
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const stages: { status: TaskStatus; label: string; icon: typeof Inbox }[] = [
  { status: 'received', label: 'Received', icon: Inbox },
  { status: 'analyzing', label: 'Analyzing', icon: Search },
  { status: 'implementing', label: 'Implementing', icon: Code },
  { status: 'patching', label: 'Patching', icon: FileEdit },
  { status: 'verifying', label: 'Verifying', icon: ShieldCheck },
  { status: 'completed', label: 'Completed', icon: CheckCircle },
];

const stageIndex = (status: TaskStatus) => {
  if (status === 'failed') return -1;
  return stages.findIndex(s => s.status === status);
};

export const TaskPipeline = () => {
  const { activeProject } = useNeuron();
  const task = activeProject?.activeTask;

  if (!task) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
        <Clock className="w-12 h-12 mb-4 opacity-50" />
        <p className="text-lg font-medium">No active task</p>
        <p className="text-sm">Start a new task to see the pipeline</p>
      </div>
    );
  }

  const currentStage = stageIndex(task.status);
  const isFailed = task.status === 'failed';

  return (
    <div className="space-y-6">
      {/* Task info */}
      <div className="p-4 rounded-xl bg-card border border-border">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-semibold text-lg">{task.name}</h3>
          <Badge variant={isFailed ? 'destructive' : 'secondary'}>
            {task.triggerSource.toUpperCase()}
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground mb-4">{task.description}</p>
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <span>Elapsed: {Math.floor(task.timeElapsed / 60)}m {task.timeElapsed % 60}s</span>
          <span>•</span>
          <span>Files: {task.filesTouched.length}</span>
          <span>•</span>
          <span>Agents: {task.agents.length}</span>
        </div>
      </div>

      {/* Pipeline visualization */}
      <div className="relative">
        <div className="flex items-center justify-between">
          {stages.map((stage, index) => {
            const Icon = stage.icon;
            const isActive = index === currentStage;
            const isCompleted = index < currentStage;
            const isCurrent = isActive && !isFailed;

            return (
              <div key={stage.status} className="flex flex-col items-center relative z-10">
                <div className={cn(
                  'w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all',
                  isCompleted && 'bg-primary border-primary',
                  isCurrent && 'border-primary bg-primary/20 animate-pulse',
                  !isCompleted && !isCurrent && 'border-border bg-muted',
                  isFailed && isActive && 'border-destructive bg-destructive/20'
                )}>
                  {isFailed && isActive ? (
                    <XCircle className="w-6 h-6 text-destructive" />
                  ) : (
                    <Icon className={cn(
                      'w-6 h-6',
                      isCompleted ? 'text-primary-foreground' : 
                      isCurrent ? 'text-primary' : 'text-muted-foreground'
                    )} />
                  )}
                </div>
                <span className={cn(
                  'mt-2 text-xs font-medium',
                  isActive ? 'text-foreground' : 'text-muted-foreground'
                )}>
                  {stage.label}
                </span>
              </div>
            );
          })}
        </div>

        {/* Progress line */}
        <div className="absolute top-6 left-6 right-6 h-0.5 bg-border -z-0">
          <div 
            className={cn(
              'h-full transition-all duration-500',
              isFailed ? 'bg-destructive' : 'bg-primary'
            )}
            style={{ 
              width: `${Math.max(0, (currentStage / (stages.length - 1)) * 100)}%` 
            }}
          />
        </div>
      </div>

      {/* Files touched */}
      <div className="p-4 rounded-xl bg-muted/30 border border-border">
        <h4 className="text-sm font-medium mb-2">Files Touched</h4>
        <div className="flex flex-wrap gap-2">
          {task.filesTouched.map(file => (
            <Badge key={file} variant="outline" className="font-mono text-xs">
              {file}
            </Badge>
          ))}
        </div>
      </div>
    </div>
  );
};
