import React, { useState } from 'react';
import axios from 'axios';
import { useHistory } from 'react-router-dom';

const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    const response = await axios.post('/campaigns/api/login/', { username, password });

    // Redirect based on role
    if (response.data.role === 'admin') {
      history.push('/admin-dashboard');
    } else if (response.data.role === 'marketing') {
      history.push('/marketing-dashboard');
    }
  } catch (error) {
    console.error('Login failed', error);
  }
};

return(
  <form onSubmit={handleSubmit}>
    <div>
      <label>Username or Email:</label>
      <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
    </div>
    <div>
      <label>Password:</label>
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
    </div>
    <button type="submit">Login</button>
  </form>
);

export default Login;
