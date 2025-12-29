import { useNeuron } from '@/context/NeuronContext';
import { AgentCard } from './AgentCard';

export const AgentGrid = () => {
  const { agents } = useNeuron();

  // Sort to show failed agents first
  const sortedAgents = [...agents].sort((a, b) => {
    if (a.status === 'failed' && b.status !== 'failed') return -1;
    if (b.status === 'failed' && a.status !== 'failed') return 1;
    return 0;
  });

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {sortedAgents.map(agent => (
        <AgentCard key={agent.id} agent={agent} />
      ))}
    </div>
  );
};
