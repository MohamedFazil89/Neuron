import { cn } from '@/lib/utils';
import { useNeuron } from '@/context/NeuronContext';
import { 
  GitBranch, 
  FolderOpen, 
  Shield, 
  Activity,
  Play,
  Pause,
  Square,
  RefreshCw
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

const coreStatusColors = {
  running: 'bg-primary text-primary-foreground',
  idle: 'bg-muted text-muted-foreground',
  error: 'bg-destructive text-destructive-foreground',
};

const coreStatusDot = {
  running: 'bg-primary animate-pulse',
  idle: 'bg-muted-foreground',
  error: 'bg-destructive animate-pulse',
};

export const ProjectStatus = () => {
  const { activeProject, startTask, pauseTask, abortTask } = useNeuron();

  if (!activeProject) {
    return (
      <div className="p-6 rounded-xl border border-dashed border-border bg-muted/20 text-center">
        <p className="text-muted-foreground">No project selected</p>
        <p className="text-sm text-muted-foreground mt-1">Select a project to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Project header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">{activeProject.name}</h1>
            <Badge variant={activeProject.workspaceMode === 'safe' ? 'secondary' : 'destructive'}>
              <Shield className="w-3 h-3 mr-1" />
              {activeProject.workspaceMode} mode
            </Badge>
          </div>
          <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <FolderOpen className="w-4 h-4" />
              {activeProject.localPath}
            </span>
            <span className="flex items-center gap-1.5">
              <GitBranch className="w-4 h-4" />
              {activeProject.gitBranch}
            </span>
          </div>
        </div>

        {/* Core status */}
        <div className={cn(
          'flex items-center gap-2 px-4 py-2 rounded-lg',
          coreStatusColors[activeProject.coreStatus]
        )}>
          <span className={cn('w-2 h-2 rounded-full', coreStatusDot[activeProject.coreStatus])} />
          <Activity className="w-4 h-4" />
          <span className="font-medium capitalize">{activeProject.coreStatus}</span>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-2">
        <Button 
          size="sm" 
          onClick={startTask}
          disabled={activeProject.coreStatus === 'running'}
        >
          <Play className="w-4 h-4 mr-2" />
          Start Task
        </Button>
        <Button 
          variant="secondary" 
          size="sm" 
          onClick={pauseTask}
          disabled={activeProject.coreStatus !== 'running'}
        >
          <Pause className="w-4 h-4 mr-2" />
          Pause
        </Button>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={abortTask}
          disabled={activeProject.coreStatus !== 'running'}
        >
          <Square className="w-4 h-4 mr-2" />
          Abort
        </Button>
        <Button variant="ghost" size="sm">
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry
        </Button>
      </div>
    </div>
  );
};
