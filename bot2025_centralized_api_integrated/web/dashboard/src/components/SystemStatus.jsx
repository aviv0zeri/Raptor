import React, { Component } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert,
  CircularProgress,
  Button,
  Divider,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  Info,
  Refresh,
  Speed,
  Memory,
  Storage,
  NetworkCheck,
  Security,
  Timeline,
  AccountBalance,
  ShowChart,
  BugReport,
} from '@mui/icons-material';

class SystemStatus extends Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: true,
      systemStatus: {
        overall: 'offline',
        components: {
          model: { status: 'offline', lastUpdate: null, performance: 0 },
          main: { status: 'offline', lastUpdate: null, performance: 0 },
          database: { status: 'offline', lastUpdate: null, performance: 0 },
          api: { status: 'offline', lastUpdate: null, performance: 0 },
          web: { status: 'offline', lastUpdate: null, performance: 0 },
        },
        resources: {
          cpu: 0,
          memory: 0,
          disk: 0,
          network: 0,
        },
        alerts: [],
      },
      error: null,
    };
  }

  componentDidMount() {
    this.loadSystemStatus();
    this.interval = setInterval(this.loadSystemStatus, 5000);
  }

  componentWillUnmount() {
    if (this.interval) {
      clearInterval(this.interval);
    }
  }

  loadSystemStatus = async () => {
    try {
      this.setState({ loading: true, error: null });
      
      // Simulate API call - replace with actual endpoint
      const status = await this.fetchSystemStatus();
      
      this.setState({ systemStatus: status, loading: false });
    } catch (error) {
      this.setState({
        error: 'Failed to load system status',
        loading: false,
      });
    }
  };

  fetchSystemStatus = async () => {
    // Simulate API call - replace with actual endpoint
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          overall: Math.random() > 0.3 ? 'online' : 'offline',
          components: {
            model: {
              status: Math.random() > 0.2 ? 'online' : 'offline',
              lastUpdate: new Date(Date.now() - Math.random() * 60000),
              performance: Math.random() * 100,
            },
            main: {
              status: Math.random() > 0.2 ? 'online' : 'offline',
              lastUpdate: new Date(Date.now() - Math.random() * 60000),
              performance: Math.random() * 100,
            },
            database: {
              status: Math.random() > 0.1 ? 'online' : 'offline',
              lastUpdate: new Date(Date.now() - Math.random() * 60000),
              performance: Math.random() * 100,
            },
            api: {
              status: Math.random() > 0.15 ? 'online' : 'offline',
              lastUpdate: new Date(Date.now() - Math.random() * 60000),
              performance: Math.random() * 100,
            },
            web: {
              status: 'online',
              lastUpdate: new Date(),
              performance: 95,
            },
          },
          resources: {
            cpu: Math.random() * 100,
            memory: Math.random() * 100,
            disk: Math.random() * 100,
            network: Math.random() * 100,
          },
          alerts: [
            {
              id: 1,
              level: 'warning',
              message: 'High memory usage detected',
              timestamp: new Date(Date.now() - 300000),
            },
            {
              id: 2,
              level: 'info',
              message: 'Database backup completed',
              timestamp: new Date(Date.now() - 1800000),
            },
          ],
        });
      }, 500);
    });
  };

  getStatusColor = (status) => {
    switch (status) {
      case 'online':
        return 'success';
      case 'offline':
        return 'error';
      case 'warning':
        return 'warning';
      default:
        return 'default';
    }
  };

  getStatusIcon = (status) => {
    switch (status) {
      case 'online':
        return <CheckCircle />;
      case 'offline':
        return <Error />;
      case 'warning':
        return <Warning />;
      default:
        return <Info />;
    }
  };

  getAlertColor = (level) => {
    switch (level) {
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Never';
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return timestamp.toLocaleString();
  };

  render() {
    const { loading, systemStatus, error } = this.state;
    const { overall, components, resources, alerts } = systemStatus;

    if (loading) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      );
    }

    return (
      <Box>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
            📊 System Status
          </Typography>
          <Box display="flex" gap={2}>
            <Chip
              icon={this.getStatusIcon(overall)}
              label={overall.toUpperCase()}
              color={this.getStatusColor(overall)}
            />
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={this.loadSystemStatus}
            >
              Refresh
            </Button>
          </Box>
        </Box>

        <Grid container spacing={3}>
          {/* Component Status */}
          <Grid item xs={12} lg={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  🔧 Component Status
                </Typography>
                <Grid container spacing={2}>
                  {Object.entries(components).map(([name, component]) => (
                    <Grid item xs={12} sm={6} key={name}>
                      <Box
                        sx={{
                          p: 2,
                          border: '1px solid',
                          borderColor: 'divider',
                          borderRadius: 1,
                        }}
                      >
                        <Box display="flex" alignItems="center" gap={1} mb={1}>
                          <Chip
                            icon={this.getStatusIcon(component.status)}
                            label={component.status.toUpperCase()}
                            color={this.getStatusColor(component.status)}
                            size="small"
                          />
                          <Typography variant="body2" color="textSecondary">
                            {name.charAt(0).toUpperCase() + name.slice(1)}
                          </Typography>
                        </Box>
                        <Typography variant="caption" color="textSecondary">
                          Last update: {this.formatTimestamp(component.lastUpdate)}
                        </Typography>
                        <Box mt={1}>
                          <Typography variant="caption" color="textSecondary">
                            Performance: {component.performance.toFixed(1)}%
                          </Typography>
                          <LinearProgress
                            variant="determinate"
                            value={component.performance}
                            sx={{ mt: 0.5 }}
                          />
                        </Box>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Resource Usage */}
          <Grid item xs={12} lg={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📈 Resource Usage
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Box textAlign="center">
                      <Speed color="primary" sx={{ fontSize: 40 }} />
                      <Typography variant="h6">{resources.cpu.toFixed(1)}%</Typography>
                      <Typography variant="body2" color="textSecondary">CPU</Typography>
                      <LinearProgress
                        variant="determinate"
                        value={resources.cpu}
                        sx={{ mt: 1 }}
                      />
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box textAlign="center">
                      <Memory color="primary" sx={{ fontSize: 40 }} />
                      <Typography variant="h6">{resources.memory.toFixed(1)}%</Typography>
                      <Typography variant="body2" color="textSecondary">Memory</Typography>
                      <LinearProgress
                        variant="determinate"
                        value={resources.memory}
                        sx={{ mt: 1 }}
                      />
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box textAlign="center">
                      <Storage color="primary" sx={{ fontSize: 40 }} />
                      <Typography variant="h6">{resources.disk.toFixed(1)}%</Typography>
                      <Typography variant="body2" color="textSecondary">Disk</Typography>
                      <LinearProgress
                        variant="determinate"
                        value={resources.disk}
                        sx={{ mt: 1 }}
                      />
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box textAlign="center">
                      <NetworkCheck color="primary" sx={{ fontSize: 40 }} />
                      <Typography variant="h6">{resources.network.toFixed(1)}%</Typography>
                      <Typography variant="body2" color="textSecondary">Network</Typography>
                      <LinearProgress
                        variant="determinate"
                        value={resources.network}
                        sx={{ mt: 1 }}
                      />
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* System Alerts */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  🚨 System Alerts
                </Typography>
                {alerts.length === 0 ? (
                  <Box textAlign="center" py={2}>
                    <Typography color="textSecondary">
                      No active alerts
                    </Typography>
                  </Box>
                ) : (
                  <List>
                    {alerts.map((alert, index) => (
                      <React.Fragment key={alert.id}>
                        <ListItem>
                          <ListItemIcon>
                            <Chip
                              icon={this.getStatusIcon(alert.level)}
                              label={alert.level.toUpperCase()}
                              color={this.getAlertColor(alert.level)}
                              size="small"
                            />
                          </ListItemIcon>
                          <ListItemText
                            primary={alert.message}
                            secondary={this.formatTimestamp(alert.timestamp)}
                          />
                        </ListItem>
                        {index < alerts.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Quick Actions */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  ⚡ Quick Actions
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<AccountBalance />}
                      onClick={() => console.log('Check balance')}
                    >
                      Check Balance
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<ShowChart />}
                      onClick={() => console.log('View positions')}
                    >
                      View Positions
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<BugReport />}
                      onClick={() => console.log('Run diagnostics')}
                    >
                      Run Diagnostics
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<Security />}
                      onClick={() => console.log('Security check')}
                    >
                      Security Check
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  }
}

export default SystemStatus;
