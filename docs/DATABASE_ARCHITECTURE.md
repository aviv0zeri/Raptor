# 🗄️ Database Architecture & Improvement Guide

## 📊 Current Database Structure

### Overview
The Raptor trading system uses a hybrid database approach combining SQLite for structured data and CSV files for time-series data.

### Current Components

#### 1. SQLite Database (`app/modules/database/`)
- **Purpose**: Stores structured trading data, orders, and system state
- **Location**: `app/modules/database/database.py`
- **Tables**:
  - `orders` - Trading order records
  - `receipts` - Order execution receipts
  - `system_state` - Application state management

#### 2. CSV Files (`logs/`)
- **Purpose**: Time-series data storage for signals and logs
- **Files**:
  - `logs/model_output.csv` - Model-generated signals
  - `logs/bot/main.log` - Bot execution logs
  - `logs/model/real.log` - Real model logs
  - `logs/model/test.log` - Test model logs

#### 3. JSON Configuration (`data/`)
- **Purpose**: System configuration and data format definitions
- **Files**:
  - `data/api/signal_format.json` - Signal format specification
  - `data/api/data_transfer_classes.json` - Data transfer definitions
  - `data/api/api_routes.json` - API route documentation

## 🔧 Current Implementation Analysis

### Strengths ✅
1. **Simple Setup**: SQLite requires no server configuration
2. **Portable**: Database files can be easily moved/backed up
3. **Fast Reads**: Good performance for small to medium datasets
4. **ACID Compliance**: Reliable transaction handling
5. **JSON Integration**: Configuration-driven data validation

### Weaknesses ⚠️
1. **Limited Scalability**: SQLite doesn't handle high concurrency well
2. **No Real-time Sync**: Multiple instances can't share data easily
3. **Manual Backup**: No automated backup system
4. **Limited Analytics**: No built-in aggregation capabilities
5. **File-based Logs**: CSV logs are hard to query and analyze

## 🚀 Recommended Improvements

### Phase 1: Enhanced SQLite Setup (Immediate)

#### 1. Database Schema Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_orders_timestamp ON orders(timestamp);
CREATE INDEX idx_orders_symbol ON orders(symbol);
CREATE INDEX idx_signals_model ON signals(model_name);

-- Add signal storage table
CREATE TABLE signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    signal_type TEXT NOT NULL CHECK(signal_type IN ('BUY', 'SELL', 'HOLD')),
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    reasoning TEXT,
    model_name TEXT NOT NULL,
    interval TEXT NOT NULL,
    symbol TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. Connection Pooling
```python
# Implement connection pooling for better performance
import sqlite3
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.pool_size = 5
        self.connections = []
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
```

#### 3. Automated Backup System
```python
# Daily automated backups
import shutil
from datetime import datetime

def backup_database():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"backups/raptor_db_{timestamp}.db"
    shutil.copy2("app/modules/database/raptor.db", backup_path)
    # Keep only last 30 days of backups
    cleanup_old_backups()
```

### Phase 2: Time-Series Database Integration (Medium-term)

#### 1. InfluxDB for Signal Data
```python
# Replace CSV signal storage with InfluxDB
from influxdb_client import InfluxDBClient

class SignalStorage:
    def __init__(self):
        self.client = InfluxDBClient(
            url="http://localhost:8086",
            token="your-token",
            org="raptor"
        )
    
    def store_signal(self, signal_data):
        point = Point("signals") \
            .tag("model", signal_data["model"]) \
            .tag("symbol", signal_data["symbol"]) \
            .field("signal", signal_data["signal"]) \
            .field("confidence", signal_data["confidence"]) \
            .time(signal_data["timestamp"])
        
        self.client.write_api().write(bucket="trading", record=point)
```

#### 2. Redis for Real-time Data
```python
# Use Redis for real-time signal broadcasting
import redis

class RealTimeSignalBroadcaster:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    def broadcast_signal(self, signal_data):
        # Store in Redis with TTL
        self.redis_client.setex(
            f"signal:{signal_data['timestamp']}", 
            3600,  # 1 hour TTL
            json.dumps(signal_data)
        )
        # Publish to WebSocket subscribers
        self.redis_client.publish("signals", json.dumps(signal_data))
```

### Phase 3: Full Database Migration (Long-term)

#### 1. PostgreSQL for Production
```python
# Production-ready PostgreSQL setup
import psycopg2
from sqlalchemy import create_engine

class ProductionDatabase:
    def __init__(self):
        self.engine = create_engine(
            'postgresql://user:password@localhost/raptor',
            pool_size=20,
            max_overflow=30
        )
    
    def setup_tables(self):
        # Create production tables with proper constraints
        pass
```

#### 2. Database Migration System
```python
# Alembic for database migrations
from alembic import command
from alembic.config import Config

def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
```

## 📈 Performance Optimization

### 1. Query Optimization
```sql
-- Use prepared statements
-- Add proper indexes
-- Implement query result caching
-- Use connection pooling
```

### 2. Data Archiving
```python
# Archive old data to reduce database size
def archive_old_signals(days_old=90):
    cutoff_date = datetime.now() - timedelta(days=days_old)
    # Move old signals to archive table
    # Compress archived data
```

### 3. Monitoring & Analytics
```python
# Add database performance monitoring
class DatabaseMonitor:
    def track_query_performance(self):
        # Log slow queries
        # Monitor connection pool usage
        # Track database size growth
        pass
```

## 🔒 Security Considerations

### 1. Data Encryption
- Encrypt sensitive data at rest
- Use connection encryption (SSL/TLS)
- Implement proper access controls

### 2. Backup Security
- Encrypt backup files
- Store backups in secure locations
- Implement backup verification

### 3. Access Control
```python
# Implement role-based access control
class DatabaseAccessControl:
    def __init__(self):
        self.roles = {
            'admin': ['read', 'write', 'delete'],
            'trader': ['read', 'write'],
            'viewer': ['read']
        }
```

## 📊 Recommended Database Stack

### For Development (Current)
- ✅ SQLite for structured data
- ✅ CSV files for logs
- ✅ JSON for configuration

### For Staging
- 🔄 PostgreSQL for structured data
- 🔄 InfluxDB for time-series data
- 🔄 Redis for caching and real-time data

### For Production
- 🎯 PostgreSQL with read replicas
- 🎯 InfluxDB cluster for time-series
- 🎯 Redis cluster for caching
- 🎯 Automated backup and monitoring

## 🛠️ Implementation Priority

### High Priority (Do First)
1. Add signal storage table to SQLite
2. Implement automated backups
3. Add database indexes
4. Create connection pooling

### Medium Priority (Do Next)
1. Integrate InfluxDB for signal data
2. Add Redis for real-time broadcasting
3. Implement data archiving
4. Add performance monitoring

### Low Priority (Future)
1. Migrate to PostgreSQL
2. Implement full clustering
3. Add advanced analytics
4. Create data warehouse integration

## 📚 Additional Resources

- [SQLite Performance Tuning](https://www.sqlite.org/optoverview.html)
- [InfluxDB Best Practices](https://docs.influxdata.com/influxdb/v2.0/best-practices/)
- [PostgreSQL Performance](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Redis Data Structures](https://redis.io/docs/data-types/)

---

**Next Steps**: Start with Phase 1 improvements to enhance the current SQLite setup, then gradually migrate to more robust solutions as the system scales.
