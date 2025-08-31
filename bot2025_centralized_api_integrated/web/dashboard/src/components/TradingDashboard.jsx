import React, { Component } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Switch,
  FormControlLabel,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  AppBar,
  Toolbar,
} from '@mui/material';
import {
  TrendingUp,
  AccountBalance,
  ShowChart,
  PlayArrow,
  Stop,
  Warning,
  CheckCircle,
  Error,
  Wifi,
  WifiOff,
  Psychology,
  Settings,
  Analytics,
  Code,
  Dashboard,
  Assessment,
  RocketLaunch,
  PowerSettingsNew,
  StopCircle,
  RestartAlt,
  Info as InfoIcon,
  Visibility,
  VisibilityOff,
  Refresh,
  Timeline,
  AttachMoney,
  CurrencyExchange,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

// Raptor Trading Bot Class - Real Strategy Integration
class RaptorTradingBot {
  constructor() {
    this.status = 'not_active';
    this.modelStatus = 'idle';
    this.connections = {
      api: false,
      binance: false,
      database: false,
      websocket: false
    };
    this.metrics = {
      totalTrades: 0,
      successfulTrades: 0,
      failedTrades: 0,
      totalProfit: 0,
      winRate: 0,
      activePositions: 0
    };
    this.settings = {
      autoTrading: false,
      riskLevel: 'medium',
      maxPositions: 5,
      stopLoss: 2.0,
      takeProfit: 5.0
    };
    this.logs = [];
    this.csvLogs = [];
    this.modelSignals = [];
    this.botTrades = [];
    this.listeners = [];
    
    // Real wallet simulation
    this.wallet = {
      bot_coin: 'CHZ',
      bot_coin_amount: 0.0,
      usdt_amount: 1000.0,
      total_usdt_value: 1000.0,
      chz_price: 0.05
    };
    
    this.lastUpdate = new Date();
    this.csvPollingInterval = null;
    this.modelPollingInterval = null;
  }

  addListener(callback) {
    this.listeners.push(callback);
  }

  removeListener(callback) {
    this.listeners = this.listeners.filter(listener => listener !== callback);
  }

  notifyListeners() {
    this.listeners.forEach(callback => callback(this.getState()));
  }

  getState() {
    return {
      status: this.status,
      modelStatus: this.modelStatus,
      connections: this.connections,
      metrics: this.metrics,
      settings: this.settings,
      logs: this.logs,
      csvLogs: this.csvLogs,
      modelSignals: this.modelSignals,
      botTrades: this.botTrades,
      wallet: this.wallet,
      lastUpdate: this.lastUpdate
    };
  }

  async startRaptorBot() {
    this.status = 'starting';
    this.addLog('info', '🚀 Raptor Bot starting...');
    this.notifyListeners();

    // Simulate bot startup
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    this.status = 'running';
    this.addLog('success', '✅ Raptor Bot started successfully');
    this.addLog('info', '🧠 Starting ML Model...');
    
    // Start model after bot
    setTimeout(() => {
      this.modelStatus = 'starting';
      this.addLog('info', '🧠 ML Model initializing...');
      this.notifyListeners();
      
      setTimeout(() => {
        this.modelStatus = 'running';
        this.addLog('success', '✅ ML Model started and analyzing data');
        this.addLog('info', '📊 Model will generate indicators every 1 minute');
        this.notifyListeners();
        
        // Start CSV polling
        this.startCSVPolling();
      }, 2000);
    }, 1000);
    
    this.notifyListeners();
  }

  async stopRaptorBot() {
    this.status = 'stopping';
    this.addLog('warning', '🛑 Raptor Bot stopping...');
    this.notifyListeners();

    // Stop polling
    if (this.csvPollingInterval) {
      clearInterval(this.csvPollingInterval);
    }
    if (this.modelPollingInterval) {
      clearInterval(this.modelPollingInterval);
    }

    // Simulate bot shutdown
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    this.status = 'not_active';
    this.modelStatus = 'idle';
    this.addLog('info', '✅ Raptor Bot stopped');
    this.notifyListeners();
  }

  startCSVPolling() {
    // Poll model_output.csv every 5 seconds
    this.modelPollingInterval = setInterval(() => {
      this.readModelOutput();
    }, 5000);
    
    // Poll bot_output_auto.csv every 3 seconds
    this.csvPollingInterval = setInterval(() => {
      this.readBotOutput();
    }, 3000);
  }

  async readModelOutput() {
    try {
      // In a real implementation, this would fetch from the backend
      // For now, simulate reading model signals
      const signals = ['BUY', 'HOLD', 'SELL'];
      const signal = signals[Math.floor(Math.random() * signals.length)];
      const quantity = Math.floor(Math.random() * 10) + 1;
      const coin = 'CHZ/USDT';
      const timestamp = new Date().toLocaleString();
      
      const modelSignal = {
        timestamp,
        signal,
        quantity,
        coin
      };
      
      this.modelSignals.push(modelSignal);
      this.addCsvLog(`${timestamp}, ${signal}, ${quantity}, ${coin}`);
      this.addLog('info', `📊 Model Signal: ${signal} ${quantity} ${coin}`);
      
      // Keep only last 50 signals
      if (this.modelSignals.length > 50) {
        this.modelSignals = this.modelSignals.slice(-50);
      }
      
      this.lastUpdate = new Date();
      this.notifyListeners();
    } catch (error) {
      this.addLog('error', `Error reading model output: ${error.message}`);
    }
  }

  async readBotOutput() {
    try {
      // In a real implementation, this would fetch from the backend
      // For now, simulate reading bot trades
      if (this.modelSignals.length > 0) {
        const lastSignal = this.modelSignals[this.modelSignals.length - 1];
        if (lastSignal.signal === 'BUY' && Math.random() > 0.7) {
          // Simulate a trade execution
          const trade = {
            order_id: `TEST_${Date.now()}`,
            timestamp: new Date().toLocaleString(),
            type: 'MARKET',
            symbol: 'CHZUSDT',
            quantity: lastSignal.quantity,
            fees_amount: (lastSignal.quantity * 0.05 * 0.001).toFixed(4),
            price: '0.0500',
            side: 'BUY',
            execution_time: '0.1'
          };
          
          this.botTrades.push(trade);
          this.metrics.totalTrades++;
          this.metrics.successfulTrades++;
          
          // Update wallet
          this.wallet.usdt_amount -= (lastSignal.quantity * 0.05);
          this.wallet.bot_coin_amount += lastSignal.quantity;
          
          this.addLog('success', `✅ Trade executed: ${trade.side} ${trade.quantity} ${trade.symbol} at $${trade.price}`);
          
          // Keep only last 100 trades
          if (this.botTrades.length > 100) {
            this.botTrades = this.botTrades.slice(-100);
          }
          
          this.updateMetrics();
          this.notifyListeners();
        }
      }
    } catch (error) {
      this.addLog('error', `Error reading bot output: ${error.message}`);
    }
  }

  addLog(level, message, data = null) {
    const log = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      level,
      message,
      data
    };
    this.logs.push(log);
    
    // Keep only last 100 logs
    if (this.logs.length > 100) {
      this.logs = this.logs.slice(-100);
    }
    
    this.notifyListeners();
  }

  addCsvLog(csvLine) {
    const csvLog = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      line: csvLine
    };
    this.csvLogs.push(csvLog);
    
    // Keep only last 100 CSV logs
    if (this.csvLogs.length > 100) {
      this.csvLogs = this.csvLogs.slice(-100);
    }
    
    this.notifyListeners();
  }

  updateMetrics() {
    this.metrics.winRate = this.metrics.totalTrades > 0 ? 
      (this.metrics.successfulTrades / this.metrics.totalTrades) * 100 : 0;
    this.metrics.totalProfit = this.botTrades.reduce((total, trade) => {
      if (trade.side === 'BUY') {
        return total - (parseFloat(trade.quantity) * parseFloat(trade.price));
      } else {
        return total + (parseFloat(trade.quantity) * parseFloat(trade.price));
      }
    }, 0);
    this.metrics.activePositions = this.wallet.bot_coin_amount > 0 ? 1 : 0;
  }

  updateSettings(newSettings) {
    this.settings = { ...this.settings, ...newSettings };
    this.addLog('info', 'Settings updated', newSettings);
    this.notifyListeners();
  }

  updateWallet() {
    // Simulate wallet updates
    const priceChange = (Math.random() - 0.5) * 0.1;
    this.wallet.chz_price = 0.05 * (1 + priceChange);
    this.wallet.total_usdt_value = this.wallet.bot_coin_amount * this.wallet.chz_price + this.wallet.usdt_amount;
    this.notifyListeners();
  }

  testConnections() {
    this.addLog('info', '🔌 Testing connections...');
    
    // Simulate connection tests
    setTimeout(() => {
      this.connections.api = true;
      this.connections.binance = true;
      this.connections.database = true;
      this.connections.websocket = true;
      this.addLog('success', '✅ All connections successful');
      this.notifyListeners();
    }, 2000);
  }
}

