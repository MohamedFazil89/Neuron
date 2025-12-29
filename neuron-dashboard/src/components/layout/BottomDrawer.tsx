import { ChevronUp, ChevronDown, FileCode, AlertCircle, FileDiff } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useNeuron } from '@/context/NeuronContext';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LogEntry } from '@/components/log/LogEntry';
import { FileChangeItem } from '@/components/files/FileChangeItem';

interface BottomDrawerProps {
  isOpen: boolean;
  onToggle: () => void;
}

export const BottomDrawer = ({ isOpen, onToggle }: BottomDrawerProps) => {
  const { logs, fileChanges } = useNeuron();

  const errorCount = logs.filter(l => l.severity === 'error').length;

  return (
    <div className={cn(
      'border-t border-border bg-card transition-all duration-300',
      isOpen ? 'h-72' : 'h-10'
    )}>
      {/* Toggle bar */}
      <Button
        variant="ghost"
        size="sm"
        className="w-full h-10 rounded-none justify-between px-4 hover:bg-muted/50"
        onClick={onToggle}
      >
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium">Console</span>
          {errorCount > 0 && (
            <span className="flex items-center gap-1 text-xs text-destructive">
              <AlertCircle className="w-3 h-3" />
              {errorCount} error{errorCount > 1 ? 's' : ''}
            </span>
          )}
        </div>
        {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
      </Button>

      {/* Content */}
      {isOpen && (
        <Tabs defaultValue="logs" className="h-[calc(100%-2.5rem)]">
          <TabsList className="h-9 bg-muted/30 rounded-none border-b border-border w-full justify-start px-4">
            <TabsTrigger value="logs" className="text-xs gap-2">
              <FileCode className="w-3 h-3" />
              Logs
            </TabsTrigger>
            <TabsTrigger value="files" className="text-xs gap-2">
              <FileDiff className="w-3 h-3" />
              File Changes
            </TabsTrigger>
            <TabsTrigger value="errors" className="text-xs gap-2">
              <AlertCircle className="w-3 h-3" />
              Errors {errorCount > 0 && `(${errorCount})`}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="logs" className="h-[calc(100%-2.25rem)] m-0 overflow-auto p-2">
            <div className="space-y-1 font-mono text-xs">
              {logs.map(log => (
                <LogEntry key={log.id} log={log} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="files" className="h-[calc(100%-2.25rem)] m-0 overflow-auto p-2">
            <div className="space-y-1">
              {fileChanges.map(file => (
                <FileChangeItem key={file.path} file={file} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="errors" className="h-[calc(100%-2.25rem)] m-0 overflow-auto p-2">
            <div className="space-y-1 font-mono text-xs">
              {logs.filter(l => l.severity === 'error').map(log => (
                <LogEntry key={log.id} log={log} />
              ))}
            </div>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
};
