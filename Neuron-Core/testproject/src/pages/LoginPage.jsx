import React from 'react';
import LoginForm from '../components/LoginForm';

const LoginPage = () => {
  return (
    <div>
      <h1>Login</h1>
      <LoginForm /> {/* ADDED: LoginForm component */}
    </div>
  );
};

export default LoginPage;