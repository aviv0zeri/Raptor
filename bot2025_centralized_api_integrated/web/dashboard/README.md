# 🌟 Cosmic Trading Bot - React Dashboard

A modern, responsive React dashboard for monitoring and controlling the Cosmic Trading Bot system.

## 🚀 Features

### 📊 Trading Dashboard
- **Real-time Trading Data**: Live balance, profit/loss, active positions
- **Price Charts**: Interactive price charts with Recharts
- **Recent Trades**: Live trade history with status indicators
- **Performance Metrics**: Win rate, total trades, and key statistics

### 📋 Logs Viewer
- **Real-time Log Streaming**: Live log updates with auto-refresh
- **Advanced Filtering**: Filter by log level, source, and search terms
- **Log Export**: Download logs in various formats
- **Multi-source Logs**: View logs from Model, Main, Stop Loss, and System

### 🧪 Test Runner
- **Comprehensive Testing**: API, Model, Trade Execution, Stop Loss tests
- **Configurable Test Parameters**: Duration, risk level, test mode
- **Real-time Test Results**: Live test execution and results
- **System Metrics**: CPU, Memory, Network, Disk monitoring

### 📊 System Status
- **Component Health**: Monitor Model, Main, Database, API status
- **Resource Monitoring**: Real-time CPU, Memory, Disk, Network usage
- **System Alerts**: Active alerts and notifications
- **Quick Actions**: Balance check, position view, diagnostics

### ⚙️ Settings
- **Trading Configuration**: Risk management, position sizing, stop loss
- **API Management**: Binance and Bybit API key configuration
- **Database Settings**: PostgreSQL connection configuration
- **Performance Tuning**: Caching, timeouts, concurrent requests
- **Notifications**: Email and Telegram notification setup

## 🛠️ Technology Stack

- **React 18**: Modern React with hooks and functional components
- **Material-UI (MUI)**: Professional UI components and theming
- **Vite**: Fast build tool and development server
- **Recharts**: Beautiful and responsive charts
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls

## 📦 Installation

### Prerequisites
- Node.js 16+ 
- npm or yarn
- Cosmic Trading Bot backend running

### Setup
```bash
# Navigate to the dashboard directory
cd web/dashboard

# Install dependencies
npm install

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:5173`

## 🚀 Usage

### Development
```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Production
```bash
# Build the application
npm run build

# Serve the built files
npm run preview
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the dashboard directory:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:5000/api
VITE_WS_URL=ws://localhost:5000/ws

# Feature Flags
VITE_ENABLE_WEBSOCKETS=true
VITE_ENABLE_REAL_TIME=true

# Development
VITE_DEV_MODE=true
```

### API Integration
The dashboard is designed to work with the Cosmic Trading Bot backend. Update the API endpoints in the components to match your backend configuration.

## 📱 Responsive Design

The dashboard is fully responsive and works on:
- Desktop (1920x1080+)
- Tablet (768px+)
- Mobile (320px+)

## 🎨 Theming

The dashboard uses a dark theme optimized for trading applications. The theme can be customized in `src/App.jsx`:

```javascript
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#667eea',
    },
    secondary: {
      main: '#764ba2',
    },
    // ... more theme options
  },
});
```

## 🔌 API Endpoints

The dashboard expects the following API endpoints:

### Trading Data
- `GET /api/trading/status` - Get trading status
- `GET /api/trading/balance` - Get account balance
- `GET /api/trading/positions` - Get active positions
- `GET /api/trading/history` - Get trade history

### Logs
- `GET /api/logs` - Get logs with filtering
- `GET /api/logs/stream` - WebSocket for real-time logs

### System
- `GET /api/system/status` - Get system status
- `GET /api/system/metrics` - Get system metrics

### Tests
- `POST /api/tests/run` - Run tests
- `GET /api/tests/results` - Get test results

### Settings
- `GET /api/settings` - Get settings
- `PUT /api/settings` - Update settings

## 🧪 Testing

```bash
# Run unit tests
npm run test

# Run tests with coverage
npm run test:coverage

# Run e2e tests
npm run test:e2e
```

## 📦 Build & Deploy

### Build for Production
```bash
npm run build
```

This creates a `dist` folder with optimized production files.

### Deploy to Static Hosting
The built files can be deployed to any static hosting service:
- Netlify
- Vercel
- GitHub Pages
- AWS S3
- Nginx

### Docker Deployment
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🔒 Security

- API keys are stored securely in the backend
- HTTPS is recommended for production
- CORS is configured for the backend domain
- Input validation on all forms

## 🐛 Troubleshooting

### Common Issues

1. **Dashboard not loading**
   - Check if the backend is running
   - Verify API endpoints are accessible
   - Check browser console for errors

2. **Real-time updates not working**
   - Ensure WebSocket connection is established
   - Check network connectivity
   - Verify WebSocket URL configuration

3. **Build errors**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility
   - Verify all dependencies are installed

### Debug Mode
Enable debug mode by setting `VITE_DEV_MODE=true` in your `.env` file.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review the API documentation
- Open an issue on GitHub
- Contact the development team

---

**🌟 Happy Trading with the Cosmic Bot Dashboard!**
