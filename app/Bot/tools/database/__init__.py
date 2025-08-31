"""
🗄️ Database Utilities - The Cosmic Data Temple
Exports all database-related functions and classes for easy importing
"""

from .database import (
    connect,
    create_table,
    insert_order,
    get_all_orders,
    get_order_by_id,
    delete_all_orders,
    delete_order_by_id
)

from .order import (
    Order,
    Receipt
)

from .product import (
    Product,
    ProductManager,
    product_manager
)

__all__ = [
    # Database functions
    'connect',
    'create_table',
    'insert_order',
    'get_all_orders',
    'get_order_by_id',
    'delete_all_orders',
    'delete_order_by_id',
    
    # Data classes
    'Order',
    'Receipt',
    'Product',
    'ProductManager',
    'product_manager'
]
