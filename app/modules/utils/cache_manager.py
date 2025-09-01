"""
💾 Cache Manager - The Memory Palace of Digital Data
Where frequently accessed information finds its temporary home
"""

import time
import threading
from typing import Any, Dict, Optional
from collections import OrderedDict
from .log_module import CustomLogger

# Initialize the cosmic logger
logger = CustomLogger("app.log")

class CacheEntry:
    """
    📦 A single cache entry with expiration tracking
    """
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.expires_at = time.time() + ttl
        self.created_at = time.time()
    
    def is_expired(self) -> bool:
        """⏰ Check if this cache entry has expired"""
        return time.time() > self.expires_at
    
    def get_age(self) -> float:
        """📅 Get the age of this cache entry in seconds"""
        return time.time() - self.created_at

class LRUCache:
    """
    🔄 Least Recently Used Cache with expiration support
    Automatically removes old entries when cache is full
    """
    
    def __init__(self, max_size: int = 100, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict = OrderedDict()
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expirations': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """
        🔍 Retrieve a value from cache
        Returns None if key doesn't exist or has expired
        """
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                if entry.is_expired():
                    # Remove expired entry
                    del self.cache[key]
                    self.stats['expirations'] += 1
                    self.stats['misses'] += 1
                    return None
                
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                self.stats['hits'] += 1
                return entry.value
            
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        💾 Store a value in cache with optional TTL
        """
        with self.lock:
            # Remove if already exists
            if key in self.cache:
                del self.cache[key]
            
            # Create new entry
            entry_ttl = ttl if ttl is not None else self.default_ttl
            entry = CacheEntry(value, entry_ttl)
            
            # Add to cache
            self.cache[key] = entry
            
            # Evict oldest if cache is full
            if len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self.stats['evictions'] += 1
    
    def delete(self, key: str) -> bool:
        """
        🗑️ Remove a key from cache
        Returns True if key existed, False otherwise
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """
        🧹 Clear all entries from cache
        """
        with self.lock:
            self.cache.clear()
            logger.log('info', "Cache cleared")
    
    def cleanup_expired(self) -> int:
        """
        🧽 Remove all expired entries
        Returns the number of entries removed
        """
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items() 
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self.cache[key]
                self.stats['expirations'] += 1
            
            if expired_keys:
                logger.log('info', f"Cleaned up {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        📊 Get cache statistics
        """
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate': f"{hit_rate:.2f}%",
                'evictions': self.stats['evictions'],
                'expirations': self.stats['expirations'],
                'total_requests': total_requests
            }
    
    def print_stats(self) -> None:
        """
        📈 Display cache statistics in a beautiful format
        """
        stats = self.get_stats()
        
        print("\n" + "="*50)
        print("💾 CACHE STATISTICS")
        print("="*50)
        print(f"📦 Size: {stats['size']}/{stats['max_size']}")
        print(f"🎯 Hit Rate: {stats['hit_rate']}")
        print(f"✅ Hits: {stats['hits']}")
        print(f"❌ Misses: {stats['misses']}")
        print(f"🗑️ Evictions: {stats['evictions']}")
        print(f"⏰ Expirations: {stats['expirations']}")
        print(f"📊 Total Requests: {stats['total_requests']}")
        print("="*50)

class CacheManager:
    """
    🎛️ The Grand Cache Orchestrator
    Manages multiple cache instances for different data types
    """
    
    def __init__(self):
        self.caches: Dict[str, LRUCache] = {}
        self.lock = threading.RLock()
        
        # Initialize default caches
        self._init_default_caches()
    
    def _init_default_caches(self):
        """🔧 Initialize default cache instances"""
        self.create_cache('prices', max_size=1000, default_ttl=30)  # Short TTL for prices
        self.create_cache('wallet', max_size=100, default_ttl=60)   # Medium TTL for wallet
        self.create_cache('symbols', max_size=500, default_ttl=3600)  # Long TTL for symbols
        self.create_cache('orders', max_size=200, default_ttl=300)   # Medium TTL for orders
    
    def create_cache(self, name: str, max_size: int = 100, default_ttl: int = 300) -> LRUCache:
        """
        🆕 Create a new cache instance
        """
        with self.lock:
            if name in self.caches:
                logger.log('warning', f"Cache '{name}' already exists, returning existing instance")
                return self.caches[name]
            
            cache = LRUCache(max_size, default_ttl)
            self.caches[name] = cache
            logger.log('info', f"Created cache '{name}' with max_size={max_size}, ttl={default_ttl}")
            return cache
    
    def get_cache(self, name: str) -> Optional[LRUCache]:
        """
        🔍 Get a cache instance by name
        """
        with self.lock:
            return self.caches.get(name)
    
    def get(self, cache_name: str, key: str) -> Optional[Any]:
        """
        🔍 Get a value from a specific cache
        """
        cache = self.get_cache(cache_name)
        if cache:
            return cache.get(key)
        return None
    
    def set(self, cache_name: str, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        💾 Set a value in a specific cache
        """
        cache = self.get_cache(cache_name)
        if cache:
            cache.set(key, value, ttl)
    
    def delete(self, cache_name: str, key: str) -> bool:
        """
        🗑️ Delete a key from a specific cache
        """
        cache = self.get_cache(cache_name)
        if cache:
            return cache.delete(key)
        return False
    
    def clear_cache(self, cache_name: str) -> None:
        """
        🧹 Clear a specific cache
        """
        cache = self.get_cache(cache_name)
        if cache:
            cache.clear()
    
    def cleanup_all(self) -> int:
        """
        🧽 Clean up expired entries in all caches
        Returns total number of entries removed
        """
        total_removed = 0
        with self.lock:
            for cache in self.caches.values():
                total_removed += cache.cleanup_expired()
        
        if total_removed > 0:
            logger.log('info', f"Cleaned up {total_removed} expired entries across all caches")
        
        return total_removed
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        📊 Get statistics for all caches
        """
        with self.lock:
            return {name: cache.get_stats() for name, cache in self.caches.items()}
    
    def print_all_stats(self) -> None:
        """
        📈 Display statistics for all caches
        """
        stats = self.get_all_stats()
        
        print("\n" + "="*60)
        print("💾 CACHE MANAGER STATISTICS")
        print("="*60)
        
        for cache_name, cache_stats in stats.items():
            print(f"\n📦 {cache_name.upper()} CACHE:")
            print(f"  Size: {cache_stats['size']}/{cache_stats['max_size']}")
            print(f"  Hit Rate: {cache_stats['hit_rate']}")
            print(f"  Hits: {cache_stats['hits']}, Misses: {cache_stats['misses']}")
        
        print("\n" + "="*60)

# Global cache manager instance
cache_manager = CacheManager()

def get_cached_value(cache_name: str, key: str) -> Optional[Any]:
    """
    🌟 Convenience function to get cached values
    """
    return cache_manager.get(cache_name, key)

def set_cached_value(cache_name: str, key: str, value: Any, ttl: Optional[int] = None) -> None:
    """
    🌟 Convenience function to set cached values
    """
    cache_manager.set(cache_name, key, value, ttl)

def clear_cache(cache_name: str) -> None:
    """
    🌟 Convenience function to clear a cache
    """
    cache_manager.clear_cache(cache_name)
