# 🦖 RAPTOR TRADING BOT - STRATEGY & MODEL RULES

## 📋 **CRITICAL: ALWAYS REMEMBER THIS STRATEGY AND MODEL**

This document contains the **COMPLETE** strategy and model architecture for the Raptor Trading Bot. 
**NEVER** deviate from this strategy without explicit user permission.

---

## 🧠 **MODEL ARCHITECTURE**

### **Model Location**: `/Model/`
### **Model Files**:
- `main.py` - Main model orchestrator
- `BinancePuller.py` - Data fetching from Binance
- `DataPuller.py` - Data processing and preparation
- `LiveModel.py` - ML model implementation
- `test_model.py` - Simplified test model

### **Model Configuration**:
```python
# From Model/main.py
interval = '2h'  # Candle interval
currencies = ['CHZUSDT','UNIUSDT','DOTUSDT','ETCUSDT','ANKRUSDT','BTCUSDT']
target_currency = 'CHZUSDT'  # Primary trading pair
model_output_path = 'model_output.csv'  # Output file
```

### **Model Output Format**:
```csv
timestamp, signal, quantity, coin
2025-08-29 14:30:00, BUY, 1, CHZ/USDT
2025-08-29 14:31:00, HOLD, 1, CHZ/USDT
2025-08-29 14:32:00, SELL, 1, CHZ/USDT
```

### **Model Schedule**:
- **Frequency**: Every 1 minute (changed from 10 seconds)
- **Method**: `schedule.every(1).minutes.do(perform_action)`
- **Output**: Writes to `model_output.csv` in project root

---

## 🎯 **TRADING STRATEGY - STEP BY STEP**

### **1. CSV-Driven Architecture**
The entire strategy is **CSV-driven** and **event-based**:
- Model writes signals to `model_output.csv`
- Main bot continuously monitors this file
- Bot processes signals and executes trades
- All actions logged to `bot_output_auto.csv`

### **2. Signal Processing Flow**

#### **Step 1: CSV Monitoring**
```python
# From original main.py (commented section)
while True:
    if os.stat(model).st_size == 0:  # If file is empty
        print("waiting for signals...\n")
        await asyncio.sleep(1)
        continue
    
    # Process the last line if file is not empty
    result = get_last_line_of_csv(model, last_processed_timestamp)
    if result is None:
        await asyncio.sleep(1)
        continue
```

#### **Step 2: Signal Parsing**
```python
# Parse the CSV line
line_number, last_line = result
trade = Trade(line_number, *last_line)
coin, base_coin = trade.pair.split('/')
wallet = Wallet(coin)
wallet.update_wallet()
```

#### **Step 3: Hold Logic Check**
```python
# CRITICAL: Force HOLD if bot coin > USDT
if wallet.bot_coin_amount > wallet.usdt_amount:
    trade.action = "HOLD"
```

### **3. Trade Execution Logic**

#### **BUY Signal Processing**:
```python
if trade.action == "BUY":
    wallet.update_wallet()
    start_time = time.time()
    amount = wallet.usdt_amount - 0.5  # Leave 0.5 USDT for fees
    
    # Execute BUY order
    receipt = await ut.make_order(cur, conn, client, logger, coin, base_coin, amount, "BUY", USD_FIAT, receipt, test_order)
    end_time = time.time()
    trade.execution_time = end_time - start_time
    receipt.execution_time = trade.execution_time

    # Log to CSV
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            receipt.order_id,
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            receipt.type,
            receipt.symbol,
            receipt.quantity,
            receipt.fees_amount,
            receipt.price,
            receipt.side,
            receipt.execution_time
        ])
    
    # Play sound and print confirmation
    Sounds.bot_sounds.buy_sound()
    print(f"{Fore.GREEN}{trade}{Style.RESET_ALL} , trade was placed \n")

    # INITIATE STOP LOSS TRACKING
    initial_price = receipt.price
    tracker = CoinTracker(initial_price, coin)
    print("STOPLOSS INITIATED!")
    tracker.start_tracking()
```

#### **HOLD Signal Processing**:
```python
elif trade.action == "HOLD":
    hold_data = trade.repr_hold_csv()
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(hold_data)
    print(f"{Fore.YELLOW}{trade.__repr__()}{Style.RESET_ALL} , no trade was placed.\n")
    order_number = line_number - 1
```

### **4. Stop Loss Management**

