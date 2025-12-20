import React, { useState } from 'react';
import axios from 'axios';
import '../styles/ResponsiveStyles.css'

const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await axios.post('/api/login', { username: email, password }); // ADDED: changed email to username
      localStorage.setItem('token', response.data.token); // Store JWT token
      // Redirect to dashboard or home page
      window.location.href = '/dashboard';
    } catch (err) {
      if (err.response && err.response.status === 401) {
        setError('Invalid email or password'); // Display error message
      } else {
        setError('An error occurred. Please try again.');
      }
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Email:</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Password:</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      <button type="submit">Login</button>
      {error && <p>{error}</p>} {/* ADDED: error message display */}
    </form>
  );
};

export default LoginForm;