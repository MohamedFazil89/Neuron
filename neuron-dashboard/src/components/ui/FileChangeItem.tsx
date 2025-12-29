import { cn } from '@/lib/utils';
import type { FileChange } from '@/types/neuron';
import { FilePlus, FileEdit, FileX, Folder } from 'lucide-react';

interface FileChangeItemProps {
  file: FileChange;
}

const typeIcons = {
  created: FilePlus,
  modified: FileEdit,
  skipped: FileX,
};

const typeColors = {
  created: 'text-primary',
  modified: 'text-chart-3',
  skipped: 'text-muted-foreground',
};

export const FileChangeItem = ({ file }: FileChangeItemProps) => {
  const Icon = typeIcons[file.type];

  return (
    <div className="flex items-center gap-2 py-1.5 px-2 rounded hover:bg-muted/30 font-mono text-xs">
      <Icon className={cn('w-4 h-4', typeColors[file.type])} />
      <span className={cn(typeColors[file.type])}>
        {file.path}
      </span>
      {file.isWorkspace && (
        <span className="flex items-center gap-1 text-xs text-accent ml-auto">
          <Folder className="w-3 h-3" />
          workspace
        </span>
      )}
    </div>
  );
};
