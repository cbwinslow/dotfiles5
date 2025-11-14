#!/usr/bin/env python3
"""
Real-time Performance Monitoring and Analytics System
Provides comprehensive monitoring, metrics collection, and analytics for multi-agent systems
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "tags": self.tags
        }

@dataclass
class Alert:
    """Alert definition"""
    name: str
    condition: str
    severity: AlertSeverity
    threshold: float
    duration: timedelta
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "condition": self.condition,
            "severity": self.severity.value,
            "threshold": self.threshold,
            "duration": self.duration.total_seconds(),
            "enabled": self.enabled,
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "trigger_count": self.trigger_count
        }

class TimeSeriesBuffer:
    """Circular buffer for time series data"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.buffer: deque = deque(maxlen=max_size)
        self.lock = threading.Lock()
    
    def add(self, point: MetricPoint):
        """Add a metric point"""
        with self.lock:
            self.buffer.append(point)
    
    def get_recent(self, duration: timedelta) -> List[MetricPoint]:
        """Get points from recent duration"""
        cutoff = datetime.now() - duration
        with self.lock:
            return [point for point in self.buffer if point.timestamp >= cutoff]
    
    def get_latest(self, count: int = 1) -> List[MetricPoint]:
        """Get latest N points"""
        with self.lock:
            return list(self.buffer)[-count:]
    
    def clear(self):
        """Clear buffer"""
        with self.lock:
            self.buffer.clear()

class Metric:
    """Base metric class"""
    
    def __init__(self, name: str, metric_type: MetricType, tags: Dict[str, str] = None):
        self.name = name
        self.type = metric_type
        self.tags = tags or {}
        self.buffer = TimeSeriesBuffer()
        self.created_at = datetime.now()
    
    def add_point(self, value: float, tags: Dict[str, str] = None):
        """Add a data point"""
        merged_tags = {**self.tags, **(tags or {})}
        point = MetricPoint(timestamp=datetime.now(), value=value, tags=merged_tags)
        self.buffer.add(point)
    
    def get_recent(self, duration: timedelta) -> List[MetricPoint]:
        """Get recent data points"""
        return self.buffer.get_recent(duration)
    
    def get_statistics(self, duration: timedelta) -> Dict[str, float]:
        """Get statistical summary"""
        points = self.get_recent(duration)
        if not points:
            return {}
        
        values = [p.value for p in points]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
            "sum": sum(values)
        }

