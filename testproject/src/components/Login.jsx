import React, { useState } from 'react';
import './Login.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (!response.ok) {
        throw new Error('Invalid email or password');
      }
      const data = await response.json();
      localStorage.setItem('token', data.token);
      // Handle successful login (e.g., redirect to dashboard)
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className='login-container'>
      <h2>Login</h2>
      {error && <p className='error'>{error}</p>}
      <form onSubmit={handleSubmit} className='login-form'>
        <input
          type='email'
          placeholder='Email'
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          aria-label='Email'
        />
        <input
          type='password'
          placeholder='Password'
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          aria-label='Password'
        />
        <button type='submit'>Login</button>
      </form>
    </div>
  );
};

export default Login;
