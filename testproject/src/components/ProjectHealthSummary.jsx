import React from 'react';
import './ProjectHealthSummary.css';

const ProjectHealthSummary = ({ health }) => {
  return (
    <div className="project-health-summary">
      <h2>Project Health</h2>
      <p>Status: <span className={health.overallStatus.toLowerCase()}>{health.overallStatus}</span></p>
      <ul>
        <li>Missing Config Files: {health.metrics.missingConfigFiles}</li>
        <li>Orphan Files: {health.metrics.orphanFiles}</li>
        <li>Unwired Routes: {health.metrics.unwiredRoutes}</li>
        <li>Empty Directories: {health.metrics.emptyDirectories}</li>
      </ul>
    </div>
  );
};

export default ProjectHealthSummary;
