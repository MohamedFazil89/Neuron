import React from 'react';
import './FeatureTimeline.css';

const FeatureTimeline = ({ features }) => {
  return (
    <div className="feature-timeline">
      <h2>Feature Timeline</h2>
      <ul>
        {features.map((feature, index) => (
          <li key={index}>
            {feature.description} - {feature.filesChangedCount} files changed - {feature.timestamp}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FeatureTimeline;
