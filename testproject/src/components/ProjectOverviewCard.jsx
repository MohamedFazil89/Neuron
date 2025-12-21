import React from 'react';
import './ProjectOverviewCard.css';

const ProjectOverviewCard = ({ projectName, absolutePath, frameworksDetected, lastAnalyzed }) => {
  return (
    <div className="project-overview-card">
      <h2>{projectName}</h2>
      <p>{absolutePath}</p>
      <p>Frameworks: {frameworksDetected}</p>
      <p>Last Analyzed: {lastAnalyzed}</p>
    </div>
  );
};

export default ProjectOverviewCard;
