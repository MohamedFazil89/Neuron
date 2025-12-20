import React from 'react';
import './QuickActionsPanel.css';

const QuickActionsPanel = () => {
  return (
    <div className="quick-actions-panel">
      <button>Analyze Project</button>
      <button>Build New Feature</button>
      <button>Verify Project</button>
      <button>Open Project Folder</button>
      <button>Copy CLI Command</button>
    </div>
  );
};

export default QuickActionsPanel;
