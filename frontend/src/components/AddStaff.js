import React, { useState } from 'react';
import {
  Typography,
  TextField,
  Button,
  Paper,
  Grid,
  Alert,
  MenuItem,
} from '@mui/material';
import { staffAPI } from '../services/api';

function AddStaff({ onSuccess }) {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    phone: '',
    position: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const positions = [
    'Support Worker',
    'Coordinator',
    'Manager',
    'Admin',
    'Therapist',
    'Nurse',
  ];

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await staffAPI.create(formData);
      setSuccess('Staff member created successfully! Automation workflows triggered.');
      setFormData({
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        phone: '',
        position: '',
      });
      
      // Redirect to staff list after 2 seconds
      setTimeout(() => {
        onSuccess();
      }, 2000);
      
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create staff member');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        ➕ Add New Staff Member
      </Typography>
      
      <Paper style={{ padding: '30px', marginTop: '20px' }}>
        {error && <Alert severity="error" style={{ marginBottom: '20px' }}>{error}</Alert>}
        {success && <Alert severity="success" style={{ marginBottom: '20px' }}>{success}</Alert>}
        
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="First Name"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Last Name"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Phone"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                select
                label="Position"
                name="position"
                value={formData.position}
                onChange={handleChange}
              >
                {positions.map((position) => (
                  <MenuItem key={position} value={position}>
                    {position}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            
            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                disabled={loading}
                style={{ marginRight: '10px' }}
              >
                {loading ? 'Creating...' : 'Create Staff Member'}
              </Button>
              
              <Button
                variant="outlined"
                size="large"
                onClick={onSuccess}
              >
                Cancel
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </div>
  );
}

export default AddStaff;