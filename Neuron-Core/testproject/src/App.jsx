import React from 'react';
import LoginForm from './components/LoginForm';

const App = () => {
  return (
    <div>
      <h1>Welcome to the App</h1>
      <LoginForm /> {/* ADDED: Login form integration */}
    </div>
  );
};

export default App;