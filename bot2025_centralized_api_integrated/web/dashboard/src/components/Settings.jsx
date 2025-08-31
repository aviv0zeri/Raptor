import React, { Component } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
} from '@mui/material';
import {
  ExpandMore,
  Save,
  Refresh,
  Security,
  Speed,
  AccountBalance,
  BugReport,
  Settings as SettingsIcon,
} from '@mui/icons-material';

class Settings extends Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: false,
      saving: false,
      settings: {
        trading: {
          testMode: true,
          maxPositionSize: 100.0,
          riskPercentage: 2.0,
          stopLossPercentage: 0.06,
          defaultExchange: 'binance',
          enablePaperTrading: true,
        },
        api: {
          binanceApiKey: '',
          binanceSecretKey: '',
          bybitApiKey: '',
          bybitSecretKey: '',
          testnet: true,
        },
        database: {
          host: 'localhost',
          port: 5432,
          name: 'trading_bot',
          user: 'postgres',
          password: '',
        },
        performance: {
          cacheEnabled: true,
          cacheTTL: 30,
          maxConcurrentRequests: 10,
          requestTimeout: 30,
          autoRestart: true,
        },
        notifications: {
          emailEnabled: false,
          emailAddress: '',
          telegramEnabled: false,
          telegramBotToken: '',
          telegramChatId: '',
          tradeNotifications: true,
          errorNotifications: true,
        },
      },
      error: null,
      success: null,
    };
  }

  componentDidMount() {
    this.loadSettings();
  }

  loadSettings = async () => {
    try {
      this.setState({ loading: true, error: null });
      
      // Simulate API call - replace with actual endpoint
      const settings = await this.fetchSettings();
      
      this.setState({ settings, loading: false });
    } catch (error) {
      this.setState({
        error: 'Failed to load settings',
        loading: false,
      });
    }
  };

  fetchSettings = async () => {
    // Simulate API call - replace with actual endpoint
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          trading: {
            testMode: true,
            maxPositionSize: 100.0,
            riskPercentage: 2.0,
            stopLossPercentage: 0.06,
            defaultExchange: 'binance',
            enablePaperTrading: true,
          },
          api: {
            binanceApiKey: '***hidden***',
            binanceSecretKey: '***hidden***',
            bybitApiKey: '',
            bybitSecretKey: '',
            testnet: true,
          },
          database: {
            host: 'localhost',
            port: 5432,
            name: 'trading_bot',
            user: 'postgres',
            password: '***hidden***',
          },
          performance: {
            cacheEnabled: true,
            cacheTTL: 30,
            maxConcurrentRequests: 10,
            requestTimeout: 30,
            autoRestart: true,
          },
          notifications: {
            emailEnabled: false,
            emailAddress: '',
            telegramEnabled: false,
            telegramBotToken: '',
            telegramChatId: '',
            tradeNotifications: true,
            errorNotifications: true,
          },
        });
      }, 500);
    });
  };

  handleSettingChange = (section, field, value) => {
    this.setState(prevState => ({
      settings: {
        ...prevState.settings,
        [section]: {
          ...prevState.settings[section],
          [field]: value,
        },
      },
    }));
  };

  saveSettings = async () => {
    try {
      this.setState({ saving: true, error: null, success: null });
      
      // Simulate API call - replace with actual endpoint
      await this.updateSettings(this.state.settings);
      
      this.setState({ 
        saving: false, 
        success: 'Settings saved successfully' 
      });
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        this.setState({ success: null });
      }, 3000);
    } catch (error) {
      this.setState({
        error: 'Failed to save settings',
        saving: false,
      });
    }
  };

  updateSettings = async (settings) => {
    // Simulate API call - replace with actual endpoint
    return new Promise((resolve) => {
      setTimeout(() => {
        console.log('Saving settings:', settings);
        resolve();
      }, 1000);
    });
  };

  testConnection = async (type) => {
    try {
      // Simulate connection test - replace with actual endpoint
      await this.performConnectionTest(type);
      
      this.setState({ 
        success: `${type} connection test successful` 
      });
      
      setTimeout(() => {
        this.setState({ success: null });
      }, 3000);
    } catch (error) {
      this.setState({
        error: `${type} connection test failed`,
      });
    }
  };

  performConnectionTest = async (type) => {
    // Simulate connection test - replace with actual endpoint
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (Math.random() > 0.2) {
          resolve();
        } else {
          reject(new Error('Connection failed'));
        }
      }, 2000);
    });
  };

  render() {
    const { loading, saving, settings, error, success } = this.state;

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

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
            ⚙️ Settings
          </Typography>
          <Box display="flex" gap={2}>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={this.loadSettings}
            >
              Reset
            </Button>
            <Button
              variant="contained"
              startIcon={saving ? <CircularProgress size={16} /> : <Save />}
              onClick={this.saveSettings}
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </Button>
          </Box>
        </Box>

        <Grid container spacing={3}>
          {/* Trading Settings */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={2}>
                  <AccountBalance color="primary" />
                  <Typography variant="h6">Trading Configuration</Typography>
                </Box>
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.trading.testMode}
                      onChange={(e) => this.handleSettingChange('trading', 'testMode', e.target.checked)}
                    />
                  }
                  label="Test Mode (Paper Trading)"
                />
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.trading.enablePaperTrading}
                      onChange={(e) => this.handleSettingChange('trading', 'enablePaperTrading', e.target.checked)}
                    />
                  }
                  label="Enable Paper Trading"
                />

                <TextField
                  fullWidth
                  label="Max Position Size (USDT)"
                  type="number"
                  value={settings.trading.maxPositionSize}
                  onChange={(e) => this.handleSettingChange('trading', 'maxPositionSize', parseFloat(e.target.value))}
                  sx={{ mt: 2 }}
                />

                <TextField
                  fullWidth
                  label="Risk Percentage (%)"
                  type="number"
                  value={settings.trading.riskPercentage}
                  onChange={(e) => this.handleSettingChange('trading', 'riskPercentage', parseFloat(e.target.value))}
                  sx={{ mt: 2 }}
                />

                <TextField
                  fullWidth
                  label="Stop Loss Percentage (%)"
                  type="number"
                  value={settings.trading.stopLossPercentage}
                  onChange={(e) => this.handleSettingChange('trading', 'stopLossPercentage', parseFloat(e.target.value))}
                  sx={{ mt: 2 }}
                />

                <FormControl fullWidth sx={{ mt: 2 }}>
                  <InputLabel>Default Exchange</InputLabel>
                  <Select
                    value={settings.trading.defaultExchange}
                    label="Default Exchange"
                    onChange={(e) => this.handleSettingChange('trading', 'defaultExchange', e.target.value)}
                  >
                    <MenuItem value="binance">Binance</MenuItem>
                    <MenuItem value="bybit">Bybit</MenuItem>
                  </Select>
                </FormControl>
              </CardContent>
            </Card>
          </Grid>

          {/* API Settings */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={2}>
                  <Security color="primary" />
                  <Typography variant="h6">API Configuration</Typography>
                </Box>

                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.api.testnet}
                      onChange={(e) => this.handleSettingChange('api', 'testnet', e.target.checked)}
                    />
                  }
                  label="Use Testnet"
                />

                <TextField
                  fullWidth
                  label="Binance API Key"
                  value={settings.api.binanceApiKey}
                  onChange={(e) => this.handleSettingChange('api', 'binanceApiKey', e.target.value)}
                  sx={{ mt: 2 }}
                />

                <TextField
                  fullWidth
                  label="Binance Secret Key"
                  type="password"
                  value={settings.api.binanceSecretKey}
                  onChange={(e) => this.handleSettingChange('api', 'binanceSecretKey', e.target.value)}
                  sx={{ mt: 2 }}
                />

                <TextField
                  fullWidth
                  label="Bybit API Key"
                  value={settings.api.bybitApiKey}
                  onChange={(e) => this.handleSettingChange('api', 'bybitApiKey', e.target.value)}
                  sx={{ mt: 2 }}
                />

                <TextField
                  fullWidth
                  label="Bybit Secret Key"
                  type="password"
                  value={settings.api.bybitSecretKey}
                  onChange={(e) => this.handleSettingChange('api', 'bybitSecretKey', e.target.value)}
                  sx={{ mt: 2 }}
                />

                <Box display="flex" gap={1} mt={2}>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => this.testConnection('Binance')}
                  >
                    Test Binance
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => this.testConnection('Bybit')}
                  >
                    Test Bybit
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Database Settings */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={2}>
                  <SettingsIcon color="primary" />
                  <Typography variant="h6">Database Configuration</Typography>
                </Box>

                <TextField
                  fullWidth
                  label="Database Host"
                  value={settings.database.host}
                  onChange={(e) => this.handleSettingChange('database', 'host', e.target.value)}
                />

                <TextField
                  fullWidth
                  label="Database Port"
                  type="number"
                  value={settings.database.port}
                  onChange={(e) => this.handleSettingChange('database', 'port', parseInt(e.target.value))}
                  sx={{ mt: 2 }}
                />

                <TextField
                  fullWidth
                  label="Database Name"
                  value={settings.database.name}
                  onChange={(e) => this.handleSettingChange('database', 'name', e.target.value)}
                  sx={{ mt: 2 }}
                />

                <TextField
                  fullWidth
                  label="Database User"
                  value={settings.database.user}
                  onChange={(e) => this.handleSettingChange('database', 'user', e.target.value)}
                  sx={{ mt: 2 }}
                />

                <TextField
                  fullWidth
                  label="Database Password"
                  type="password"
                  value={settings.database.password}
                  onChange={(e) => this.handleSettingChange('database', 'password', e.target.value)}
                  sx={{ mt: 2 }}
                />

                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => this.testConnection('Database')}
                  sx={{ mt: 2 }}
                >
                  Test Database Connection
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {/* Performance Settings */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={2}>
                  <Speed color="primary" />
                  <Typography variant="h6">Performance Settings</Typography>
                </Box>

                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.performance.cacheEnabled}
                      onChange={(e) => this.handleSettingChange('performance', 'cacheEnabled', e.target.checked)}
                    />
                  }
                  label="Enable Caching"
                />

                <TextField
                  fullWidth
                  label="Cache TTL (seconds)"
                  type="number"
                  value={settings.performance.cacheTTL}
                  onChange={(e) => this.handleSettingChange('performance', 'cacheTTL', parseInt(e.target.value))}
                  sx={{ mt: 2 }}
                />

                <TextField
                  fullWidth
                  label="Max Concurrent Requests"
                  type="number"
                  value={settings.performance.maxConcurrentRequests}
                  onChange={(e) => this.handleSettingChange('performance', 'maxConcurrentRequests', parseInt(e.target.value))}
                  sx={{ mt: 2 }}
                />

                <TextField
                  fullWidth
                  label="Request Timeout (seconds)"
                  type="number"
                  value={settings.performance.requestTimeout}
                  onChange={(e) => this.handleSettingChange('performance', 'requestTimeout', parseInt(e.target.value))}
                  sx={{ mt: 2 }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.performance.autoRestart}
                      onChange={(e) => this.handleSettingChange('performance', 'autoRestart', e.target.checked)}
                    />
                  }
                  label="Auto Restart on Failure"
                  sx={{ mt: 2 }}
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Notification Settings */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={2}>
                  <BugReport color="primary" />
                  <Typography variant="h6">Notification Settings</Typography>
                </Box>

                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Email Notifications
                    </Typography>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.notifications.emailEnabled}
                          onChange={(e) => this.handleSettingChange('notifications', 'emailEnabled', e.target.checked)}
                        />
                      }
                      label="Enable Email Notifications"
                    />

                    <TextField
                      fullWidth
                      label="Email Address"
                      type="email"
                      value={settings.notifications.emailAddress}
                      onChange={(e) => this.handleSettingChange('notifications', 'emailAddress', e.target.value)}
                      disabled={!settings.notifications.emailEnabled}
                      sx={{ mt: 2 }}
                    />
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Telegram Notifications
                    </Typography>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.notifications.telegramEnabled}
                          onChange={(e) => this.handleSettingChange('notifications', 'telegramEnabled', e.target.checked)}
                        />
                      }
                      label="Enable Telegram Notifications"
                    />

                    <TextField
                      fullWidth
                      label="Telegram Bot Token"
                      value={settings.notifications.telegramBotToken}
                      onChange={(e) => this.handleSettingChange('notifications', 'telegramBotToken', e.target.value)}
                      disabled={!settings.notifications.telegramEnabled}
                      sx={{ mt: 2 }}
                    />

                    <TextField
                      fullWidth
                      label="Telegram Chat ID"
                      value={settings.notifications.telegramChatId}
                      onChange={(e) => this.handleSettingChange('notifications', 'telegramChatId', e.target.value)}
                      disabled={!settings.notifications.telegramEnabled}
                      sx={{ mt: 2 }}
                    />
                  </Grid>
                </Grid>

                <Divider sx={{ my: 2 }} />

                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.notifications.tradeNotifications}
                      onChange={(e) => this.handleSettingChange('notifications', 'tradeNotifications', e.target.checked)}
                    />
                  }
                  label="Trade Notifications"
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.notifications.errorNotifications}
                      onChange={(e) => this.handleSettingChange('notifications', 'errorNotifications', e.target.checked)}
                    />
                  }
                  label="Error Notifications"
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  }
}

export default Settings;