class PerformanceMonitor:
    """Main performance monitoring system"""
    
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self.alerts: Dict[str, Alert] = {}
        self.alert_handlers: List[Callable] = []
        self.running = False
        self.monitor_task: Optional[asyncio.Task] = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # System-wide metrics
        self.register_metric("system.requests_total", MetricType.COUNTER)
        self.register_metric("system.errors_total", MetricType.COUNTER)
        self.register_metric("system.response_time", MetricType.HISTOGRAM)
        self.register_metric("system.active_agents", MetricType.GAUGE)
        self.register_metric("system.memory_usage", MetricType.GAUGE)
        self.register_metric("system.cpu_usage", MetricType.GAUGE)
    
    def register_metric(self, name: str, metric_type: MetricType, tags: Dict[str, str] = None) -> Metric:
        """Register a new metric"""
        metric = Metric(name, metric_type, tags)
        self.metrics[name] = metric
        logger.info(f"Registered metric: {name} ({metric_type.value})")
        return metric
    
    def register_alert(self, alert: Alert):
        """Register an alert"""
        self.alerts[alert.name] = alert
        logger.info(f"Registered alert: {alert.name}")
    
    def add_alert_handler(self, handler: Callable):
        """Add alert handler function"""
        self.alert_handlers.append(handler)
    
    def increment_counter(self, name: str, value: float = 1.0, tags: Dict[str, str] = None):
        """Increment counter metric"""
        if name in self.metrics and self.metrics[name].type == MetricType.COUNTER:
            current = self._get_current_value(name)
            self.metrics[name].add_point(current + value, tags)
        else:
            logger.warning(f"Counter metric {name} not found or wrong type")
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set gauge metric value"""
        if name in self.metrics and self.metrics[name].type == MetricType.GAUGE:
            self.metrics[name].add_point(value, tags)
        else:
            logger.warning(f"Gauge metric {name} not found or wrong type")
    
    def record_timer(self, name: str, duration: float, tags: Dict[str, str] = None):
        """Record timer/histogram metric"""
        if name in self.metrics and self.metrics[name].type in [MetricType.TIMER, MetricType.HISTOGRAM]:
            self.metrics[name].add_point(duration, tags)
        else:
            logger.warning(f"Timer/Histogram metric {name} not found or wrong type")
    
    def time_function(self, metric_name: str, tags: Dict[str, str] = None):
        """Decorator to time function execution"""
        def decorator(func):
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    self.record_timer(metric_name, duration, tags)
            
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    self.record_timer(metric_name, duration, tags)
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def _get_current_value(self, name: str) -> float:
        """Get current value for counter metrics"""
        if name not in self.metrics:
            return 0.0
        
        latest = self.metrics[name].buffer.get_latest(1)
        return latest[0].value if latest else 0.0
    
    async def start_monitoring(self, interval: float = 5.0):
        """Start background monitoring"""
        self.running = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop(interval))
        logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop background monitoring"""
        self.running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Performance monitoring stopped")
    
    async def _monitoring_loop(self, interval: float):
        """Background monitoring loop"""
        while self.running:
            try:
                await self._check_alerts()
                await self._collect_system_metrics()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(interval)
    
    async def _check_alerts(self):
        """Check all alerts and trigger if needed"""
        now = datetime.now()
        
        for alert in self.alerts.values():
            if not alert.enabled:
                continue
            
            try:
                triggered = await self._evaluate_alert(alert)
                if triggered:
                    if (alert.last_triggered is None or 
                        now - alert.last_triggered >= alert.duration):
                        await self._trigger_alert(alert)
            except Exception as e:
                logger.error(f"Error evaluating alert {alert.name}: {e}")
    
    async def _evaluate_alert(self, alert: Alert) -> bool:
        """Evaluate alert condition"""
        # Simple threshold-based evaluation
        # In production, this would support more complex conditions
        if "response_time" in alert.name:
            metric = self.metrics.get("system.response_time")
            if metric:
                stats = metric.get_statistics(timedelta(minutes=5))
                return stats.get("mean", 0) > alert.threshold
        
        elif "error_rate" in alert.name:
            requests = self.metrics.get("system.requests_total")
            errors = self.metrics.get("system.errors_total")
            if requests and errors:
                req_stats = requests.get_statistics(timedelta(minutes=5))
                err_stats = errors.get_statistics(timedelta(minutes=5))
                
                if req_stats.get("sum", 0) > 0:
                    error_rate = err_stats.get("sum", 0) / req_stats.get("sum", 1)
                    return error_rate > alert.threshold
        
        return False
    
    async def _trigger_alert(self, alert: Alert):
        """Trigger an alert"""
        alert.last_triggered = datetime.now()
        alert.trigger_count += 1
        
        alert_data = {
            "alert": alert.to_dict(),
            "timestamp": datetime.now().isoformat(),
            "metrics": self.get_metrics_summary()
        }
        
        logger.warning(f"Alert triggered: {alert.name} ({alert.severity.value})")
        
        # Call all alert handlers
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert_data)
                else:
                    handler(alert_data)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            import psutil
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.set_gauge("system.memory_usage", memory.percent, {"unit": "percent"})
            
            # CPU usage
            cpu = psutil.cpu_percent(interval=1)
            self.set_gauge("system.cpu_usage", cpu, {"unit": "percent"})
            
        except ImportError:
            # psutil not available, skip system metrics
            pass
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def get_metrics_summary(self, duration: timedelta = timedelta(minutes=5)) -> Dict[str, Any]:
        """Get summary of all metrics"""
        summary = {}
        
        for name, metric in self.metrics.items():
            stats = metric.get_statistics(duration)
            if stats:
                summary[name] = {
                    "type": metric.type.value,
                    "statistics": stats,
                    "latest_value": self._get_current_value(name)
                }
        
        return summary
    
    def get_alerts_summary(self) -> Dict[str, Any]:
        """Get summary of all alerts"""
        return {
            name: alert.to_dict() 
            for name, alert in self.alerts.items()
        }
    
    def export_metrics(self, duration: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """Export metrics data for analysis"""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "duration": duration.total_seconds(),
            "metrics": {}
        }
        
        for name, metric in self.metrics.items():
            points = metric.get_recent(duration)
            export_data["metrics"][name] = {
                "type": metric.type.value,
                "tags": metric.tags,
                "data": [point.to_dict() for point in points]
            }
        
        return export_data
    
    def clear_metrics(self):
        """Clear all metric data"""
        for metric in self.metrics.values():
            metric.buffer.clear()
        logger.info("All metrics cleared")