#### **Stop Loss Initialization**:
```python
# After BUY order execution
initial_price = receipt.price
tracker = CoinTracker(initial_price, coin)
print("STOPLOSS INITIATED!")
tracker.start_tracking()
```

#### **Stop Loss Monitoring Loop**:
```python
while True:
    # Log current status
    with open(stoploss_file, 'a') as sf:
        sf.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {coin} - Current price: {tracker.current_price:.9f} USDT, Highest Limit: {tracker.current_price_limit:.9f} USDT\n")
        coin_value_in_usdt = get_asset_balance_in_usdt(coin)
        sf.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Available {coin} balance in USDT: {coin_value_in_usdt:.2f} USDT\n")

    # Check if stop loss triggered
    if tracker.current_price < tracker.current_price_limit:
        tracker.stop_tracking()
        
        # EXECUTE SELL ORDER
        wallet.update_wallet()
        start_time = time.time()
        amount = wallet.bot_coin_amount - 0.5  # Leave some for fees
        
        receipt = await ut.make_order(cur, conn, client, logger, coin, base_coin, amount, "SELL", USD_FIAT, receipt, test_order)
        end_time = time.time()      
        trade.execution_time = end_time - start_time
        receipt.execution_time = trade.execution_time                            
        
        # Play sound and log
        Sounds.bot_sounds.sell_sound()
        print(f"STOPLOSS: SOLD ALL {coin}")
        
        # Log stop loss
        with open(stoploss_file, 'a') as sf:
            sf.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - STOPLOSS: SOLD ALL {coin}\n")

        # Log to CSV
        with open(csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                receipt.order_id,
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                receipt.type,
                receipt.symbol,
                receipt.quantity,
                receipt.fees_amount,
                receipt.price,
                receipt.side,
                receipt.execution_time
            ])
        order_number += 1
        break

    await asyncio.sleep(1)  # Check every second
```

---

## 💼 **WALLET MANAGEMENT**

### **Wallet Class Structure**:
```python
class Wallet:
    def __init__(self, coin):
        self.bot_coin = coin
        self.bot_coin_amount = 0.0  # Amount of bot coin held
        self.usdt_amount = 0.0      # Amount of USDT held
        self.update_wallet()        # Initialize wallet

    def update_wallet(self):
        """Fetches current balances from Binance API"""
        # API call to get account balances
        # Updates bot_coin_amount and usdt_amount

    def convert_to_usdt(self):
        """Converts bot_coin_amount to USDT equivalent"""
        # API call to get current price
        # Returns USDT value of bot coin holdings
```

### **Critical Wallet Logic**:
```python
# ALWAYS check this before processing signals
if wallet.bot_coin_amount > wallet.usdt_amount:
    trade.action = "HOLD"  # Force HOLD to prevent over-trading
```

---

## 📊 **CSV FILE STRUCTURES**

### **1. model_output.csv** (Model Output):
```csv
timestamp, signal, quantity, coin
2025-08-29 14:30:00, BUY, 1, CHZ/USDT
2025-08-29 14:31:00, HOLD, 1, CHZ/USDT
2025-08-29 14:32:00, SELL, 1, CHZ/USDT
```

### **2. bot_output_auto.csv** (Bot Trades):
```csv
Order Id,Order Datetime,Order Type,Order Symbol,Order Quantity,Order Fees Amount,Order Price,Order Side,Order Execution Time
TEST_1234567890,2025-08-29 14:30:00,MARKET,CHZUSDT,100,0.005,0.0500,BUY,0.1
TEST_1234567891,2025-08-29 14:35:00,MARKET,CHZUSDT,100,0.005,0.0490,SELL,0.1
```

### **3. stoploss.txt** (Stop Loss Log):
```
2025-08-29 14:30:00 - CHZ - Current price: 0.050000000 USDT, Highest Limit: 0.049000000 USDT
2025-08-29 14:30:00 - Available CHZ balance in USDT: 5.00 USDT
2025-08-29 14:35:00 - STOPLOSS: SOLD ALL CHZ
```

---

## 🔧 **CRITICAL COMPONENTS**

### **1. Trade Class**:
```python
class Trade:
    def __init__(self, line_number, timestamp, action, quantity, pair, execution_time=None):
        self.line_number = line_number
        self.timestamp = timestamp
        self.action = action.strip()
        self.quantity = float(quantity)
        self.pair = pair.strip()
        self.execution_time = execution_time

    def repr_hold_csv(self):
        return [
            -1,
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "@MARKETORDER",
            self.pair,
            self.quantity,
            -1,
            -1,
            self.action,
            0
        ]
```

