# 🦖 RAPTOR TRADING BOT - STRATEGY ANALYSIS

## 📋 Original Strategy Overview

The original main.py implements a **CSV-based trading strategy** where:

1. **Model Output**: ML model writes signals to `model_output.csv`
2. **Main Bot Reads**: Main bot continuously monitors the CSV file
3. **Signal Processing**: Processes BUY/HOLD signals and executes trades
4. **Stop Loss Management**: Implements dynamic stop-loss tracking

## 🔄 Trading Flow

### 1. Model Output Format
```
timestamp, signal, quantity, coin
2025-08-29 14:30:00, BUY, 1, CHZ/USDT
2025-08-29 14:31:00, HOLD, 1, CHZ/USDT
```

### 2. Main Bot Processing Steps

#### Step 1: CSV Monitoring
- Continuously reads `model_output.csv`
- Tracks last processed timestamp to avoid duplicates
- Waits for new signals

#### Step 2: Signal Processing
- **BUY Signal**: 
  - Check wallet balance
  - Execute BUY order
  - Initialize stop-loss tracker
  - Start monitoring price for stop-loss

- **HOLD Signal**:
  - Log as HOLD in bot output
  - No trade execution
  - Continue monitoring

#### Step 3: Stop Loss Management
- **Initialization**: After BUY, start tracking initial price
- **Dynamic Limit**: Calculate stop-loss limit based on initial price
- **Continuous Monitoring**: Check price every second
- **Stop Loss Trigger**: When price drops below limit → SELL ALL

### 3. Wallet Management
- **Balance Check**: Before BUY, ensure sufficient USDT
- **Hold Logic**: If bot_coin_amount > usdt_amount → Force HOLD
- **Real-time Updates**: Update wallet before each trade

## 🎯 Key Strategy Components

### 1. Risk Management
- **Stop Loss**: Automatic sell when price drops below calculated limit
- **Balance Protection**: Won't buy if insufficient funds
- **Hold Logic**: Prevents over-trading

### 2. Trade Execution
- **Market Orders**: Uses market orders for immediate execution
- **Fee Tracking**: Records all fees and execution times
- **Receipt System**: Detailed trade logging

### 3. CSV Output System
- **Bot Output**: `bot_output_auto.csv` - All executed trades
- **Model Output**: `model_output.csv` - ML model signals
- **Stop Loss Log**: `stoploss.txt` - Price monitoring data

## 🚨 What I Missed in Frontend Implementation

### 1. **CSV Reading Logic**
- Frontend doesn't read actual `model_output.csv`
- No real-time CSV monitoring
- Missing signal processing logic

### 2. **Stop Loss Implementation**
- No stop-loss tracking in frontend
- Missing price monitoring
- No automatic sell logic

### 3. **Wallet Integration**
- Fake wallet doesn't integrate with real trading logic
- No balance checking before trades
- Missing hold logic

### 4. **Trade Execution**
- No actual order placement
- Missing receipt system
- No fee tracking

### 5. **Real Strategy Flow**
- Frontend shows demo data instead of real strategy
- No CSV-based signal processing
- Missing the core trading algorithm

## 🔧 Required Fixes

### 1. Model Integration
- Make model output to `model_output.csv` every 1 minute
- Ensure proper CSV format

### 2. Frontend Strategy Implementation
- Add CSV reading functionality
- Implement real signal processing
- Add stop-loss monitoring
- Integrate with real wallet logic

### 3. Real Trading Logic
- Replace demo data with actual strategy
- Implement BUY/HOLD/SELL logic
- Add proper risk management

## 📊 Expected Behavior

1. **Model**: Outputs signals every 1 minute to CSV
2. **Main Bot**: Reads CSV, processes signals, executes trades
3. **Stop Loss**: Monitors prices, sells on trigger
4. **Frontend**: Shows real-time strategy execution
5. **Logs**: All actions logged to CSV files

The strategy is **CSV-driven** and **event-based**, not continuous trading. It waits for ML model signals and executes accordingly with proper risk management.