# Alert handlers
async def console_alert_handler(alert_data: Dict[str, Any]):
    """Simple console alert handler"""
    alert = alert_data["alert"]
    print(f"\n🚨 ALERT: {alert['name']}")
    print(f"   Severity: {alert['severity']}")
    print(f"   Threshold: {alert['threshold']}")
    print(f"   Triggered: {alert['last_triggered']}")
    print(f"   Count: {alert['trigger_count']}")
    print()

async def file_alert_handler(alert_data: Dict[str, Any], filename: str = "alerts.log"):
    """File-based alert handler"""
    with open(filename, "a") as f:
        f.write(f"{json.dumps(alert_data)}\n")

# Performance context manager
class PerformanceContext:
    """Context manager for performance measurement"""
    
    def __init__(self, monitor: PerformanceMonitor, metric_name: str, tags: Dict[str, str] = None):
        self.monitor = monitor
        self.metric_name = metric_name
        self.tags = tags or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.monitor.record_timer(self.metric_name, duration, self.tags)
        
        # Record error if exception occurred
        if exc_type:
            self.monitor.increment_counter("system.errors_total", 1.0, 
                                         {"error_type": exc_type.__name__})

# Example usage
async def example_function(monitor: PerformanceMonitor):
    """Example function to demonstrate monitoring"""
    with PerformanceContext(monitor, "example_function_duration"):
        monitor.increment_counter("system.requests_total")
        monitor.set_gauge("system.active_agents", 5)
        
        # Simulate work
        await asyncio.sleep(0.1)
        
        # Randomly fail sometimes
        import random
        if random.random() < 0.1:
            raise ValueError("Random error")

async def main():
    """Demonstrate performance monitoring"""
    # Initialize monitor
    monitor = PerformanceMonitor()
    
    # Register alerts
    high_response_time_alert = Alert(
        name="high_response_time",
        condition="mean_response_time > 1.0",
        severity=AlertSeverity.WARNING,
        threshold=1.0,
        duration=timedelta(minutes=2)
    )
    monitor.register_alert(high_response_time_alert)
    
    # Add alert handlers
    monitor.add_alert_handler(console_alert_handler)
    monitor.add_alert_handler(lambda data: file_alert_handler(data, "performance_alerts.log"))
    
    # Start monitoring
    await monitor.start_monitoring(interval=2.0)
    
    try:
        print("Running performance monitoring demo...")
        
        # Simulate some activity
        for i in range(20):
            try:
                await example_function(monitor)
            except ValueError:
                pass  # Expected random errors
            
            # Add some custom metrics
            monitor.record_timer("custom_operation", 0.05 + i * 0.01)
            monitor.set_gauge("custom_gauge", i * 10)
            
            await asyncio.sleep(0.5)
        
        # Print metrics summary
        print("\nMetrics Summary:")
        summary = monitor.get_metrics_summary()
        print(json.dumps(summary, indent=2))
        
        # Export metrics
        export_data = monitor.export_metrics(timedelta(minutes=1))
        with open("metrics_export.json", "w") as f:
            json.dump(export_data, f, indent=2)
        print("\nMetrics exported to metrics_export.json")
        
    finally:
        await monitor.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())