import React from 'react';
import UserList from './components/UserList';

const App = () => {
  return (
    <div className='app'>
      <h1>User Management App</h1>
      {/* ADDED: UserList component to display users */}
      <UserList />
    </div>
  );
};

export default App;
