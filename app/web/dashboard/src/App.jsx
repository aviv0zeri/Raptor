import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import DashboardLayout from './components/DashboardLayout';
import TradingDashboard from './components/TradingDashboard';
import LogsViewer from './components/LogsViewer';
import TestRunner from './components/TestRunner';
import SystemStatus from './components/SystemStatus';
import Settings from './components/Settings';
import SignalWall from './components/SignalWall';


// 🌟 Purple Theme with Cosmic Styling
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#9c27b0', // Purple
      light: '#ba68c8',
      dark: '#7b1fa2',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#e1bee7', // Light purple
      light: '#f3e5f5',
      dark: '#c2185b',
      contrastText: '#000000',
    },
    background: {
      default: '#0a0a0a',
      paper: '#1a1a1a',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b3b3b3',
    },
    success: {
      main: '#4caf50',
      light: '#81c784',
      dark: '#388e3c',
    },
    error: {
      main: '#f44336',
      light: '#e57373',
      dark: '#d32f2f',
    },
    warning: {
      main: '#ff9800',
      light: '#ffb74d',
      dark: '#f57c00',
    },
    info: {
      main: '#2196f3',
      light: '#64b5f6',
      dark: '#1976d2',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
      background: 'linear-gradient(45deg, #9c27b0, #e1bee7)',
      backgroundClip: 'text',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
      color: '#9c27b0',
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 500,
      color: '#ba68c8',
    },
    h4: {
      fontSize: '1.25rem',
      fontWeight: 500,
      color: '#e1bee7',
    },
    h5: {
      fontSize: '1.125rem',
      fontWeight: 500,
      color: '#f3e5f5',
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
      color: '#f3e5f5',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
          boxShadow: '0 4px 8px rgba(156, 39, 176, 0.3)',
          '&:hover': {
            boxShadow: '0 6px 12px rgba(156, 39, 176, 0.4)',
            transform: 'translateY(-2px)',
          },
          transition: 'all 0.3s ease',
        },
        contained: {
          background: 'linear-gradient(45deg, #9c27b0, #ba68c8)',
          '&:hover': {
            background: 'linear-gradient(45deg, #7b1fa2, #9c27b0)',
          },
        },
        outlined: {
          borderColor: '#9c27b0',
          color: '#9c27b0',
          '&:hover': {
            borderColor: '#ba68c8',
            backgroundColor: 'rgba(156, 39, 176, 0.1)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          background: 'linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%)',
          border: '1px solid rgba(156, 39, 176, 0.2)',
          boxShadow: '0 8px 32px rgba(156, 39, 176, 0.1)',
          backdropFilter: 'blur(10px)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          background: 'linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(90deg, #9c27b0, #7b1fa2)',
          boxShadow: '0 4px 20px rgba(156, 39, 176, 0.3)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          background: 'linear-gradient(180deg, #1a1a1a 0%, #2a2a2a 100%)',
          borderRight: '1px solid rgba(156, 39, 176, 0.2)',
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '4px 8px',
          '&:hover': {
            backgroundColor: 'rgba(156, 39, 176, 0.1)',
          },
          '&.Mui-selected': {
            backgroundColor: 'rgba(156, 39, 176, 0.2)',
            '&:hover': {
              backgroundColor: 'rgba(156, 39, 176, 0.3)',
            },
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          fontWeight: 600,
        },
        colorPrimary: {
          backgroundColor: 'rgba(156, 39, 176, 0.2)',
          color: '#9c27b0',
          border: '1px solid rgba(156, 39, 176, 0.3)',
        },
        colorSuccess: {
          backgroundColor: 'rgba(76, 175, 80, 0.2)',
          color: '#4caf50',
          border: '1px solid rgba(76, 175, 80, 0.3)',
        },
        colorError: {
          backgroundColor: 'rgba(244, 67, 54, 0.2)',
          color: '#f44336',
          border: '1px solid rgba(244, 67, 54, 0.3)',
        },
      },
    },
  },
});

// 🌟 Sounds Interface for Frontend
class FrontendSoundsInterface {
  constructor() {
    this.enabled = true;
    this.volume = 0.5;
    this.audioContext = null;
    this.initAudioContext();
  }

  initAudioContext() {
    try {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    } catch (error) {
      console.warn('Audio context not supported:', error);
    }
  }

  playTone(frequency, duration, type = 'sine') {
    if (!this.enabled || !this.audioContext) return;

    try {
      const oscillator = this.audioContext.createOscillator();
      const gainNode = this.audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(this.audioContext.destination);

      oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
      oscillator.type = type;

      gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
      gainNode.gain.linearRampToValueAtTime(this.volume * 0.3, this.audioContext.currentTime + 0.01);
      gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + duration);

      oscillator.start(this.audioContext.currentTime);
      oscillator.stop(this.audioContext.currentTime + duration);
    } catch (error) {
      console.warn('Error playing tone:', error);
    }
  }

  playOrderExecuted() {
    this.playTone(800, 0.3); // High pitch, short
  }

  playOrderCancelled() {
    this.playTone(400, 0.2); // Low pitch, very short
  }

  playErrorAlert() {
    this.playTone(200, 0.5); // Very low pitch, longer
  }

  playSuccessConfirmation() {
    this.playTone(1000, 0.4); // Very high pitch
  }

  playWarningNotification() {
    this.playTone(600, 0.3); // Medium pitch
  }

  playTradeSignal() {
    this.playTone(900, 0.2); // High pitch, short
  }

  playSystemStart() {
    this.playTone(500, 1.0); // Medium pitch, long
  }

  playSystemStop() {
    this.playTone(300, 0.8); // Low pitch, long
  }

  playBalanceUpdate() {
    this.playTone(700, 0.2); // Medium-high pitch
  }

  playProfitAlert() {
    this.playTone(1200, 0.3); // Very high pitch
  }

  playLossAlert() {
    this.playTone(150, 0.6); // Very low pitch, longer
  }

  setVolume(volume) {
    this.volume = Math.max(0, Math.min(1, volume));
  }

  enable() {
    this.enabled = true;
  }

  disable() {
    this.enabled = false;
  }
}

// Global sounds interface
window.soundsInterface = new FrontendSoundsInterface();

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <DashboardLayout>
          <Routes>
            <Route path="/" element={<SignalWall />} />
            <Route path="/logs" element={<LogsViewer />} />
            <Route path="/test" element={<TestRunner />} />
            <Route path="/status" element={<SystemStatus />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/wall" element={<SignalWall />} />
          </Routes>
        </DashboardLayout>
      </Router>
      

    </ThemeProvider>
  );
}

export default App;
