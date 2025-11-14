#!/usr/bin/env python3
"""
 =============================================================================
 AI RULES PERFORMANCE OPTIMIZATION AND CACHING SYSTEM
 =============================================================================
 High-performance caching layer and optimization utilities for AI Rules system.
 Provides intelligent caching, performance monitoring, and optimization recommendations.
"""

import os
import sys
import json
import time
import hashlib
import pickle
import threading
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from functools import wraps, lru_cache
from concurrent.futures import ThreadPoolExecutor
import weakref

# Add home directory to path
sys.path.append(str(Path.home()))

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class CacheConfig:
    """Configuration for caching system"""
    
    # Cache settings
    cache_dir: str = None
    max_memory_cache_size: int = 1000  # items
    max_disk_cache_size: int = 100 * 1024 * 1024  # 100MB
    cache_ttl: int = 3600  # 1 hour
    cleanup_interval: int = 300  # 5 minutes
    
    # Performance settings
    enable_compression: bool = True
    enable_encryption: bool = False
    enable_metrics: bool = True
    thread_pool_size: int = 4
    
    # Database settings
    db_path: str = None
    
    def __post_init__(self):
        if self.cache_dir is None:
            self.cache_dir = str(Path.home() / ".cache" / "ai_rules")
        
        if self.db_path is None:
            self.db_path = os.path.join(self.cache_dir, "cache.db")
        
        # Ensure cache directory exists
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int
    size_bytes: int
    ttl: int
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at.isoformat(),
            'accessed_at': self.accessed_at.isoformat(),
            'access_count': self.access_count,
            'size_bytes': self.size_bytes,
            'ttl': self.ttl
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create from dictionary"""
        return cls(
            key=data['key'],
            value=data['value'],
            created_at=datetime.fromisoformat(data['created_at']),
            accessed_at=datetime.fromisoformat(data['accessed_at']),
            access_count=data['access_count'],
            size_bytes=data['size_bytes'],
            ttl=data['ttl']
        )

# =============================================================================
# HIGH-PERFORMANCE CACHE
# =============================================================================

class AIRulesCache:
    """High-performance multi-level caching system"""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._cleanup_thread = None
        self._metrics = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0,
            'cleanups': 0
        }
        
        # Initialize database
        self._init_database()
        
        # Start cleanup thread
        self._start_cleanup_thread()
        
        # Load existing cache from disk
        self._load_disk_cache()
    
    def _init_database(self):
        """Initialize SQLite database for persistent caching"""
        self._db_conn = sqlite3.connect(self.config.db_path, check_same_thread=False)
        self._db_conn.execute('''
            CREATE TABLE IF NOT EXISTS cache_entries (
                key TEXT PRIMARY KEY,
                value BLOB,
                created_at TIMESTAMP,
                accessed_at TIMESTAMP,
                access_count INTEGER,
                size_bytes INTEGER,
                ttl INTEGER
            )
        ''')
        
        self._db_conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_accessed_at ON cache_entries(accessed_at)
        ''')
        
        self._db_conn.commit()
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_loop():
            while True:
                time.sleep(self.config.cleanup_interval)
                self._cleanup_expired()
        
        self._cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self._cleanup_thread.start()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            # Check memory cache first
            if key in self._memory_cache:
                entry = self._memory_cache[key]
                if not entry.is_expired():
                    entry.accessed_at = datetime.now()
                    entry.access_count += 1
                    self._metrics['hits'] += 1
                    return entry.value
                else:
                    # Remove expired entry
                    del self._memory_cache[key]
                    self._remove_from_disk(key)
            
            # Check disk cache
            entry = self._get_from_disk(key)
            if entry and not entry.is_expired():
                # Promote to memory cache
                self._memory_cache[key] = entry
                entry.accessed_at = datetime.now()
                entry.access_count += 1
                self._metrics['hits'] += 1
                return entry.value
            
            self._metrics['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        if ttl is None:
            ttl = self.config.cache_ttl
        
        # Calculate size
        size_bytes = len(pickle.dumps(value))
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            accessed_at=datetime.now(),
            access_count=1,
            size_bytes=size_bytes,
            ttl=ttl
        )
        
        with self._lock:
            # Check memory cache size
            if len(self._memory_cache) >= self.config.max_memory_cache_size:
                self._evict_lru()
            
            # Add to memory cache
            self._memory_cache[key] = entry
            
            # Add to disk cache
            self._save_to_disk(entry)
            
            self._metrics['sets'] += 1
    
    def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        with self._lock:
            deleted = False
            
            if key in self._memory_cache:
                del self._memory_cache[key]
                deleted = True
            
            deleted = self._remove_from_disk(key) or deleted
            
            return deleted
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._memory_cache.clear()
            
            # Clear disk cache
            self._db_conn.execute('DELETE FROM cache_entries')
            self._db_conn.commit()
    
    def _get_from_disk(self, key: str) -> Optional[CacheEntry]:
        """Get entry from disk cache"""
        try:
            cursor = self._db_conn.cursor()
            cursor.execute('''
                SELECT key, value, created_at, accessed_at, access_count, size_bytes, ttl
                FROM cache_entries WHERE key = ?
            ''', (key,))
            
            row = cursor.fetchone()
            if row:
                value = pickle.loads(row[1])
                return CacheEntry(
                    key=row[0],
                    value=value,
                    created_at=datetime.fromisoformat(row[2]),
                    accessed_at=datetime.fromisoformat(row[3]),
                    access_count=row[4],
                    size_bytes=row[5],
                    ttl=row[6]
                )
        except Exception:
            pass
        
        return None
    
    def _save_to_disk(self, entry: CacheEntry) -> None:
        """Save entry to disk cache"""
        try:
            value_blob = pickle.dumps(entry.value)
            cursor = self._db_conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO cache_entries
                (key, value, created_at, accessed_at, access_count, size_bytes, ttl)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.key,
                value_blob,
                entry.created_at.isoformat(),
                entry.accessed_at.isoformat(),
                entry.access_count,
                entry.size_bytes,
                entry.ttl
            ))
            self._db_conn.commit()
        except Exception:
            pass
    
    def _remove_from_disk(self, key: str) -> bool:
        """Remove entry from disk cache"""
        try:
            cursor = self._db_conn.cursor()
            cursor.execute('DELETE FROM cache_entries WHERE key = ?', (key,))
            self._db_conn.commit()
            return cursor.rowcount > 0
        except Exception:
            return False
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry from memory cache"""
        if not self._memory_cache:
            return
        
        # Find LRU entry
        lru_key = min(self._memory_cache.keys(), 
                    key=lambda k: self._memory_cache[k].accessed_at)
        
        del self._memory_cache[lru_key]
        self._metrics['evictions'] += 1
    
    def _cleanup_expired(self) -> None:
        """Clean up expired entries"""
        with self._lock:
            # Clean memory cache
            expired_keys = [
                key for key, entry in self._memory_cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._memory_cache[key]
                self._remove_from_disk(key)
            
            # Clean disk cache
            cursor = self._db_conn.cursor()
            cutoff_time = (datetime.now() - timedelta(seconds=self.config.cache_ttl)).isoformat()
            cursor.execute('''
                DELETE FROM cache_entries WHERE created_at < ?
            ''', (cutoff_time,))
            self._db_conn.commit()
            
            self._metrics['cleanups'] += 1
    
    def _load_disk_cache(self) -> None:
        """Load frequently accessed entries from disk to memory"""
        try:
            cursor = self._db_conn.cursor()
            cursor.execute('''
                SELECT key, value, created_at, accessed_at, access_count, size_bytes, ttl
                FROM cache_entries
                ORDER BY access_count DESC
                LIMIT ?
            ''', (self.config.max_memory_cache_size // 2,))
            
            for row in cursor.fetchall():
                value = pickle.loads(row[1])
                entry = CacheEntry(
                    key=row[0],
                    value=value,
                    created_at=datetime.fromisoformat(row[2]),
                    accessed_at=datetime.fromisoformat(row[3]),
                    access_count=row[4],
                    size_bytes=row[5],
                    ttl=row[6]
                )
                
                if not entry.is_expired():
                    self._memory_cache[entry.key] = entry
        except Exception:
            pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        with self._lock:
            total_requests = self._metrics['hits'] + self._metrics['misses']
            hit_rate = (self._metrics['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'memory_cache_size': len(self._memory_cache),
                'max_memory_cache_size': self.config.max_memory_cache_size,
                'hits': self._metrics['hits'],
                'misses': self._metrics['misses'],
                'hit_rate_percent': round(hit_rate, 2),
                'sets': self._metrics['sets'],
                'evictions': self._metrics['evictions'],
                'cleanups': self._metrics['cleanups']
            }

# =============================================================================
# PERFORMANCE OPTIMIZATION DECORATORS
# =============================================================================

# Global cache instance
_global_cache: Optional[AIRulesCache] = None

def get_global_cache() -> AIRulesCache:
    """Get or create global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = AIRulesCache()
    return _global_cache

def cached(ttl: Optional[int] = None, key_func: Optional[callable] = None):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_global_cache()
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hashlib.md5(str(args + tuple(sorted(kwargs.items()))).encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        wrapper.cache_info = lambda: get_global_cache().get_metrics()
        wrapper.cache_clear = lambda: get_global_cache().clear()
        
        return wrapper
    return decorator

def async_cached(ttl: Optional[int] = None, max_workers: int = 4):
    """Decorator for caching async function results with thread pool"""
    def decorator(func):
        _thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_global_cache()
            
            # Generate cache key
            cache_key = f"{func.__name__}:{hashlib.md5(str(args + tuple(sorted(kwargs.items()))).encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function asynchronously
            future = _thread_pool.submit(func, *args, **kwargs)
            result = future.result()
            
            # Cache result
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

# =============================================================================
# OPTIMIZED AI RULES FUNCTIONS
# =============================================================================

class OptimizedAIRules:
    """Optimized AI Rules with caching and performance enhancements"""
    
    def __init__(self, cache_config: Optional[CacheConfig] = None):
        self.cache = AIRulesCache(cache_config)
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Pre-load common validations
        self._preload_common_validations()
    
    def _preload_common_validations(self):
        """Pre-load common validation patterns"""
        common_patterns = [
            ("read", "/home/user/safe_file.txt"),
            ("write", "/home/user/output.txt"),
            ("list", "/home/user/documents"),
        ]
        
        for operation, target in common_patterns:
            self.validate_operation_cached(operation, target)
    
    @cached(ttl=3600)  # Cache for 1 hour
    def validate_operation_cached(self, operation: str, target: str) -> bool:
        """Cached version of operation validation"""
        return self._validate_operation_internal(operation, target)
    
    def _validate_operation_internal(self, operation: str, target: str) -> bool:
        """Internal validation logic"""
        # Import and use original validation
        try:
            from ai_rules_integration import AIRulesLoader
            loader = AIRulesLoader()
            return loader.validate_operation(operation, target)
        except Exception:
            # Fallback validation
            return self._fallback_validation(operation, target)
    
    def _fallback_validation(self, operation: str, target: str) -> bool:
        """Fallback validation when main system unavailable"""
        # Basic safety checks
        dangerous_ops = ['rm', 'mv', 'chmod', 'chown']
        system_paths = ['/etc/', '/usr/', '/boot/', '/sys/', '/proc/']
        
        if operation in dangerous_ops:
            for sys_path in system_paths:
                if target.startswith(sys_path):
                    return False
        
        return True
    
    @async_cached(ttl=1800, max_workers=8)  # Cache for 30 minutes
    def batch_validate_operations(self, operations: List[Tuple[str, str]]) -> List[bool]:
        """Validate multiple operations in parallel"""
        results = []
        
        for operation, target in operations:
            result = self.validate_operation_cached(operation, target)
            results.append(result)
        
        return results
    
    @cached(ttl=7200)  # Cache for 2 hours
    def get_agent_capabilities(self, agent_name: str) -> Dict[str, Any]:
        """Get cached agent capabilities"""
        # This would integrate with agent detection system
        capabilities = {
            'opencode': ['code_analysis', 'file_operations', 'documentation'],
            'cursor': ['ai_coding', 'code_generation', 'file_operations'],
            'claude': ['conversation', 'code_assistance', 'analysis'],
            'vscode': ['code_editing', 'file_operations', 'terminal_access']
        }
        
        return capabilities.get(agent_name, ['general_assistance'])
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        cache_metrics = self.cache.get_metrics()
        
        return {
            'cache': cache_metrics,
            'thread_pool': {
                'active_threads': threading.active_count(),
                'max_workers': self._thread_pool._max_workers
            },
            'memory': {
                'cache_memory_mb': sys.getsizeof(self.cache._memory_cache) / (1024 * 1024)
            },
            'optimization': {
                'cache_hit_rate': cache_metrics['hit_rate_percent'],
                'efficiency_score': min(100, cache_metrics['hit_rate_percent'] + 
                                   (100 - cache_metrics['memory_cache_size'] / 
                                    cache_metrics['max_memory_cache_size'] * 100))
            }
        }
    
    def optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache performance"""
        before_metrics = self.cache.get_metrics()
        
        # Clean expired entries
        self.cache._cleanup_expired()
        
        # Promote frequently accessed items
        self.cache._load_disk_cache()
        
        after_metrics = self.cache.get_metrics()
        
        return {
            'before': before_metrics,
            'after': after_metrics,
            'improvements': {
                'memory_usage_change': after_metrics['memory_cache_size'] - before_metrics['memory_cache_size'],
                'hit_rate_change': after_metrics['hit_rate_percent'] - before_metrics['hit_rate_percent']
            }
        }

# =============================================================================
# PERFORMANCE MONITORING
# =============================================================================

class PerformanceProfiler:
    """Performance profiler for AI Rules operations"""
    
    def __init__(self):
        self._profiles: Dict[str, List[float]] = {}
        self._lock = threading.Lock()
    
    def profile(self, name: str):
        """Decorator for profiling function performance"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.perf_counter()
                    duration = end_time - start_time
                    
                    with self._lock:
                        if name not in self._profiles:
                            self._profiles[name] = []
                        self._profiles[name].append(duration)
            
            return wrapper
        return decorator
    
    def get_stats(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics"""
        with self._lock:
            stats = {}
            
            for name, times in self._profiles.items():
                if times:
                    stats[name] = {
                        'count': len(times),
                        'total_time': sum(times),
                        'avg_time': sum(times) / len(times),
                        'min_time': min(times),
                        'max_time': max(times),
                        'p95_time': sorted(times)[int(len(times) * 0.95)] if len(times) > 20 else max(times)
                    }
            
            return stats
    
    def clear(self):
        """Clear all profiles"""
        with self._lock:
            self._profiles.clear()

# Global profiler instance
_global_profiler = PerformanceProfiler()

def profile(name: str):
    """Get global profiler decorator"""
    return _global_profiler.profile(name)

def get_performance_stats() -> Dict[str, Dict[str, float]]:
    """Get global performance statistics"""
    return _global_profiler.get_stats()

# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI interface for performance optimization"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Rules Performance Optimization')
    parser.add_argument('command', choices=['status', 'optimize', 'clear', 'stats'], 
                       help='Command to execute')
    parser.add_argument('--config', help='Configuration file path')
    
    args = parser.parse_args()
    
    # Load configuration
    config = CacheConfig()
    if args.config and Path(args.config).exists():
        with open(args.config, 'r') as f:
            config_data = json.load(f)
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
    
    # Initialize optimized system
    optimized_rules = OptimizedAIRules(config)
    
    if args.command == 'status':
        metrics = optimized_rules.get_performance_metrics()
        print(json.dumps(metrics, indent=2))
    
    elif args.command == 'optimize':
        result = optimized_rules.optimize_cache()
        print(json.dumps(result, indent=2))
    
    elif args.command == 'clear':
        optimized_rules.cache.clear()
        print("Cache cleared")
    
    elif args.command == 'stats':
        stats = get_performance_stats()
        print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()