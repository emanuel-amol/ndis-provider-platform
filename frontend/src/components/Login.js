import React, { useState } from 'react';
import { Container, Paper, TextField, Button, Typography, Alert } from '@mui/material';
import { authAPI } from '../services/api';
import { setToken } from '../utils/auth';

function Login({ onLogin }) {
  const [email, setEmail] = useState('admin@ndis.com');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await authAPI.login(email, password);
      setToken(response.data.token);
      onLogin(response.data.user);
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" style={{ marginTop: '100px' }}>
      <Paper elevation={3} style={{ padding: '40px' }}>
        <Typography variant="h4" align="center" gutterBottom>
          🏥 NDIS Platform
        </Typography>
        <Typography variant="h6" align="center" color="textSecondary" gutterBottom>
          Staff Login
        </Typography>
        
        {error && <Alert severity="error" style={{ marginBottom: '20px' }}>{error}</Alert>}
        
        <form onSubmit={handleLogin}>
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            margin="normal"
            required
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={loading}
            style={{ marginTop: '20px' }}
          >
            {loading ? 'Logging in...' : 'Login'}
          </Button>
        </form>
        
        <Typography variant="body2" align="center" style={{ marginTop: '20px' }}>
          Demo credentials: admin@ndis.com / admin123
        </Typography>
      </Paper>
    </Container>
  );
}

export default Login;