### **2. CSV Reading Function**:
```python
def get_last_line_of_csv(file_path, last_processed_timestamp):
    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            last_line = None
            line_number = 0
            for last_line in reader:
                line_number += 1

            if last_line is not None:
                current_timestamp = last_line[0].strip()
                if current_timestamp == last_processed_timestamp:
                    return None
                return (line_number, last_line)

        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
```

### **3. Stop Loss Tracker**:
```python
# From ver_1.stop_loss import CoinTracker, get_asset_balance_in_usdt
tracker = CoinTracker(initial_price, coin)
tracker.start_tracking()
# Monitors price and triggers sell when price < limit
```

---

## 🎵 **SOUND SYSTEM**

### **Sound Integration**:
```python
import Sounds.bot_sounds

# Play sounds on trade execution
Sounds.bot_sounds.buy_sound()   # On BUY
Sounds.bot_sounds.sell_sound()  # On SELL/Stop Loss
```

---

## 📁 **FILE STRUCTURE**

```
bot2025_centralized_api_integrated/
├── Model/
│   ├── main.py              # Main model orchestrator
│   ├── BinancePuller.py     # Data fetching
│   ├── DataPuller.py        # Data processing
│   ├── LiveModel.py         # ML model
│   └── test_model.py        # Test model
├── Bot/
│   ├── main.py              # Original main (commented strategy)
│   └── test_main.py         # Test implementation
├── model_output.csv         # Model signals
├── bot_output_auto.csv      # Bot trades
├── stoploss.txt            # Stop loss logs
└── STRATEGY_AND_MODEL_RULES.md  # This file
```

---

## ⚠️ **CRITICAL RULES - NEVER DEVIATE**

### **1. CSV-Driven Architecture**:
- ✅ Model MUST output to `model_output.csv`
- ✅ Bot MUST read from `model_output.csv`
- ✅ Bot MUST log to `bot_output_auto.csv`
- ❌ NEVER use direct API calls for signals

### **2. Hold Logic**:
- ✅ ALWAYS check: `if wallet.bot_coin_amount > wallet.usdt_amount`
- ✅ Force HOLD if condition is true
- ❌ NEVER skip this check

### **3. Stop Loss Management**:
- ✅ ALWAYS initiate stop loss after BUY
- ✅ Monitor price every second
- ✅ Sell ALL when price < limit
- ❌ NEVER skip stop loss

### **4. File Monitoring**:
- ✅ Check if CSV file is empty
- ✅ Track last processed timestamp
- ✅ Avoid duplicate processing
- ❌ NEVER process same signal twice

### **5. Error Handling**:
- ✅ Handle CSV reading errors
- ✅ Handle API connection errors
- ✅ Log all errors
- ❌ NEVER crash on single error

---

## 🔄 **IMPLEMENTATION CHECKLIST**

When implementing or modifying the bot:

- [ ] Model outputs to `model_output.csv` every 1 minute
- [ ] Bot reads `model_output.csv` continuously
- [ ] Bot checks wallet balance before each signal
- [ ] Bot forces HOLD if bot_coin > usdt_amount
- [ ] Bot executes BUY orders with proper logging
- [ ] Bot initiates stop loss after BUY
- [ ] Bot monitors price every second
- [ ] Bot sells ALL on stop loss trigger
- [ ] Bot logs all trades to `bot_output_auto.csv`
- [ ] Bot logs stop loss to `stoploss.txt`
- [ ] Bot plays sounds on trade execution
- [ ] Bot handles all errors gracefully

---

## 📝 **NOTES**

1. **This is the ONLY valid strategy** - any deviation requires explicit user permission
2. **The model MUST output every 1 minute** - not faster, not slower
3. **Stop loss is MANDATORY** - no trades without stop loss
4. **CSV files are the source of truth** - never bypass them
5. **Wallet balance check is CRITICAL** - prevents over-trading
6. **Sound system provides user feedback** - always implement
7. **Error handling is essential** - bot must never crash

---

**END OF STRATEGY AND MODEL RULES**
**ALWAYS REFER TO THIS DOCUMENT BEFORE MAKING ANY CHANGES**
