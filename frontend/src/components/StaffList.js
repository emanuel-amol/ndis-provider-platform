import React, { useState, useEffect } from 'react';
import {
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import { staffAPI } from '../services/api';

function StaffList() {
  const [staff, setStaff] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadStaff();
  }, []);

  const loadStaff = async () => {
    try {
      const response = await staffAPI.getAll();
      setStaff(response.data.staff);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load staff');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'error';
      case 'on_leave': return 'warning';
      default: return 'default';
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        👥 Staff Members
      </Typography>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Phone</TableCell>
              <TableCell>Position</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Hire Date</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {staff.map((member) => (
              <TableRow key={member.id}>
                <TableCell>{member.first_name} {member.last_name}</TableCell>
                <TableCell>{member.email}</TableCell>
                <TableCell>{member.phone || 'N/A'}</TableCell>
                <TableCell>{member.position || 'N/A'}</TableCell>
                <TableCell>
                  <Chip 
                    label={member.status} 
                    color={getStatusColor(member.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {member.hire_date ? new Date(member.hire_date).toLocaleDateString() : 'N/A'}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      
      {staff.length === 0 && (
        <Alert severity="info" style={{ marginTop: '20px' }}>
          No staff members found. Add some staff to get started!
        </Alert>
      )}
    </div>
  );
}

export default StaffList;