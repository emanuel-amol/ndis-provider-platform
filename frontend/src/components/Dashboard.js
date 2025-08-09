import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container,
  Grid,
  Card,
  CardContent,
  CardActions,
} from '@mui/material';
import { removeToken } from '../utils/auth';
import StaffList from './StaffList';
import AddStaff from './AddStaff';

function Dashboard({ user, onLogout }) {
  const [currentView, setCurrentView] = useState('overview');

  const handleLogout = () => {
    removeToken();
    onLogout();
  };

  const renderContent = () => {
    switch (currentView) {
      case 'staff':
        return <StaffList />;
      case 'add-staff':
        return <AddStaff onSuccess={() => setCurrentView('staff')} />;
      default:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h5" component="h2">
                    👥 Staff Management
                  </Typography>
                  <Typography color="textSecondary">
                    Manage NDIS staff members, roles, and permissions
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small" onClick={() => setCurrentView('staff')}>
                    View Staff
                  </Button>
                  <Button size="small" onClick={() => setCurrentView('add-staff')}>
                    Add Staff
                  </Button>
                </CardActions>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h5" component="h2">
                    🏠 Participants
                  </Typography>
                  <Typography color="textSecondary">
                    Manage NDIS participants and their support plans
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small">View Participants</Button>
                  <Button size="small">Add Participant</Button>
                </CardActions>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h5" component="h2">
                    📅 Scheduling
                  </Typography>
                  <Typography color="textSecondary">
                    Manage shifts, appointments, and staff rosters
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small">View Schedule</Button>
                  <Button size="small">Create Shift</Button>
                </CardActions>
              </Card>
            </Grid>
          </Grid>
        );
    }
  };

  return (
    <div>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" style={{ flexGrow: 1 }}>
            🏥 NDIS Platform - Welcome, {user.email}
          </Typography>
          <Button color="inherit" onClick={() => setCurrentView('overview')}>
            Dashboard
          </Button>
          <Button color="inherit" onClick={() => setCurrentView('staff')}>
            Staff
          </Button>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>
      
      <Container style={{ marginTop: '20px' }}>
        {renderContent()}
      </Container>
    </div>
  );
}

export default Dashboard;