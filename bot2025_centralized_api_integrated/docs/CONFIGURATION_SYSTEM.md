# 🔧 Configuration System Guide

## **Overview**

Your trading bot now uses a **unified environment variable system** for all configuration. This provides better security, flexibility, and consistency across all modules.

## **Configuration Sources**

### **1. Environment Variables (.env file) - PRIMARY SOURCE**
- **Location**: `/.env` (project root)
- **Purpose**: Contains all configuration including API keys, database settings, etc.
- **Security**: `.env` is in `.gitignore` to keep sensitive data out of version control
- **Usage**: All modules now load from this file

### **2. Hardcoded Config (config.py) - LEGACY**
- **Location**: `Bot/ver_1/tools/config/config.py`
- **Status**: **DEPRECATED** - Only kept for reference
- **Action**: Will be removed in future updates

## **Current Configuration**

### **API Keys (Updated)**
```bash
# .env file now contains your actual API keys
BINANCE_API_KEY=<REDACTED_BINANCE_API_KEY>
BINANCE_SECRET_KEY=<REDACTED_BINANCE_SECRET_KEY>
```

### **Database Configuration**
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading_bot
DB_USER=postgres
DB_PASSWORD=<REDACTED_DB_PASSWORD>
```

### **Trading Configuration**
```bash
DEFAULT_QUANTITY=1.0
MAX_POSITION_SIZE=100.0
RISK_PERCENTAGE=2.0
ENABLE_PAPER_TRADING=true
DEFAULT_EXCHANGE=binance
```

## **Modules Updated to Use .env**

✅ **main.py** - Main trading bot logic  
✅ **OrderTester_GUI.py** - GUI testing interface  
✅ **ORDERTESTER.py** - Command-line testing  
✅ **stop_loss.py** - Stop-loss system  
✅ **api_server.py** - Flask API backend  
✅ **config_manager.py** - Configuration manager  

## **How It Works**

### **Loading Environment Variables**
```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access configuration
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
DB_HOST = os.getenv('DB_HOST', 'localhost')  # with default
```

### **Configuration Manager**
```python
from Bot.ver_1.tools.config.config_manager import config_manager

# Get configuration values
api_key = config_manager.get('api', 'binance_api_key')
db_host = config_manager.get('database', 'host')
```

## **Benefits of This System**

1. **Security**: API keys are not hardcoded in source code
2. **Flexibility**: Easy to change settings without modifying code
3. **Environment Support**: Different configs for development/production
4. **Version Control Safe**: Sensitive data stays out of git
5. **Consistency**: All modules use the same configuration source

## **Managing Configuration**

### **Adding New Configuration**
1. Add to `.env` file:
   ```bash
   NEW_SETTING=value
   ```

2. Access in code:
   ```python
   new_value = os.getenv('NEW_SETTING', 'default_value')
   ```

### **Updating API Keys**
1. Edit `.env` file
2. Replace the placeholder values with your actual keys
3. Restart the application

### **Environment-Specific Configs**
You can create different .env files:
- `.env.development`
- `.env.production`
- `.env.testing`

## **Troubleshooting**

### **If API keys don't work:**
1. Check `.env` file exists and has correct keys
2. Ensure `python-dotenv` is installed
3. Verify `load_dotenv()` is called before accessing variables

### **If database connection fails:**
1. Check PostgreSQL is running
2. Verify database credentials in `.env`
3. Test connection manually

### **If configuration is not loading:**
1. Check file permissions on `.env`
2. Ensure `load_dotenv()` is called
3. Verify variable names match exactly

## **Migration Complete**

✅ **All modules now use .env**  
✅ **API keys are properly configured**  
✅ **Database connection working**  
✅ **Configuration system unified**  

Your trading bot is now using a modern, secure configuration system! 🚀