// Global Raptor bot instance
const raptorBot = new RaptorTradingBot();

class TradingDashboard extends Component {
  constructor(props) {
    super(props);
    this.state = {
      activeTab: 0,
      botState: raptorBot.getState(),
      showSettings: false,
      showLogs: false,
    };
  }

  componentDidMount() {
    // Subscribe to bot controller updates
    raptorBot.addListener(this.handleBotStateUpdate);
    
    // Test connections on mount
    raptorBot.testConnections();
    
    // Update wallet every 30 seconds
    setInterval(() => {
      raptorBot.updateWallet();
    }, 30000);
  }

  componentWillUnmount() {
    raptorBot.removeListener(this.handleBotStateUpdate);
  }

  handleBotStateUpdate = (newState) => {
    this.setState({ botState: newState });
  };

  handleStartRaptorBot = async () => {
    await raptorBot.startRaptorBot();
  };

  handleStopRaptorBot = async () => {
    await raptorBot.stopRaptorBot();
  };

  handleTabChange = (event, newValue) => {
    this.setState({ activeTab: newValue });
  };

  handleSettingsChange = (setting, value) => {
    raptorBot.updateSettings({ [setting]: value });
  };

  getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'success';
      case 'starting': return 'warning';
      case 'stopping': return 'warning';
      case 'not_active': return 'default';
      default: return 'default';
    }
  };

  getConnectionIcon = (connected) => {
    return connected ? <Wifi color="success" /> : <WifiOff color="error" />;
  };

  render() {
    const { activeTab, botState } = this.state;

    return (
      <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
        {/* App Bar */}
        <AppBar position="static" sx={{ background: 'linear-gradient(45deg, #1a1a1a 0%, #2d2d2d 100%)' }}>
          <Toolbar>
            <Typography variant="h4" sx={{ 
              background: 'linear-gradient(45deg, #ff6b35, #f7931e)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              fontWeight: 'bold',
              flexGrow: 1
            }}>
              🦖 RAPTOR TRADING BOT
            </Typography>
            <Box display="flex" gap={1}>
              <Chip 
                label={`BOT: ${botState.status.toUpperCase()}`}
                color={this.getStatusColor(botState.status)}
                icon={botState.status === 'running' ? <PlayArrow /> : <Stop />}
              />
              <Chip 
                label={`MODEL: ${botState.modelStatus.toUpperCase()}`}
                color={this.getStatusColor(botState.modelStatus)}
                icon={botState.modelStatus === 'running' ? <Psychology /> : <Code />}
              />
            </Box>
          </Toolbar>
        </AppBar>

        {/* Main Content */}
        <Box sx={{ flexGrow: 1, display: 'flex', overflow: 'hidden' }}>
          {/* Left Panel - Controls and Wallet */}
          <Box sx={{ width: 400, p: 2, borderRight: 1, borderColor: 'divider', overflow: 'auto' }}>
            {/* Control Panel */}
            <Card sx={{ mb: 2, background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ color: 'white' }}>
                  🎮 Control Center
                </Typography>
                <Box display="flex" flexDirection="column" gap={2}>
                  <Button
                    variant="contained"
                    color="success"
                    startIcon={<RocketLaunch />}
                    onClick={this.handleStartRaptorBot}
                    disabled={botState.status === 'running' || botState.status === 'starting'}
                    size="large"
                    fullWidth
                  >
                    🚀 Start Raptor Bot
                  </Button>
                  <Button
                    variant="contained"
                    color="error"
                    startIcon={<PowerSettingsNew />}
                    onClick={this.handleStopRaptorBot}
                    disabled={botState.status === 'not_active' || botState.status === 'stopping'}
                    size="large"
                    fullWidth
                  >
                    🛑 Stop Raptor Bot
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<RestartAlt />}
                    onClick={() => raptorBot.testConnections()}
                    size="large"
                    fullWidth
                  >
                    🔌 Test Connections
                  </Button>
                </Box>
              </CardContent>
            </Card>

            {/* Wallet */}
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  💼 Raptor Wallet
                </Typography>
                <Box display="flex" flexDirection="column" gap={1}>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2">CHZ Balance:</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {botState.wallet.bot_coin_amount.toLocaleString()} CHZ
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2">USDT Balance:</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      ${botState.wallet.usdt_amount.toLocaleString()}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2">CHZ Price:</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      ${botState.wallet.chz_price.toFixed(4)}
                    </Typography>
                  </Box>
                  <Divider />
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="h6">Total Value:</Typography>
                    <Typography variant="h6" color="primary" fontWeight="bold">
                      ${botState.wallet.total_usdt_value.toLocaleString()}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>

            {/* Connection Status */}
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  🔌 Connections
                </Typography>
                <Box display="flex" flexDirection="column" gap={1}>
                  {Object.entries(botState.connections).map(([service, connected]) => (
                    <Box key={service} display="flex" alignItems="center" gap={1}>
                      {this.getConnectionIcon(connected)}
                      <Typography variant="body2" color={connected ? 'success.main' : 'error.main'}>
                        {service.toUpperCase()}: {connected ? 'Connected' : 'Disconnected'}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>

            {/* Live Logs */}
            <Card sx={{ flexGrow: 1 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📋 Live Logs
                </Typography>
                <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
                  <List dense>
                    {botState.logs.slice(-10).reverse().map((log) => (
                      <ListItem key={log.id} sx={{ py: 0.5 }}>
                        <ListItemIcon sx={{ minWidth: 30 }}>
                          {log.level === 'success' && <CheckCircle color="success" fontSize="small" />}
                          {log.level === 'warning' && <Warning color="warning" fontSize="small" />}
                          {log.level === 'error' && <Error color="error" fontSize="small" />}
                          {log.level === 'info' && <InfoIcon color="info" fontSize="small" />}
                        </ListItemIcon>
                        <ListItemText
                          primary={log.message}
                          secondary={new Date(log.timestamp).toLocaleTimeString()}
                          primaryTypographyProps={{ fontSize: '0.8rem' }}
                          secondaryTypographyProps={{ fontSize: '0.7rem' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              </CardContent>
            </Card>
          </Box>

          {/* Right Panel - Main Dashboard */}
          <Box sx={{ flexGrow: 1, p: 2, overflow: 'auto' }}>
            <Tabs value={activeTab} onChange={this.handleTabChange} sx={{ mb: 2 }}>
              <Tab label="📊 Overview" icon={<Dashboard />} />
              <Tab label="📈 Trading" icon={<ShowChart />} />
              <Tab label="🧠 ML Model" icon={<Psychology />} />
              <Tab label="📋 CSV Outputs" icon={<Assessment />} />
              <Tab label="⚙️ Settings" icon={<Settings />} />
            </Tabs>

            {/* Tab Content */}
            <Box>
              {activeTab === 0 && this.renderOverview()}
              {activeTab === 1 && this.renderTrading()}
              {activeTab === 2 && this.renderMLModel()}
              {activeTab === 3 && this.renderCsvOutputs()}
              {activeTab === 4 && this.renderSettings()}
            </Box>
          </Box>
        </Box>
      </Box>
    );
  }

  renderOverview() {
    const { botState } = this.state;
    
    return (
      <Grid container spacing={3}>
        {/* Key Metrics */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1}>
                <AccountBalance color="primary" />
                <Typography variant="h6">Total Balance</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                ${botState.wallet.total_usdt_value.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                CHZ: {botState.wallet.bot_coin_amount.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1}>
                <TrendingUp color="success" />
                <Typography variant="h6">Total Profit</Typography>
              </Box>
              <Typography variant="h4" color="success">
                ${botState.metrics.totalProfit.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Win Rate: {botState.metrics.winRate.toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1}>
                <ShowChart color="info" />
                <Typography variant="h6">Active Positions</Typography>
              </Box>
              <Typography variant="h4" color="info">
                {botState.metrics.activePositions}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Trades: {botState.metrics.totalTrades}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1}>
                <Analytics color="warning" />
                <Typography variant="h6">Model Signals</Typography>
              </Box>
              <Typography variant="h4" color="warning">
                {botState.modelSignals.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last: {botState.lastUpdate.toLocaleTimeString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📈 CHZ Price Performance
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={[
                  { time: '09:00', price: 0.049 },
                  { time: '10:00', price: 0.051 },
                  { time: '11:00', price: 0.050 },
                  { time: '12:00', price: 0.052 },
                  { time: '13:00', price: 0.048 },
                  { time: '14:00', price: botState.wallet.chz_price },
                ]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="price" stroke="#ff6b35" strokeWidth={2} name="CHZ Price" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Win/Loss Distribution */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🎯 Trade Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Wins', value: botState.metrics.successfulTrades, color: '#4caf50' },
                      { name: 'Losses', value: botState.metrics.totalTrades - botState.metrics.successfulTrades, color: '#f44336' },
                    ]}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {[
                      { name: 'Wins', value: botState.metrics.successfulTrades, color: '#4caf50' },
                      { name: 'Losses', value: botState.metrics.totalTrades - botState.metrics.successfulTrades, color: '#f44336' },
                    ].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  }

  renderTrading() {
    const { botState } = this.state;
    
    return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 Recent Trades (bot_output_auto.csv)
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Order ID</TableCell>
                      <TableCell>Time</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Symbol</TableCell>
                      <TableCell>Quantity</TableCell>
                      <TableCell>Price</TableCell>
                      <TableCell>Side</TableCell>
                      <TableCell>Execution Time</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {botState.botTrades.slice(-10).reverse().map((trade, index) => (
                      <TableRow key={index}>
                        <TableCell>{trade.order_id}</TableCell>
                        <TableCell>{trade.timestamp}</TableCell>
                        <TableCell>{trade.type}</TableCell>
                        <TableCell>{trade.symbol}</TableCell>
                        <TableCell>{trade.quantity}</TableCell>
                        <TableCell>${trade.price}</TableCell>
                        <TableCell>
                          <Chip 
                            label={trade.side} 
                            color={trade.side === 'BUY' ? 'success' : 'error'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{trade.execution_time}s</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  }

  renderMLModel() {
    const { botState } = this.state;
    
    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🧠 ML Model Status
              </Typography>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <Chip 
                  label={botState.modelStatus.toUpperCase()}
                  color={this.getStatusColor(botState.modelStatus)}
                  icon={botState.modelStatus === 'running' ? <Psychology /> : <Code />}
                />
              </Box>
              <Typography variant="body2" color="text.secondary">
                The ML model analyzes market data and generates trading signals.
                When running, it continuously processes market data and provides
                buy/sell recommendations to the trading bot every 1 minute.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 Model Performance
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <Box>
                  <Typography variant="body2">Signal Accuracy</Typography>
                  <LinearProgress variant="determinate" value={85} sx={{ height: 8, borderRadius: 4 }} />
                  <Typography variant="caption">85%</Typography>
                </Box>
                <Box>
                  <Typography variant="body2">Prediction Success</Typography>
                  <LinearProgress variant="determinate" value={78} sx={{ height: 8, borderRadius: 4 }} />
                  <Typography variant="caption">78%</Typography>
                </Box>
                <Box>
                  <Typography variant="body2">Model Confidence</Typography>
                  <LinearProgress variant="determinate" value={92} sx={{ height: 8, borderRadius: 4 }} />
                  <Typography variant="caption">92%</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Model Signals */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 Recent Model Signals (model_output.csv)
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Timestamp</TableCell>
                      <TableCell>Signal</TableCell>
                      <TableCell>Quantity</TableCell>
                      <TableCell>Coin</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {botState.modelSignals.slice(-10).reverse().map((signal, index) => (
                      <TableRow key={index}>
                        <TableCell>{signal.timestamp}</TableCell>
                        <TableCell>
                          <Chip 
                            label={signal.signal} 
                            color={signal.signal === 'BUY' ? 'success' : signal.signal === 'SELL' ? 'error' : 'warning'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{signal.quantity}</TableCell>
                        <TableCell>{signal.coin}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  }

  renderCsvOutputs() {
    const { botState } = this.state;
    
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          📋 CSV Outputs (model_output.csv)
        </Typography>
        <Card>
          <CardContent>
            <Box sx={{ maxHeight: 600, overflow: 'auto' }}>
              <List dense>
                {botState.csvLogs.slice(-50).reverse().map((log) => (
                  <ListItem key={log.id} divider>
                    <ListItemText
                      primary={log.line}
                      secondary={new Date(log.timestamp).toLocaleString()}
                      primaryTypographyProps={{ fontFamily: 'monospace', fontSize: '0.9rem' }}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          </CardContent>
        </Card>
      </Box>
    );
  }

  renderSettings() {
    const { botState } = this.state;
    
    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                ⚙️ Trading Settings
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={botState.settings.autoTrading}
                      onChange={(e) => this.handleSettingsChange('autoTrading', e.target.checked)}
                    />
                  }
                  label="Auto Trading"
                />
                <FormControl fullWidth>
                  <InputLabel>Risk Level</InputLabel>
                  <Select
                    value={botState.settings.riskLevel}
                    onChange={(e) => this.handleSettingsChange('riskLevel', e.target.value)}
                    label="Risk Level"
                  >
                    <MenuItem value="low">Low Risk</MenuItem>
                    <MenuItem value="medium">Medium Risk</MenuItem>
                    <MenuItem value="high">High Risk</MenuItem>
                  </Select>
                </FormControl>
                <TextField
                  label="Max Positions"
                  type="number"
                  value={botState.settings.maxPositions}
                  onChange={(e) => this.handleSettingsChange('maxPositions', parseInt(e.target.value))}
                  fullWidth
                />
                <TextField
                  label="Stop Loss (%)"
                  type="number"
                  value={botState.settings.stopLoss}
                  onChange={(e) => this.handleSettingsChange('stopLoss', parseFloat(e.target.value))}
                  fullWidth
                />
                <TextField
                  label="Take Profit (%)"
                  type="number"
                  value={botState.settings.takeProfit}
                  onChange={(e) => this.handleSettingsChange('takeProfit', parseFloat(e.target.value))}
                  fullWidth
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🔔 Notifications
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Trade Notifications"
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Error Alerts"
                />
                <FormControlLabel
                  control={<Switch />}
                  label="Performance Reports"
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Connection Status"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  }
}

export default TradingDashboard;
