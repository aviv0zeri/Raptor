# 🤖 Raptor Model Developer Guide

Welcome to the Raptor Trading System! This guide will help you create models that work perfectly with our signal wall and dashboard.

## 🌟 Why Your Model Needs to Follow Our Format

Think of our system like a universal translator. Just like how people from different countries need to speak the same language to understand each other, all models need to send signals in the same format so our dashboard can understand them.

**Benefits of following our format:**
- ✅ Your signals will appear on the beautiful dashboard
- ✅ You can use our WebSocket system for real-time updates
- ✅ Your model will work with our existing infrastructure
- ✅ Easy to integrate with other parts of the system

## 📡 How the Signal System Works

### The Signal Journey (Like a Message in a Bottle!)

1. **Your Model Makes a Decision** 🧠
   - Your model analyzes market data
   - It decides: BUY, SELL, or HOLD
   - It calculates how confident it is (0.0 to 1.0)

2. **Package the Signal** 📦
   - Wrap your decision in our special JSON format
   - Include all the required information
   - Add a timestamp so we know when it was made

3. **Send to the API** 🚀
   - POST your signal to `http://localhost:5050/api/model/signal`
   - The API server acts like a post office
   - It makes sure your signal is in the right format

4. **Broadcast to Dashboard** 📺
   - The webhook server receives your signal
   - It broadcasts it to all connected dashboards via WebSocket
   - Your signal appears on the beautiful signal wall!

## 🎯 Required Signal Format

Your model MUST send signals in this exact JSON format:

```json
{
  "type": "model_signal",
  "data": {
    "timestamp": "2025-09-04T22:43:43.123Z",
    "signal": "BUY",
    "confidence": 0.75,
    "reasoning": "Model detected strong bullish pattern",
    "model": "your_model_name",
    "interval": "1m"
  },
  "timestamp": "2025-09-04T22:43:43.123Z"
}
```

### Field Explanations

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | ✅ | Always "model_signal" |
| `data.timestamp` | string | ✅ | When your model made the decision (ISO 8601 format) |
| `data.signal` | string | ✅ | "BUY", "SELL", or "HOLD" |
| `data.confidence` | number | ✅ | How sure your model is (0.0 to 1.0) |
| `data.reasoning` | string | ✅ | Why your model made this decision |
| `data.model` | string | ✅ | Your model's name (e.g., "my_awesome_model") |
| `data.interval` | string | ✅ | How often your model runs ("1m", "5m", "1h", etc.) |
| `timestamp` | string | ✅ | When you sent this message (ISO 8601 format) |

## 🔧 Technical Requirements

### WebSocket Connection
- **Port**: 8767
- **URL**: `ws://localhost:8767`
- **Purpose**: Real-time communication with the dashboard

### API Endpoint
- **URL**: `http://localhost:5050/api/model/signal`
- **Method**: POST
- **Content-Type**: application/json
- **Timeout**: 10 seconds

### Signal Values
- **1** = BUY signal
- **0** = HOLD signal  
- **-1** = SELL signal

## 📝 Example Model Implementation

Here's a simple example of how to send a signal:

```python
import requests
import json
from datetime import datetime

def send_signal(signal_value, confidence, reasoning, model_name, interval):
    """
    Send a trading signal to the Raptor system
    """
    # Convert signal value to string
    signal_map = {1: "BUY", 0: "HOLD", -1: "SELL"}
    signal_str = signal_map.get(signal_value, "HOLD")
    
    # Create the signal payload
    payload = {
        "type": "model_signal",
        "data": {
            "timestamp": datetime.now().isoformat(),
            "signal": signal_str,
            "confidence": confidence,
            "reasoning": reasoning,
            "model": model_name,
            "interval": interval
        },
        "timestamp": datetime.now().isoformat()
    }
    
    # Send to API
    try:
        response = requests.post(
            "http://localhost:5050/api/model/signal",
            json=payload,
            timeout=10
        )
        print(f"Signal sent successfully: {response.status_code}")
        return True
    except Exception as e:
        print(f"Failed to send signal: {e}")
        return False

# Example usage
send_signal(
    signal_value=1,  # BUY
    confidence=0.85,
    reasoning="Strong bullish momentum detected",
    model_name="my_awesome_model",
    interval="1m"
)
```

## 🎨 Integration with Signal Wall

The Signal Wall (frontend dashboard) expects signals in this format and will:

1. **Display Recent Signals** 📊
   - Shows the last 50 signals in a beautiful table
   - Updates in real-time as new signals arrive
   - Color-codes BUY (green), SELL (red), HOLD (yellow)

2. **Show Model Status** 🔄
   - Displays if your model is running
   - Shows when it's ready to generate signals
   - Indicates if it's currently generating signals

3. **Real-time Updates** ⚡
   - Uses WebSocket for instant updates
   - No need to refresh the page
   - Signals appear immediately when sent

## 🚀 Getting Started

1. **Create Your Model** 🧠
   - Build your trading logic
   - Make sure it can generate BUY/SELL/HOLD decisions
   - Calculate confidence scores

2. **Test the Format** 🧪
   - Send a test signal using the example code above
   - Check that it appears on the dashboard
   - Verify all fields are displayed correctly

3. **Integrate with Your Model** 🔗
   - Add the signal sending code to your model
   - Make sure it sends signals at the right intervals
   - Test with different signal types

4. **Monitor and Improve** 📈
   - Watch your signals on the dashboard
   - Analyze performance over time
   - Adjust your model based on results

## 🆘 Troubleshooting

### Signal Not Appearing on Dashboard?
- ✅ Check that your JSON format is exactly correct
- ✅ Verify you're sending to the right API endpoint
- ✅ Make sure the API server is running
- ✅ Check that the WebSocket connection is working

### WebSocket Connection Issues?
- ✅ Ensure the webhook server is running on port 8767
- ✅ Check that your frontend is connecting to the right URL
- ✅ Verify no firewall is blocking the connection

### API Server Not Responding?
- ✅ Make sure the API server is running on port 5050
- ✅ Check the API server logs for errors
- ✅ Verify your request format is correct

## 🎯 Best Practices

1. **Always Include All Required Fields** - Missing fields will cause errors
2. **Use Proper Timestamps** - ISO 8601 format is required
3. **Set Realistic Confidence Scores** - Don't always use 1.0
4. **Write Clear Reasoning** - Help users understand your model's decisions
5. **Test Thoroughly** - Send test signals before going live
6. **Handle Errors Gracefully** - Your model should continue working even if signal sending fails

## 🔮 Future Enhancements

We're planning to add:
- 🔐 HTTPS support with authentication
- 📊 Advanced analytics and backtesting
- 🤖 Multiple model comparison tools
- 📱 Mobile app support
- 🌐 Cloud deployment options

---

**Happy Trading! 🚀**

Remember: The key to success is following the format exactly. Our system is designed to be flexible and powerful, but it needs signals in the right format to work properly. Take your time to understand the system, and you'll be creating amazing trading models in no time!
