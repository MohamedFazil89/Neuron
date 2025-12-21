import React from 'react';
import UserList from './components/UserList';
import Dashboard from "./components/Dashboard"
import FeatureTimeline from "./components/FeatureTimeline"


const App = () => {
  return (
    <div className='app'>
      <h1>User Management App</h1>
      {/* ADDED: UserList component to display users */}
      <Dashboard />

    </div>
  );
};

export default App;
