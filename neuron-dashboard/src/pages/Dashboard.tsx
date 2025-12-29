import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { ProjectStatus } from '@/components/project/ProjectStatus';
import { TaskPipeline } from '@/components/pipeline/TaskPipeline';
import { MetricsCard } from '@/components/metrics/MetricsCard';
import { useNeuron } from '@/context/NeuronContext';

const Dashboard = () => {
  const { metrics } = useNeuron();

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Project Status */}
        <ProjectStatus />

        {/* Metrics overview */}
        <MetricsCard metrics={metrics} />

        {/* Task Pipeline */}
        <div>
          <h2 className="text-lg font-semibold mb-4">Task Pipeline</h2>
          <TaskPipeline />
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Dashboard;
