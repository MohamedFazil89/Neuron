import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { TaskPipeline } from '@/components/pipeline/TaskPipeline';
import { GitBranch } from 'lucide-react';

const Pipeline = () => {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <div className="flex items-center gap-3">
            <GitBranch className="w-6 h-6 text-primary" />
            <h1 className="text-2xl font-bold">Task Pipeline</h1>
          </div>
          <p className="text-muted-foreground mt-1">
            Track feature execution from analysis to completion
          </p>
        </div>

        {/* Pipeline visualization */}
        <TaskPipeline />
      </div>
    </DashboardLayout>
  );
};

export default Pipeline;
