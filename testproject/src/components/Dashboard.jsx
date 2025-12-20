import React from 'react';
import ProjectOverviewCard from './ProjectOverviewCard';
import ProjectHealthSummary from './ProjectHealthSummary';
import FeatureTimeline from './FeatureTimeline';
import QuickActionsPanel from './QuickActionsPanel';
import './Dashboard.css';

const Dashboard = () => {
  return (
    <div className="dashboard">
      <aside className="sidebar">
        {/* Sidebar content here */}
      </aside>
      <main className="main-content">
        <ProjectOverviewCard />
        <ProjectHealthSummary />
        <FeatureTimeline />
        <QuickActionsPanel />
      </main>
    </div>
  );
};

export default Dashboard;
