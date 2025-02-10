import React, { useState } from 'react';
import axios from 'axios';
import { useHistory } from 'react-router-dom';

const Login = ({ setToken }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const history = useHistory();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/campaigns/api/token/', { username, password });
      setToken(response.data.access);

      // Fetch user profile to get the role
      const userProfile = await axios.get('/campaigns/api/user-profile/', {
        headers: {
          Authorization: `Bearer ${response.data.access}`,
        },
      });

      // Redirect based on role
      if (userProfile.data.role === 'admin') {
        history.push('/admin-dashboard');
      } else if (userProfile.data.role === 'marketing') {
        history.push('/marketing-dashboard');
      }
    } catch (error) {
      console.error('Login failed', error);
    }
  };

  return (
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
};

export default Login;