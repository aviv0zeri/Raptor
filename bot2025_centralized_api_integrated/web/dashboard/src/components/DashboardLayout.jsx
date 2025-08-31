import React, { Component } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Chip,
  Avatar,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Assessment as AssessmentIcon,
  BugReport as BugReportIcon,
  Settings as SettingsIcon,
  Timeline as TimelineIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { Link, useLocation } from 'react-router-dom';

const drawerWidth = 240;

class DashboardLayout extends Component {
  constructor(props) {
    super(props);
    this.state = {
      mobileOpen: false,
      systemStatus: 'offline',
      lastUpdate: new Date(),
    };
  }

  componentDidMount() {
    this.checkSystemStatus();
    this.interval = setInterval(this.checkSystemStatus, 5000);
  }

  componentWillUnmount() {
    if (this.interval) {
      clearInterval(this.interval);
    }
  }

  checkSystemStatus = async () => {
    try {
      const response = await fetch('/api/status');
      if (response.ok) {
        this.setState({ systemStatus: 'online' });
      } else {
        this.setState({ systemStatus: 'offline' });
      }
    } catch (error) {
      this.setState({ systemStatus: 'offline' });
    }
    this.setState({ lastUpdate: new Date() });
  };

  handleDrawerToggle = () => {
    this.setState(prevState => ({ mobileOpen: !prevState.mobileOpen }));
  };

  getStatusColor = () => {
    switch (this.state.systemStatus) {
      case 'online':
        return 'success';
      case 'offline':
        return 'error';
      default:
        return 'warning';
    }
  };

  render() {
    const { children } = this.props;
    const { mobileOpen, systemStatus, lastUpdate } = this.state;

    const menuItems = [
      { text: 'Trading Dashboard', icon: <DashboardIcon />, path: '/' },
      { text: 'System Status', icon: <AssessmentIcon />, path: '/status' },
      { text: 'Logs Viewer', icon: <TimelineIcon />, path: '/logs' },
      { text: 'Test Runner', icon: <BugReportIcon />, path: '/tests' },
      { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
    ];

    const drawer = (
      <div>
        <Toolbar>
          <Typography variant="h6" noWrap component="div" sx={{ color: 'primary.main' }}>
            🌟 Cosmic Bot
          </Typography>
        </Toolbar>
        <Divider />
        <List>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton component={Link} to={item.path}>
                <ListItemIcon sx={{ color: 'primary.main' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
        <Divider />
        <Box sx={{ p: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            System Status
          </Typography>
          <Chip
            label={systemStatus.toUpperCase()}
            color={this.getStatusColor()}
            size="small"
            sx={{ mb: 1 }}
          />
          <Typography variant="caption" color="text.secondary">
            Last update: {lastUpdate.toLocaleTimeString()}
          </Typography>
        </Box>
      </div>
    );

    return (
      <Box sx={{ display: 'flex' }}>
        <AppBar
          position="fixed"
          sx={{
            width: { sm: `calc(100% - ${drawerWidth}px)` },
            ml: { sm: `${drawerWidth}px` },
            bgcolor: 'background.paper',
            borderBottom: '1px solid #333',
          }}
        >
          <Toolbar>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={this.handleDrawerToggle}
              sx={{ mr: 2, display: { sm: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
              Cosmic Trading Bot Dashboard
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <IconButton color="primary" title="Start Bot">
                <PlayIcon />
              </IconButton>
              <IconButton color="error" title="Stop Bot">
                <StopIcon />
              </IconButton>
              <IconButton color="primary" title="Refresh" onClick={this.checkSystemStatus}>
                <RefreshIcon />
              </IconButton>
            </Box>
          </Toolbar>
        </AppBar>
        <Box
          component="nav"
          sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        >
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={this.handleDrawerToggle}
            ModalProps={{
              keepMounted: true,
            }}
            sx={{
              display: { xs: 'block', sm: 'none' },
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
            }}
          >
            {drawer}
          </Drawer>
          <Drawer
            variant="permanent"
            sx={{
              display: { xs: 'none', sm: 'block' },
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
            }}
            open
          >
            {drawer}
          </Drawer>
        </Box>
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            width: { sm: `calc(100% - ${drawerWidth}px)` },
            mt: 8,
          }}
        >
          {children}
        </Box>
      </Box>
    );
  }
}

export default DashboardLayout;
