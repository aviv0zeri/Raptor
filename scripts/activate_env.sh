#!/bin/bash
# 🌟 Virtual Environment Activation Script
# Activates the trading bot's virtual environment

echo "🌟 Activating Trading Bot Virtual Environment..."
source venv/bin/activate
echo "✅ Virtual environment activated!"
echo "🐍 Python interpreter: $(which python)"
echo "📦 Python version: $(python --version)"
echo ""
echo "🚀 Ready to run the trading bot!"
echo "💡 Use 'python run.py' to start the bot"
echo "💡 Use 'python test_dashboard.py' to test the dashboard"
