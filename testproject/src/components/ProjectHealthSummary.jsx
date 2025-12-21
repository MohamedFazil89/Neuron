import React from 'react';
import './ProjectHealthSummary.css';

const ProjectHealthSummary = ({ health }) => {
  return (
    <div className="project-health-summary">
      <h2>Project Health</h2>
      {/* <p>Status: <span className={health.overallStatus.toLowerCase()}>{health.overallStatus}</span></p> */}
      <ul>
        <li>Missing Config Files: </li>
        <li>Orphan Files:</li>
        <li>Unwired Routes:</li>
        <li>Empty Directories:</li>
      </ul>
    </div>
  );
};

export default ProjectHealthSummary;
