import React, { Component } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  Divider,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Refresh,
  CheckCircle,
  Error,
  Warning,
  ExpandMore,
  BugReport,
  Speed,
  Memory,
  Storage,
  NetworkCheck,
  Security,
  Timeline,
} from '@mui/icons-material';

class TestRunner extends Component {
  constructor(props) {
    super(props);
    this.state = {
      running: false,
      currentTest: null,
      testResults: [],
      testQueue: [],
      selectedTests: [],
      testConfig: {
        testMode: 'paper',
        duration: 60,
        maxTrades: 10,
        riskLevel: 'low',
      },
      systemMetrics: {
        cpu: 0,
        memory: 0,
        network: 0,
        disk: 0,
      },
      error: null,
    };
  }

  componentDidMount() {
    this.loadTestResults();
    this.startMetricsMonitoring();
  }

  componentWillUnmount() {
    this.stopMetricsMonitoring();
  }

  loadTestResults = async () => {
    try {
      // Simulate API call - replace with actual endpoint
      const results = await this.fetchTestResults();
      this.setState({ testResults: results });
    } catch (error) {
      this.setState({ error: 'Failed to load test results' });
    }
  };

  fetchTestResults = async () => {
    // Simulate API call - replace with actual endpoint
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          {
            id: 1,
            name: 'API Connection Test',
            status: 'passed',
            duration: 2.5,
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            details: 'Successfully connected to Binance API',
          },
          {
            id: 2,
            name: 'Model Prediction Test',
            status: 'passed',
            duration: 15.2,
            timestamp: new Date(Date.now() - 7200000).toISOString(),
            details: 'ML model generated predictions with 75% accuracy',
          },
          {
            id: 3,
            name: 'Trade Execution Test',
            status: 'failed',
            duration: 8.1,
            timestamp: new Date(Date.now() - 10800000).toISOString(),
            details: 'Failed to execute test trade due to insufficient balance',
          },
          {
            id: 4,
            name: 'Stop Loss Test',
            status: 'passed',
            duration: 5.3,
            timestamp: new Date(Date.now() - 14400000).toISOString(),
            details: 'Stop loss mechanism working correctly',
          },
        ]);
      }, 500);
    });
  };

  startMetricsMonitoring = () => {
    this.metricsInterval = setInterval(() => {
      this.updateSystemMetrics();
    }, 2000);
  };

  stopMetricsMonitoring = () => {
    if (this.metricsInterval) {
      clearInterval(this.metricsInterval);
    }
  };

  updateSystemMetrics = () => {
    // Simulate system metrics - replace with actual monitoring
    this.setState({
      systemMetrics: {
        cpu: Math.random() * 100,
        memory: Math.random() * 100,
        network: Math.random() * 100,
        disk: Math.random() * 100,
      },
    });
  };

  handleTestSelection = (testName) => {
    const { selectedTests } = this.state;
    const updated = selectedTests.includes(testName)
      ? selectedTests.filter(test => test !== testName)
      : [...selectedTests, testName];
    
    this.setState({ selectedTests: updated });
  };

  handleConfigChange = (field, value) => {
    this.setState(prevState => ({
      testConfig: {
        ...prevState.testConfig,
        [field]: value,
      },
    }));
  };

  runTests = async () => {
    const { selectedTests, testConfig } = this.state;
    
    if (selectedTests.length === 0) {
      this.setState({ error: 'Please select at least one test to run' });
      return;
    }

    this.setState({ running: true, error: null });

    try {
      // Simulate test execution - replace with actual API calls
      for (const testName of selectedTests) {
        await this.runSingleTest(testName, testConfig);
      }
    } catch (error) {
      this.setState({ error: 'Test execution failed' });
    } finally {
      this.setState({ running: false });
      this.loadTestResults();
    }
  };

  runSingleTest = async (testName, config) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const newResult = {
          id: Date.now(),
          name: testName,
          status: Math.random() > 0.2 ? 'passed' : 'failed',
          duration: Math.random() * 20 + 1,
          timestamp: new Date().toISOString(),
          details: `Test ${testName} completed with config: ${JSON.stringify(config)}`,
        };

        this.setState(prevState => ({
          testResults: [newResult, ...prevState.testResults],
          currentTest: testName,
        }));

        resolve();
      }, Math.random() * 3000 + 1000);
    });
  };

  stopTests = () => {
    this.setState({ running: false, currentTest: null });
  };

  getStatusColor = (status) => {
    switch (status) {
      case 'passed':
        return 'success';
      case 'failed':
        return 'error';
      case 'running':
        return 'warning';
      default:
        return 'default';
    }
  };

  getStatusIcon = (status) => {
    switch (status) {
      case 'passed':
        return <CheckCircle />;
      case 'failed':
        return <Error />;
      case 'running':
        return <CircularProgress size={16} />;
      default:
        return <Warning />;
    }
  };

  formatDuration = (seconds) => {
    return `${seconds.toFixed(1)}s`;
  };

  formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  render() {
    const {
      running,
      currentTest,
      testResults,
      selectedTests,
      testConfig,
      systemMetrics,
      error,
    } = this.state;

    const availableTests = [
      { name: 'API Connection Test', description: 'Test connection to Binance and Bybit APIs' },
      { name: 'Model Prediction Test', description: 'Test ML model predictions and accuracy' },
      { name: 'Trade Execution Test', description: 'Test paper trading execution' },
      { name: 'Stop Loss Test', description: 'Test stop loss mechanism' },
      { name: 'Database Test', description: 'Test database connectivity and operations' },
      { name: 'Performance Test', description: 'Test system performance under load' },
      { name: 'Security Test', description: 'Test API key validation and security' },
      { name: 'Integration Test', description: 'Test full bot workflow' },
    ];

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
            🧪 Test Runner
          </Typography>
          <Box display="flex" gap={2}>
            <Chip
              icon={running ? <CircularProgress size={16} /> : <BugReport />}
              label={running ? 'RUNNING' : 'IDLE'}
              color={running ? 'warning' : 'default'}
            />
            <Button
              variant="contained"
              startIcon={<PlayArrow />}
              onClick={this.runTests}
              disabled={running || selectedTests.length === 0}
            >
              Run Tests
            </Button>
            <Button
              variant="outlined"
              color="error"
              startIcon={<Stop />}
              onClick={this.stopTests}
              disabled={!running}
            >
              Stop Tests
            </Button>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={this.loadTestResults}
            >
              Refresh
            </Button>
          </Box>
        </Box>

        <Grid container spacing={3}>
          {/* Test Selection */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  🔍 Available Tests
                </Typography>
                <List>
                  {availableTests.map((test) => (
                    <ListItem key={test.name} dense>
                      <ListItemIcon>
                        <Switch
                          checked={selectedTests.includes(test.name)}
                          onChange={() => this.handleTestSelection(test.name)}
                        />
                      </ListItemIcon>
                      <ListItemText
                        primary={test.name}
                        secondary={test.description}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Test Configuration */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  ⚙️ Test Configuration
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Test Mode</InputLabel>
                      <Select
                        value={testConfig.testMode}
                        label="Test Mode"
                        onChange={(e) => this.handleConfigChange('testMode', e.target.value)}
                      >
                        <MenuItem value="paper">Paper Trading</MenuItem>
                        <MenuItem value="simulation">Simulation</MenuItem>
                        <MenuItem value="backtest">Backtest</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      size="small"
                      label="Duration (seconds)"
                      type="number"
                      value={testConfig.duration}
                      onChange={(e) => this.handleConfigChange('duration', parseInt(e.target.value))}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      size="small"
                      label="Max Trades"
                      type="number"
                      value={testConfig.maxTrades}
                      onChange={(e) => this.handleConfigChange('maxTrades', parseInt(e.target.value))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Risk Level</InputLabel>
                      <Select
                        value={testConfig.riskLevel}
                        label="Risk Level"
                        onChange={(e) => this.handleConfigChange('riskLevel', e.target.value)}
                      >
                        <MenuItem value="low">Low</MenuItem>
                        <MenuItem value="medium">Medium</MenuItem>
                        <MenuItem value="high">High</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* System Metrics */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📊 System Metrics
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Speed color="primary" sx={{ fontSize: 40 }} />
                      <Typography variant="h6">{systemMetrics.cpu.toFixed(1)}%</Typography>
                      <Typography variant="body2" color="textSecondary">CPU Usage</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Memory color="primary" sx={{ fontSize: 40 }} />
                      <Typography variant="h6">{systemMetrics.memory.toFixed(1)}%</Typography>
                      <Typography variant="body2" color="textSecondary">Memory Usage</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <NetworkCheck color="primary" sx={{ fontSize: 40 }} />
                      <Typography variant="h6">{systemMetrics.network.toFixed(1)}%</Typography>
                      <Typography variant="body2" color="textSecondary">Network</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Storage color="primary" sx={{ fontSize: 40 }} />
                      <Typography variant="h6">{systemMetrics.disk.toFixed(1)}%</Typography>
                      <Typography variant="body2" color="textSecondary">Disk Usage</Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Test Results */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📋 Test Results
                </Typography>
                {currentTest && (
                  <Alert severity="info" sx={{ mb: 2 }}>
                    Currently running: {currentTest}
                  </Alert>
                )}
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Test Name</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Duration</TableCell>
                        <TableCell>Timestamp</TableCell>
                        <TableCell>Details</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {testResults.map((result) => (
                        <TableRow key={result.id}>
                          <TableCell>{result.name}</TableCell>
                          <TableCell>
                            <Chip
                              icon={this.getStatusIcon(result.status)}
                              label={result.status.toUpperCase()}
                              color={this.getStatusColor(result.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{this.formatDuration(result.duration)}</TableCell>
                          <TableCell>{this.formatTimestamp(result.timestamp)}</TableCell>
                          <TableCell>{result.details}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  }
}

export default TestRunner;
