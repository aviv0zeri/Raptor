import React, { Component } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Divider,
  Alert,
  CircularProgress,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Refresh,
  Clear,
  Download,
  FilterList,
  PlayArrow,
  Stop,
  Warning,
  Error,
  Info,
  CheckCircle,
} from '@mui/icons-material';

class LogsViewer extends Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: false,
      logs: [],
      filteredLogs: [],
      searchTerm: '',
      logLevel: 'all',
      autoRefresh: true,
      isStreaming: false,
      error: null,
      logTypes: ['main', 'stoploss', 'model', 'system'],
      selectedLogType: 'main',
    };
  }

  componentDidMount() {
    this.loadLogs();
    if (this.state.autoRefresh) {
      this.startStreaming();
    }
  }

  componentWillUnmount() {
    this.stopStreaming();
  }

  loadLogs = async () => {
    try {
      this.setState({ loading: true, error: null });
      
      // Simulate API call - replace with actual endpoint
      const logs = await this.fetchLogs();
      
      this.setState({ logs, loading: false });
      this.filterLogs();
    } catch (error) {
      this.setState({
        error: 'Failed to load logs',
        loading: false,
      });
    }
  };

  fetchLogs = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/logs');
      if (response.ok) {
        const logs = await response.json();
        return logs;
      }
      return [];
    } catch (error) {
      console.error('Failed to fetch logs:', error);
      return [];
    }
  };

  filterLogs = () => {
    const { logs, searchTerm, logLevel, selectedLogType } = this.state;
    
    let filtered = logs.filter(log => {
      // Filter by log type
      if (selectedLogType !== 'all' && log.source !== selectedLogType) {
        return false;
      }
      
      // Filter by level
      if (logLevel !== 'all' && log.level !== logLevel) {
        return false;
      }
      
      // Filter by search term
      if (searchTerm && !log.message.toLowerCase().includes(searchTerm.toLowerCase()) &&
          !log.details.toLowerCase().includes(searchTerm.toLowerCase())) {
        return false;
      }
      
      return true;
    });
    
    this.setState({ filteredLogs: filtered });
  };

  handleSearchChange = (event) => {
    this.setState({ searchTerm: event.target.value }, this.filterLogs);
  };

  handleLogLevelChange = (event) => {
    this.setState({ logLevel: event.target.value }, this.filterLogs);
  };

  handleLogTypeChange = (event) => {
    this.setState({ selectedLogType: event.target.value }, this.filterLogs);
  };

  handleAutoRefreshChange = (event) => {
    const autoRefresh = event.target.checked;
    this.setState({ autoRefresh });
    
    if (autoRefresh) {
      this.startStreaming();
    } else {
      this.stopStreaming();
    }
  };

  startStreaming = () => {
    this.setState({ isStreaming: true });
    this.streamingInterval = setInterval(() => {
      this.loadLogs();
    }, 3000);
  };

  stopStreaming = () => {
    this.setState({ isStreaming: false });
    if (this.streamingInterval) {
      clearInterval(this.streamingInterval);
    }
  };

  clearLogs = () => {
    this.setState({ logs: [], filteredLogs: [] });
  };

  downloadLogs = () => {
    const { filteredLogs } = this.state;
    const logText = filteredLogs.map(log => 
      `${log.timestamp} [${log.level.toUpperCase()}] ${log.message} - ${log.details}`
    ).join('\n');
    
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `trading_bot_logs_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  getLevelColor = (level) => {
    switch (level) {
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'success':
        return 'success';
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  getLevelIcon = (level) => {
    switch (level) {
      case 'error':
        return <Error />;
      case 'warning':
        return <Warning />;
      case 'success':
        return <CheckCircle />;
      case 'info':
        return <Info />;
      default:
        return <Info />;
    }
  };

  formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  render() {
    const {
      loading,
      filteredLogs,
      searchTerm,
      logLevel,
      autoRefresh,
      isStreaming,
      error,
      logTypes,
      selectedLogType,
    } = this.state;

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
            📋 Logs Viewer
          </Typography>
          <Box display="flex" gap={2}>
            <Chip
              icon={isStreaming ? <PlayArrow /> : <Stop />}
              label={isStreaming ? 'STREAMING' : 'STOPPED'}
              color={isStreaming ? 'success' : 'default'}
            />
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={this.loadLogs}
              disabled={loading}
            >
              Refresh
            </Button>
            <Button
              variant="outlined"
              startIcon={<Clear />}
              onClick={this.clearLogs}
            >
              Clear
            </Button>
            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={this.downloadLogs}
              disabled={filteredLogs.length === 0}
            >
              Download
            </Button>
          </Box>
        </Box>

        {/* Filters */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              🔍 Filters
            </Typography>
            <Box display="flex" gap={2} flexWrap="wrap" alignItems="center">
              <TextField
                label="Search logs"
                variant="outlined"
                size="small"
                value={searchTerm}
                onChange={this.handleSearchChange}
                sx={{ minWidth: 200 }}
              />
              
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Log Level</InputLabel>
                <Select
                  value={logLevel}
                  label="Log Level"
                  onChange={this.handleLogLevelChange}
                >
                  <MenuItem value="all">All Levels</MenuItem>
                  <MenuItem value="error">Error</MenuItem>
                  <MenuItem value="warning">Warning</MenuItem>
                  <MenuItem value="info">Info</MenuItem>
                  <MenuItem value="success">Success</MenuItem>
                </Select>
              </FormControl>

              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Log Type</InputLabel>
                <Select
                  value={selectedLogType}
                  label="Log Type"
                  onChange={this.handleLogTypeChange}
                >
                  <MenuItem value="all">All Types</MenuItem>
                  {logTypes.map(type => (
                    <MenuItem key={type} value={type}>
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControlLabel
                control={
                  <Switch
                    checked={autoRefresh}
                    onChange={this.handleAutoRefreshChange}
                  />
                }
                label="Auto Refresh"
              />
            </Box>
          </CardContent>
        </Card>

        {/* Logs List */}
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                📝 Log Entries ({filteredLogs.length})
              </Typography>
              {loading && <CircularProgress size={20} />}
            </Box>

            {filteredLogs.length === 0 ? (
              <Box textAlign="center" py={4}>
                <Typography color="textSecondary">
                  No logs found matching the current filters
                </Typography>
              </Box>
            ) : (
              <Paper sx={{ maxHeight: 600, overflow: 'auto' }}>
                <List>
                  {filteredLogs.map((log, index) => (
                    <React.Fragment key={log.id}>
                      <ListItem alignItems="flex-start">
                        <Box display="flex" flexDirection="column" width="100%">
                          <Box display="flex" alignItems="center" gap={1} mb={1}>
                            <Chip
                              icon={this.getLevelIcon(log.level)}
                              label={log.level.toUpperCase()}
                              color={this.getLevelColor(log.level)}
                              size="small"
                            />
                            <Chip
                              label={log.source}
                              variant="outlined"
                              size="small"
                            />
                            <Typography variant="caption" color="textSecondary">
                              {this.formatTimestamp(log.timestamp)}
                            </Typography>
                          </Box>
                          <Typography variant="body1" gutterBottom>
                            {log.message}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {log.details}
                          </Typography>
                        </Box>
                      </ListItem>
                      {index < filteredLogs.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              </Paper>
            )}
          </CardContent>
        </Card>
      </Box>
    );
  }
}

export default LogsViewer;
