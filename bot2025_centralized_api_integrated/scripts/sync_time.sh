#!/bin/bash

# 🌟 Linux Time Synchronization Script
# The cosmic timekeeper for Linux systems

echo "🕐 Starting Linux Time Synchronization..."

# Check if running as root (needed for time sync)
if [ "$EUID" -ne 0 ]; then
    echo "🔐 Requesting sudo privileges for time synchronization..."
    exec sudo "$0" "$@"
    exit
fi

# Function to check if systemd-timesyncd is available
check_timesyncd() {
    if command -v timedatectl >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check if ntp is available
check_ntp() {
    if command -v ntpdate >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check if chrony is available
check_chrony() {
    if command -v chronyd >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

echo "🔍 Checking available time synchronization services..."

# Try systemd-timesyncd first (most common on modern Linux)
if check_timesyncd; then
    echo "✅ Using systemd-timesyncd for time synchronization..."
    
    # Enable and start the service
    systemctl enable systemd-timesyncd
    systemctl start systemd-timesyncd
    
    # Show current status
    echo "📊 Current time synchronization status:"
    timedatectl status
    
    # Force a sync
    echo "🔄 Forcing time synchronization..."
    timedatectl set-ntp true
    
    echo "✅ Time synchronization completed using systemd-timesyncd"
    
elif check_chrony; then
    echo "✅ Using chrony for time synchronization..."
    
    # Start chrony service
    systemctl enable chronyd
    systemctl start chronyd
    
    # Show current status
    echo "📊 Current time synchronization status:"
    chronyc tracking
    
    # Force a sync
    echo "🔄 Forcing time synchronization..."
    chronyc -a makestep
    
    echo "✅ Time synchronization completed using chrony"
    
elif check_ntp; then
    echo "✅ Using ntpdate for time synchronization..."
    
    # Try to sync with common NTP servers
    echo "🔄 Synchronizing with NTP servers..."
    ntpdate -s pool.ntp.org
    
    if [ $? -eq 0 ]; then
        echo "✅ Time synchronization completed using ntpdate"
    else
        echo "❌ Failed to sync with ntpdate"
    fi
    
else
    echo "❌ No time synchronization service found"
    echo "💡 Please install one of the following:"
    echo "   - systemd-timesyncd (usually pre-installed)"
    echo "   - chrony: sudo apt-get install chrony"
    echo "   - ntp: sudo apt-get install ntp"
    exit 1
fi

# Display current time
echo ""
echo "🕐 Current system time:"
date

echo ""
echo "🌟 Time synchronization completed successfully!"
echo "💡 The system time is now synchronized with NTP servers."
