#!/bin/bash

# 🌟 Cosmic Trading Bot Installation Script
# The cosmic installer that sets up everything you need

echo "🌟 Welcome to the Cosmic Trading Bot Installation!"
echo "=================================================="

# Check if Python 3.8+ is installed
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version is installed (meets requirement: $required_version+)"
else
    echo "❌ Python 3.8+ is required. Current version: $python_version"
    echo "💡 Please install Python 3.8 or higher and try again."
    exit 1
fi

# Check if pip is installed
echo "🔍 Checking pip installation..."
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 is installed"
else
    echo "❌ pip3 is not installed"
    echo "💡 Please install pip3 and try again."
    exit 1
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing Python packages..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Python packages installed successfully"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Create .env file if it doesn't exist
echo "🔧 Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ Created .env file from env.example"
        echo "💡 Please edit .env file with your actual configuration values"
    else
        echo "⚠️ env.example not found, creating basic .env file..."
        cat > .env << EOF
# 🌟 Trading Bot Environment Configuration
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading_bot
DB_USER=postgres
DB_PASSWORD=your_database_password

# Binance API Configuration
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here

# Trading Configuration
ENABLE_PAPER_TRADING=true
DEFAULT_EXCHANGE=binance

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
ENABLE_CONSOLE_LOGGING=true

# Performance Configuration
ENABLE_CACHING=true
CACHE_TTL=300
EOF
        echo "✅ Created basic .env file"
        echo "💡 Please edit .env file with your actual configuration values"
    fi
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p logs data/output data/backup config scripts tests docs
echo "✅ Directory structure created"

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x install.sh
echo "✅ Scripts made executable"

# Install as development package
echo "🔧 Installing as development package..."
pip install -e .
echo "✅ Development package installed"

echo ""
echo "🎉 Installation completed successfully!"
echo "======================================"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your actual configuration values"
echo "2. Set up your database (PostgreSQL recommended)"
echo "3. Configure your Binance API keys"
echo "4. Run the bot: python run.py"
echo ""
echo "🚀 Available commands:"
echo "  python run.py              # Run in parallel mode (default)"
echo "  python run.py sequential   # Run in sequential mode"
echo "  python run.py model        # Run only the model"
echo "  python run.py main         # Run only the main bot"
echo "  python run.py web          # Run only the web dashboard"
echo ""
echo "📚 For more information, see README.md and PROJECT_STRUCTURE.md"
echo ""
echo "🌟 Happy trading! 🌟"
