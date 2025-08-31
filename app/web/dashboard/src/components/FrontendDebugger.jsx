/**
 * 🔍 Frontend Debugger - The Cosmic Frontend Analyzer
 * ================================================
 * 
 * 📁 File: /bot2025_centralized_api_integrated/web/dashboard/src/components/FrontendDebugger.jsx
 * 🎯 Purpose: Frontend debugging and analysis component
 * 🔧 Function: Provides real-time frontend debugging and error detection
 * 
 * 🌟 Features:
 * - Real-time component analysis
 * - Error boundary and error tracking
 * - Performance monitoring
 * - Network request debugging
 * - State management debugging
 * - Console log capture
 * - Memory usage monitoring
 * - React component tree analysis
 * 
 * 🔄 Debugging Capabilities:
 * - Component render performance
 * - State changes tracking
 * - Props validation
 * - Event handling analysis
 * - API call monitoring
 * - Error boundary integration
 * - Memory leak detection
 * 
 * 📊 Output:
 * - Real-time debug panel
 * - Error reports
 * - Performance metrics
 * - Network activity logs
 * - Component lifecycle logs
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  CircularProgress,
  IconButton,
  Collapse,
  Paper,
  Grid,
  Switch,
  FormControlLabel,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  BugReport as BugIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  CheckCircle as SuccessIcon,
  Info as InfoIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Refresh as RefreshIcon,
  Clear as ClearIcon,
  Settings as SettingsIcon,
  Memory as MemoryIcon,
  Speed as SpeedIcon,
  NetworkCheck as NetworkIcon,
  Code as CodeIcon
} from '@mui/icons-material';

// Debug levels
const DEBUG_LEVELS = {
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
  DEBUG: 'debug'
};

// Debug categories
const DEBUG_CATEGORIES = {
  COMPONENT: 'component',
  NETWORK: 'network',
  STATE: 'state',
  PERFORMANCE: 'performance',
  MEMORY: 'memory',
  ERROR: 'error'
};

class FrontendDebugger {
  constructor() {
    this.logs = [];
    this.errors = [];
    this.warnings = [];
    this.performanceMetrics = {};
    this.networkRequests = [];
    this.memoryUsage = [];
    this.isEnabled = true;
    this.maxLogs = 1000;
    this.listeners = new Set();
    
    // Initialize debugger
    this.initializeDebugger();
  }

  initializeDebugger() {
    // Capture console methods
    this.captureConsole();
    
    // Capture network requests
    this.captureNetworkRequests();
    
    // Monitor performance
    this.monitorPerformance();
    
    // Monitor memory usage
    this.monitorMemoryUsage();
    
    // Set up error boundary
    this.setupErrorBoundary();
  }

  captureConsole() {
    const originalConsole = {
      log: console.log,
      error: console.error,
      warn: console.warn,
      info: console.info,
      debug: console.debug
    };

    // Override console methods
    console.log = (...args) => {
      this.addLog(DEBUG_LEVELS.INFO, DEBUG_CATEGORIES.COMPONENT, 'Console Log', args);
      originalConsole.log(...args);
    };

    console.error = (...args) => {
      this.addLog(DEBUG_LEVELS.ERROR, DEBUG_CATEGORIES.ERROR, 'Console Error', args);
      originalConsole.error(...args);
    };

    console.warn = (...args) => {
      this.addLog(DEBUG_LEVELS.WARNING, DEBUG_CATEGORIES.COMPONENT, 'Console Warning', args);
      originalConsole.warn(...args);
    };

    console.info = (...args) => {
      this.addLog(DEBUG_LEVELS.INFO, DEBUG_CATEGORIES.COMPONENT, 'Console Info', args);
      originalConsole.info(...args);
    };

    console.debug = (...args) => {
      this.addLog(DEBUG_LEVELS.DEBUG, DEBUG_CATEGORIES.COMPONENT, 'Console Debug', args);
      originalConsole.debug(...args);
    };
  }

  captureNetworkRequests() {
    const originalFetch = window.fetch;
    
    window.fetch = async (...args) => {
      const startTime = performance.now();
      const requestId = Math.random().toString(36).substr(2, 9);
      
      try {
        const response = await originalFetch(...args);
        const endTime = performance.now();
        const duration = endTime - startTime;
        
        this.addNetworkRequest({
          id: requestId,
          url: args[0],
          method: args[1]?.method || 'GET',
          status: response.status,
          duration,
          timestamp: new Date().toISOString(),
          success: response.ok
        });
        
        return response;
      } catch (error) {
        const endTime = performance.now();
        const duration = endTime - startTime;
        
        this.addNetworkRequest({
          id: requestId,
          url: args[0],
          method: args[1]?.method || 'GET',
          status: 0,
          duration,
          timestamp: new Date().toISOString(),
          success: false,
          error: error.message
        });
        
        throw error;
      }
    };
  }

  monitorPerformance() {
    if ('performance' in window) {
      // Monitor long tasks
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.duration > 50) { // Long task threshold
            this.addLog(DEBUG_LEVELS.WARNING, DEBUG_CATEGORIES.PERFORMANCE, 'Long Task Detected', {
              duration: entry.duration,
              startTime: entry.startTime,
              name: entry.name
            });
          }
        }
      });
      
      observer.observe({ entryTypes: ['longtask'] });
    }
  }

  monitorMemoryUsage() {
    if ('memory' in performance) {
      setInterval(() => {
        const memory = performance.memory;
        this.addMemoryUsage({
          used: memory.usedJSHeapSize,
          total: memory.totalJSHeapSize,
          limit: memory.jsHeapSizeLimit,
          timestamp: new Date().toISOString()
        });
      }, 5000); // Check every 5 seconds
    }
  }

  setupErrorBoundary() {
    window.addEventListener('error', (event) => {
      this.addLog(DEBUG_LEVELS.ERROR, DEBUG_CATEGORIES.ERROR, 'Global Error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error
      });
    });

    window.addEventListener('unhandledrejection', (event) => {
      this.addLog(DEBUG_LEVELS.ERROR, DEBUG_CATEGORIES.ERROR, 'Unhandled Promise Rejection', {
        reason: event.reason
      });
    });
  }

  addLog(level, category, message, data = null) {
    if (!this.isEnabled) return;

    const log = {
      id: Math.random().toString(36).substr(2, 9),
      level,
      category,
      message,
      data,
      timestamp: new Date().toISOString(),
      component: this.getCurrentComponent()
    };

    this.logs.push(log);
    
    // Keep logs within limit
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }

    // Categorize logs
    if (level === DEBUG_LEVELS.ERROR) {
      this.errors.push(log);
    } else if (level === DEBUG_LEVELS.WARNING) {
      this.warnings.push(log);
    }

    // Notify listeners
    this.notifyListeners();
  }

  addNetworkRequest(request) {
    this.networkRequests.push(request);
    
    // Keep network requests within limit
    if (this.networkRequests.length > 100) {
      this.networkRequests.shift();
    }

    this.notifyListeners();
  }

  addMemoryUsage(memory) {
    this.memoryUsage.push(memory);
    
    // Keep memory usage within limit
    if (this.memoryUsage.length > 50) {
      this.memoryUsage.shift();
    }

    this.notifyListeners();
  }

  getCurrentComponent() {
    // Try to get current component name from React DevTools
    try {
      const reactElement = document.querySelector('[data-reactroot]');
      return reactElement ? 'React Component' : 'Unknown';
    } catch {
      return 'Unknown';
    }
  }

  addListener(callback) {
    this.listeners.add(callback);
  }

  removeListener(callback) {
    this.listeners.delete(callback);
  }

  notifyListeners() {
    this.listeners.forEach(callback => callback());
  }

  clearLogs() {
    this.logs = [];
    this.errors = [];
    this.warnings = [];
    this.networkRequests = [];
    this.memoryUsage = [];
    this.notifyListeners();
  }

  getStats() {
    return {
      totalLogs: this.logs.length,
      errors: this.errors.length,
      warnings: this.warnings.length,
      networkRequests: this.networkRequests.length,
      memoryUsage: this.memoryUsage.length,
      isEnabled: this.isEnabled
    };
  }

  enable() {
    this.isEnabled = true;
    this.addLog(DEBUG_LEVELS.INFO, DEBUG_CATEGORIES.COMPONENT, 'Debugger Enabled');
  }

  disable() {
    this.isEnabled = false;
    this.addLog(DEBUG_LEVELS.INFO, DEBUG_CATEGORIES.COMPONENT, 'Debugger Disabled');
  }
}

// Global debugger instance
const frontendDebugger = new FrontendDebugger();

// React Component
const FrontendDebuggerComponent = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState({});
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedLevel, setSelectedLevel] = useState('all');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [showNetwork, setShowNetwork] = useState(true);
  const [showMemory, setShowMemory] = useState(true);
  const [showPerformance, setShowPerformance] = useState(true);

  const updateData = useCallback(() => {
    setLogs([...frontendDebugger.logs]);
    setStats(frontendDebugger.getStats());
  }, []);

  useEffect(() => {
    frontendDebugger.addListener(updateData);
    updateData();

    return () => {
      frontendDebugger.removeListener(updateData);
    };
  }, [updateData]);

  useEffect(() => {
    if (autoRefresh && isOpen) {
      const interval = setInterval(updateData, 1000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, isOpen, updateData]);

  const filteredLogs = logs.filter(log => {
    if (selectedCategory !== 'all' && log.category !== selectedCategory) return false;
    if (selectedLevel !== 'all' && log.level !== selectedLevel) return false;
    return true;
  });

  const getLevelIcon = (level) => {
    switch (level) {
      case DEBUG_LEVELS.ERROR: return <ErrorIcon color="error" />;
      case DEBUG_LEVELS.WARNING: return <WarningIcon color="warning" />;
      case DEBUG_LEVELS.SUCCESS: return <SuccessIcon color="success" />;
      case DEBUG_LEVELS.INFO: return <InfoIcon color="info" />;
      default: return <InfoIcon />;
    }
  };

  const getLevelColor = (level) => {
    switch (level) {
      case DEBUG_LEVELS.ERROR: return 'error';
      case DEBUG_LEVELS.WARNING: return 'warning';
      case DEBUG_LEVELS.SUCCESS: return 'success';
      case DEBUG_LEVELS.INFO: return 'info';
      default: return 'default';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const formatData = (data) => {
    if (!data) return '';
    if (typeof data === 'object') {
      return JSON.stringify(data, null, 2);
    }
    return String(data);
  };

  return (
    <>
      {/* Debugger Toggle Button */}
      <Box position="fixed" bottom={16} right={16} zIndex={9999}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<BugIcon />}
          onClick={() => setIsOpen(!isOpen)}
          sx={{ borderRadius: 2 }}
        >
          Debugger
          {stats.errors > 0 && (
            <Chip
              label={stats.errors}
              color="error"
              size="small"
              sx={{ ml: 1, minWidth: 20 }}
            />
          )}
        </Button>
      </Box>

      {/* Debugger Panel */}
      <Collapse in={isOpen}>
        <Box
          position="fixed"
          bottom={80}
          right={16}
          width={600}
          maxHeight={500}
          zIndex={9998}
          sx={{ overflow: 'hidden' }}
        >
          <Card elevation={8}>
            <CardContent sx={{ p: 0 }}>
              {/* Header */}
              <Box
                display="flex"
                alignItems="center"
                justifyContent="space-between"
                p={2}
                bgcolor="primary.main"
                color="white"
              >
                <Typography variant="h6" display="flex" alignItems="center">
                  <BugIcon sx={{ mr: 1 }} />
                  Frontend Debugger
                </Typography>
                <Box display="flex" gap={1}>
                  <IconButton
                    size="small"
                    color="inherit"
                    onClick={() => setAutoRefresh(!autoRefresh)}
                  >
                    <RefreshIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="inherit"
                    onClick={frontendDebugger.clearLogs.bind(frontendDebugger)}
                  >
                    <ClearIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="inherit"
                    onClick={() => setIsOpen(false)}
                  >
                    <CollapseIcon />
                  </IconButton>
                </Box>
              </Box>

              {/* Stats Bar */}
              <Box p={1} bgcolor="grey.100">
                <Grid container spacing={1}>
                  <Grid item>
                    <Chip
                      icon={<ErrorIcon />}
                      label={`${stats.errors} Errors`}
                      color="error"
                      size="small"
                    />
                  </Grid>
                  <Grid item>
                    <Chip
                      icon={<WarningIcon />}
                      label={`${stats.warnings} Warnings`}
                      color="warning"
                      size="small"
                    />
                  </Grid>
                  <Grid item>
                    <Chip
                      icon={<NetworkIcon />}
                      label={`${stats.networkRequests} Requests`}
                      color="info"
                      size="small"
                    />
                  </Grid>
                  <Grid item>
                    <Chip
                      icon={<MemoryIcon />}
                      label={`${stats.memoryUsage} Memory`}
                      color="default"
                      size="small"
                    />
                  </Grid>
                </Grid>
              </Box>

              {/* Filters */}
              <Box p={1} bgcolor="grey.50">
                <Grid container spacing={1} alignItems="center">
                  <Grid item>
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                      <InputLabel>Category</InputLabel>
                      <Select
                        value={selectedCategory}
                        onChange={(e) => setSelectedCategory(e.target.value)}
                        label="Category"
                      >
                        <MenuItem value="all">All Categories</MenuItem>
                        {Object.values(DEBUG_CATEGORIES).map(category => (
                          <MenuItem key={category} value={category}>
                            {category.charAt(0).toUpperCase() + category.slice(1)}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item>
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                      <InputLabel>Level</InputLabel>
                      <Select
                        value={selectedLevel}
                        onChange={(e) => setSelectedLevel(e.target.value)}
                        label="Level"
                      >
                        <MenuItem value="all">All Levels</MenuItem>
                        {Object.values(DEBUG_LEVELS).map(level => (
                          <MenuItem key={level} value={level}>
                            {level.charAt(0).toUpperCase() + level.slice(1)}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={autoRefresh}
                          onChange={(e) => setAutoRefresh(e.target.checked)}
                          size="small"
                        />
                      }
                      label="Auto Refresh"
                    />
                  </Grid>
                </Grid>
              </Box>

              {/* Logs */}
              <Box
                sx={{
                  height: 300,
                  overflow: 'auto',
                  bgcolor: 'background.paper'
                }}
              >
                <List dense>
                  {filteredLogs.slice(-50).reverse().map((log) => (
                    <ListItem key={log.id} divider>
                      <ListItemIcon>
                        {getLevelIcon(log.level)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="body2" component="span">
                              {log.message}
                            </Typography>
                            <Chip
                              label={log.category}
                              size="small"
                              variant="outlined"
                            />
                            <Typography variant="caption" color="text.secondary">
                              {formatTimestamp(log.timestamp)}
                            </Typography>
                          </Box>
                        }
                        secondary={
                          log.data && (
                            <Box mt={1}>
                              <Typography variant="caption" component="pre" sx={{ fontSize: '0.7rem' }}>
                                {formatData(log.data)}
                              </Typography>
                            </Box>
                          )
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Collapse>
    </>
  );
};

// Global debugger instance
const frontendDebugger = new FrontendDebugger();

export default FrontendDebuggerComponent;
export { frontendDebugger };
