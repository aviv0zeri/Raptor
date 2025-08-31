"""
🌟 Trading Database Models - The Cosmic Data Architecture
Organized SQL classes for buy/sell operations and trading data
"""

import os
import psycopg2
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum

class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    STOP_LOSS = "STOP_LOSS"

class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"

class TradeType(Enum):
    REAL = "REAL"
    TEST = "TEST"
    PAPER = "PAPER"

@dataclass
class Order:
    id: int
    order_id: str
    symbol: str
    side: OrderType
    quantity: Decimal
    price: Decimal
    status: OrderStatus
    trade_type: TradeType
    created_at: datetime

@dataclass
class Trade:
    id: int
    trade_id: str
    order_id: str
    symbol: str
    side: OrderType
    quantity: Decimal
    price: Decimal
    trade_type: TradeType
    time: datetime

@dataclass
class Balance:
    id: int
    asset: str
    free: Decimal
    locked: Decimal
    total: Decimal
    trade_type: TradeType
    updated_at: datetime

class TradingDatabase:
    def __init__(self):
        self.connection = None
        self._init_connection()
        self._create_tables()
    
    def _init_connection(self):
        try:
            self.connection = psycopg2.connect(
                dbname=os.getenv('DB_NAME', 'trading_bot'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', '<REDACTED_DB_PASSWORD>'),
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432')
            )
            print("🌟 Database connection established")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def _create_tables(self):
        tables = [
            self._create_orders_table(),
            self._create_trades_table(),
            self._create_balances_table()
        ]
        
        for table_sql in tables:
            self._execute_sql(table_sql)
        
        print("🌟 Trading tables created successfully")
    
    def _create_orders_table(self) -> str:
        return """
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            order_id VARCHAR(50) UNIQUE NOT NULL,
            symbol VARCHAR(20) NOT NULL,
            side VARCHAR(10) NOT NULL,
            quantity DECIMAL(20,8) NOT NULL,
            price DECIMAL(20,8) NOT NULL,
            status VARCHAR(20) NOT NULL,
            trade_type VARCHAR(10) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    
    def _create_trades_table(self) -> str:
        return """
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            trade_id VARCHAR(50) UNIQUE NOT NULL,
            order_id VARCHAR(50) NOT NULL,
            symbol VARCHAR(20) NOT NULL,
            side VARCHAR(10) NOT NULL,
            quantity DECIMAL(20,8) NOT NULL,
            price DECIMAL(20,8) NOT NULL,
            trade_type VARCHAR(10) NOT NULL,
            time TIMESTAMP NOT NULL
        );
        """
    
    def _create_balances_table(self) -> str:
        return """
        CREATE TABLE IF NOT EXISTS balances (
            id SERIAL PRIMARY KEY,
            asset VARCHAR(10) NOT NULL,
            free DECIMAL(20,8) NOT NULL,
            locked DECIMAL(20,8) NOT NULL,
            total DECIMAL(20,8) NOT NULL,
            trade_type VARCHAR(10) NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    
    def _execute_sql(self, sql: str, params: Tuple = None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            
            if sql.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                result = []
                self.connection.commit()
            
            cursor.close()
            return result
        except Exception as e:
            self.connection.rollback()
            print(f"❌ SQL execution error: {e}")
            raise
    
    def insert_order(self, order: Order) -> int:
        sql = """
        INSERT INTO orders (order_id, symbol, side, quantity, price, status, trade_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """
        
        params = (
            order.order_id, order.symbol, order.side.value,
            order.quantity, order.price, order.status.value, order.trade_type.value
        )
        
        result = self._execute_sql(sql, params)
        return result[0][0] if result else None
    
    def get_orders(self, symbol: str = None, trade_type: TradeType = None) -> List[Order]:
        sql = "SELECT * FROM orders WHERE 1=1"
        params = []
        
        if symbol:
            sql += " AND symbol = %s"
            params.append(symbol)
        
        if trade_type:
            sql += " AND trade_type = %s"
            params.append(trade_type.value)
        
        sql += " ORDER BY created_at DESC;"
        
        result = self._execute_sql(sql, tuple(params))
        
        orders = []
        for row in result:
            order = Order(
                id=row[0], order_id=row[1], symbol=row[2], side=OrderType(row[3]),
                quantity=row[4], price=row[5], status=OrderStatus(row[6]),
                trade_type=TradeType(row[7]), created_at=row[8]
            )
            orders.append(order)
        
        return orders

# Global database instance
trading_db = TradingDatabase()
