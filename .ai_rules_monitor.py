#!/usr/bin/env python3
"""
 =============================================================================
 AI RULES MONITORING AND ALERTING SYSTEM
 =============================================================================
 Enterprise-grade monitoring, alerting, and observability for AI Rules system.
 Provides real-time monitoring, anomaly detection, and automated alerting.
"""

import os
import sys
import json
import time
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil not available, monitoring will be limited")

import time
import json
import os
import sys
import subprocess
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import hashlib

# Add home directory to path
sys.path.append(str(Path.home()))

try:
    from ai_rules_integration import check_compliance
except ImportError:
    print("Warning: AI rules integration not available")
    check_compliance = None

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class MonitoringConfig:
    """Configuration for monitoring system"""
    
    # Monitoring intervals
    health_check_interval: int = 60  # seconds
    performance_check_interval: int = 300  # seconds
    log_monitoring_interval: int = 30  # seconds
    
    # Alerting thresholds
    cpu_threshold: float = 80.0  # percentage
    memory_threshold: float = 85.0  # percentage
    disk_threshold: float = 90.0  # percentage
    error_rate_threshold: float = 5.0  # errors per minute
    
    # Log files to monitor
    log_files: List[str] = None
    alert_log_file: str = None
    metrics_file: str = None
    
    # Email alerting (optional)
    smtp_server: str = None
    smtp_port: int = 587
    smtp_username: str = None
    smtp_password: str = None
    alert_recipients: List[str] = None
    
    def __post_init__(self):
        if self.log_files is None:
            self.log_files = [
                str(Path.home() / "logs" / "ai_agent_startup.log"),
                str(Path.home() / "logs" / "ai_rules_enforcement.log"),
                str(Path.home() / "logs" / "ai_rules_deployment" / "deployment_*.log")
            ]
        
        if self.alert_log_file is None:
            self.alert_log_file = str(Path.home() / "logs" / "ai_rules_alerts.log")
        
        if self.metrics_file is None:
            self.metrics_file = str(Path.home() / "logs" / "ai_rules_metrics.jsonl")
        
        if self.alert_recipients is None:
            self.alert_recipients = []

class AlertSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class Alert:
    """Alert data structure"""
    timestamp: datetime
    severity: AlertSeverity
    source: str
    message: str
    details: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        if self.resolved_at:
            data['resolved_at'] = self.resolved_at.isoformat()
        data['severity'] = self.severity.value
        return data

# =============================================================================
# MONITORING CORE
# =============================================================================

class AIRulesMonitor:
    """Main monitoring system for AI Rules"""
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self.logger = self._setup_logging()
        self.alert_queue = queue.Queue()
        self.metrics_history = []
        self.active_alerts = {}
        self.monitoring_active = False
        self.threads = []
        
        # Ensure log directory exists
        Path(self.config.alert_log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Load previous metrics
        self._load_metrics_history()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the monitoring system"""
        logger = logging.getLogger('ai_rules_monitor')
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(self.config.alert_log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _load_metrics_history(self):
        """Load historical metrics from file"""
        try:
            metrics_file = Path(self.config.metrics_file)
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            self.metrics_history.append(json.loads(line))
                
                # Keep only last 1000 entries
                self.metrics_history = self.metrics_history[-1000:]
        except Exception as e:
            self.logger.warning(f"Could not load metrics history: {e}")
    
    def _save_metrics(self, metrics: Dict[str, Any]):
        """Save metrics to file"""
        try:
            with open(self.config.metrics_file, 'a') as f:
                f.write(json.dumps(metrics) + '\n')
        except Exception as e:
            self.logger.error(f"Could not save metrics: {e}")
    
    def start_monitoring(self):
        """Start all monitoring threads"""
        if self.monitoring_active:
            self.logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.logger.info("Starting AI Rules monitoring system")
        
        # Start monitoring threads
        threads = [
            threading.Thread(target=self._health_check_loop, daemon=True),
            threading.Thread(target=self._performance_monitoring_loop, daemon=True),
            threading.Thread(target=self._log_monitoring_loop, daemon=True),
            threading.Thread(target=self._alert_processing_loop, daemon=True),
        ]
        
        for thread in threads:
            thread.start()
            self.threads.append(thread)
        
        self.logger.info(f"Started {len(threads)} monitoring threads")
    
    def stop_monitoring(self):
        """Stop all monitoring threads"""
        self.monitoring_active = False
        self.logger.info("Stopping AI Rules monitoring system")
        
        # Wait for threads to finish
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        self.logger.info("Monitoring system stopped")
    
    # =============================================================================
    # MONITORING LOOPS
    # =============================================================================
    
    def _health_check_loop(self):
        """Continuous health checking"""
        while self.monitoring_active:
            try:
                health_status = self._perform_health_check()
                self._process_health_metrics(health_status)
                time.sleep(self.config.health_check_interval)
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
                time.sleep(10)  # Short delay on error
    
    def _performance_monitoring_loop(self):
        """Continuous performance monitoring"""
        while self.monitoring_active:
            try:
                performance_metrics = self._collect_performance_metrics()
                self._process_performance_metrics(performance_metrics)
                time.sleep(self.config.performance_check_interval)
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                time.sleep(30)
    
    def _log_monitoring_loop(self):
        """Continuous log monitoring"""
        while self.monitoring_active:
            try:
                log_metrics = self._monitor_log_files()
                self._process_log_metrics(log_metrics)
                time.sleep(self.config.log_monitoring_interval)
            except Exception as e:
                self.logger.error(f"Log monitoring error: {e}")
                time.sleep(15)
    
    def _alert_processing_loop(self):
        """Process alerts from queue"""
        while self.monitoring_active:
            try:
                # Process alerts with timeout
                try:
                    alert = self.alert_queue.get(timeout=1)
                    self._handle_alert(alert)
                    self.alert_queue.task_done()
                except queue.Empty:
                    continue
            except Exception as e:
                self.logger.error(f"Alert processing error: {e}")
    
    # =============================================================================
    # HEALTH CHECKING
    # =============================================================================
    
    def _perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'checks': {}
        }
        
        # Core file checks
        core_files = {
            'ai_agent_rules': Path.home() / '.ai_agent_rules',
            'ai_agent_startup': Path.home() / '.ai_agent_startup.sh',
            'ai_rules_loader': Path.home() / '.ai_rules_loader.sh',
            'ai_rules_integration': Path.home() / '.ai_rules_integration.py'
        }
        
        file_status = {}
        all_files_present = True
        
        for name, file_path in core_files.items():
            status = {
                'exists': file_path.exists(),
                'readable': False,
                'executable': False,
                'size': 0,
                'modified': None
            }
            
            if file_path.exists():
                stat = file_path.stat()
                status.update({
                    'readable': os.access(file_path, os.R_OK),
                    'executable': os.access(file_path, os.X_OK) if file_path.suffix == '.sh' else False,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            else:
                all_files_present = False
            
            file_status[name] = status
        
        health_status['checks']['core_files'] = file_status
        
        # Function availability checks
        function_status = {}
        try:
            # Test shell integration
            result = subprocess.run(
                ['bash', '-c', 'source ~/.ai_agent_startup.sh && type ai_validate_operation'],
                capture_output=True,
                text=True,
                timeout=10
            )
            function_status['ai_validate_operation'] = result.returncode == 0
        except Exception:
            function_status['ai_validate_operation'] = False
        
        # Python integration check
        if check_compliance:
            try:
                compliance = check_compliance()
                function_status['python_integration'] = compliance.get('rules_active', False)
            except Exception:
                function_status['python_integration'] = False
        else:
            function_status['python_integration'] = False
        
        health_status['checks']['functions'] = function_status
        
        # Environment variable checks
        env_vars = ['AI_RULES_ACTIVE', 'AI_RULES_VERSION', 'AI_AGENT_NAME']
        env_status = {}
        
        for var in env_vars:
            env_status[var] = {
                'set': var in os.environ,
                'value': os.environ.get(var, '')[:50]  # Truncate long values
            }
        
        health_status['checks']['environment'] = env_status
        
        # Determine overall status
        if all_files_present and all(function_status.values()):
            health_status['overall_status'] = 'healthy'
        else:
            health_status['overall_status'] = 'unhealthy'
        
        return health_status
    
    def _process_health_metrics(self, health_status: Dict[str, Any]):
        """Process health check results and generate alerts"""
        timestamp = datetime.now()
        
        # Check for critical issues
        if health_status['overall_status'] == 'unhealthy':
            # Check core files
            for file_name, file_status in health_status['checks']['core_files'].items():
                if not file_status['exists']:
                    self._create_alert(
                        AlertSeverity.CRITICAL,
                        'health_check',
                        f"Critical file missing: {file_name}",
                        {'file': file_name, 'health_check': health_status}
                    )
            
            # Check functions
            for func_name, func_status in health_status['checks']['functions'].items():
                if not func_status:
                    self._create_alert(
                        AlertSeverity.HIGH,
                        'health_check',
                        f"Function unavailable: {func_name}",
                        {'function': func_name, 'health_check': health_status}
                    )
        
        # Save metrics
        self._save_metrics({
            'type': 'health_check',
            'timestamp': timestamp.isoformat(),
            'data': health_status
        })
    
    # =============================================================================
    # PERFORMANCE MONITORING
    # =============================================================================
    
    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'usage_percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count(),
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            },
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv
            }
        }
        
        # AI Rules specific metrics
        try:
            # Count running AI agent processes
            ai_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if any(agent in cmdline.lower() for agent in ['opencode', 'cursor', 'claude', 'copilot']):
                        ai_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline[:100]  # Truncate
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            metrics['ai_processes'] = {
                'count': len(ai_processes),
                'processes': ai_processes[:10]  # Limit to first 10
            }
        except Exception as e:
            metrics['ai_processes'] = {'error': str(e)}
        
        return metrics
    
    def _process_performance_metrics(self, metrics: Dict[str, Any]):
        """Process performance metrics and generate alerts"""
        timestamp = datetime.now()
        
        # CPU threshold check
        if metrics['cpu']['usage_percent'] > self.config.cpu_threshold:
            self._create_alert(
                AlertSeverity.HIGH,
                'performance',
                f"High CPU usage: {metrics['cpu']['usage_percent']:.1f}%",
                metrics
            )
        
        # Memory threshold check
        if metrics['memory']['percent'] > self.config.memory_threshold:
            self._create_alert(
                AlertSeverity.HIGH,
                'performance',
                f"High memory usage: {metrics['memory']['percent']:.1f}%",
                metrics
            )
        
        # Disk threshold check
        if metrics['disk']['percent'] > self.config.disk_threshold:
            self._create_alert(
                AlertSeverity.MEDIUM,
                'performance',
                f"High disk usage: {metrics['disk']['percent']:.1f}%",
                metrics
            )
        
        # Save metrics
        self._save_metrics({
            'type': 'performance',
            'timestamp': timestamp.isoformat(),
            'data': metrics
        })
    
    # =============================================================================
    # LOG MONITORING
    # =============================================================================
    
    def _monitor_log_files(self) -> Dict[str, Any]:
        """Monitor log files for errors and anomalies"""
        log_metrics = {
            'timestamp': datetime.now().isoformat(),
            'files': {}
        }
        
        for log_file_pattern in self.config.log_files:
            try:
                # Handle glob patterns
                log_files = list(Path.home().glob(log_file_pattern.replace(str(Path.home()), '~')))
                
                for log_file in log_files:
                    if not log_file.exists():
                        continue
                    
                    file_metrics = self._analyze_log_file(log_file)
                    log_metrics['files'][str(log_file)] = file_metrics
                    
            except Exception as e:
                log_metrics['files'][log_file_pattern] = {'error': str(e)}
        
        return log_metrics
    
    def _analyze_log_file(self, log_file: Path) -> Dict[str, Any]:
        """Analyze a single log file"""
        try:
            # Get file size and modification time
            stat = log_file.stat()
            
            # Read last N lines
            lines_to_read = 100
            lines = []
            
            with open(log_file, 'r') as f:
                for line in f:
                    lines.append(line.strip())
                    if len(lines) > lines_to_read:
                        lines.pop(0)
            
            # Analyze lines
            error_count = 0
            warning_count = 0
            critical_count = 0
            
            for line in lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in ['error', 'failed', 'exception']):
                    error_count += 1
                if any(keyword in line_lower for keyword in ['warning', 'warn']):
                    warning_count += 1
                if any(keyword in line_lower for keyword in ['critical', 'fatal']):
                    critical_count += 1
            
            return {
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'lines_analyzed': len(lines),
                'error_count': error_count,
                'warning_count': warning_count,
                'critical_count': critical_count,
                'error_rate': error_count / max(len(lines), 1) * 100
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _process_log_metrics(self, log_metrics: Dict[str, Any]):
        """Process log metrics and generate alerts"""
        timestamp = datetime.now()
        
        for file_path, file_metrics in log_metrics['files'].items():
            if 'error' in file_metrics:
                continue
            
            # Check error rate
            if file_metrics['error_rate'] > self.config.error_rate_threshold:
                self._create_alert(
                    AlertSeverity.MEDIUM,
                    'log_monitoring',
                    f"High error rate in {file_path}: {file_metrics['error_rate']:.1f}%",
                    file_metrics
                )
            
            # Check for critical errors
            if file_metrics['critical_count'] > 0:
                self._create_alert(
                    AlertSeverity.HIGH,
                    'log_monitoring',
                    f"Critical errors detected in {file_path}",
                    file_metrics
                )
        
        # Save metrics
        self._save_metrics({
            'type': 'log_monitoring',
            'timestamp': timestamp.isoformat(),
            'data': log_metrics
        })
    
    # =============================================================================
    # ALERT MANAGEMENT
    # =============================================================================
    
    def _create_alert(self, severity: AlertSeverity, source: str, message: str, details: Dict[str, Any]):
        """Create and queue an alert"""
        alert = Alert(
            timestamp=datetime.now(),
            severity=severity,
            source=source,
            message=message,
            details=details
        )
        
        # Check for duplicate alerts
        alert_key = self._generate_alert_key(alert)
        if alert_key in self.active_alerts:
            # Update existing alert
            existing_alert = self.active_alerts[alert_key]
            existing_alert.details.update(details)
            return
        
        # Add to active alerts and queue
        self.active_alerts[alert_key] = alert
        self.alert_queue.put(alert)
        
        self.logger.warning(f"ALERT [{severity.value.upper()}] {source}: {message}")
    
    def _generate_alert_key(self, alert: Alert) -> str:
        """Generate unique key for alert deduplication"""
        key_data = f"{alert.source}_{alert.severity.value}_{alert.message}"
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    def _handle_alert(self, alert: Alert):
        """Handle an alert (logging, notification, etc.)"""
        try:
            # Log alert
            alert_data = alert.to_dict()
            with open(self.config.alert_log_file, 'a') as f:
                f.write(json.dumps(alert_data) + '\n')
            
            # Send email notification if configured
            if self.config.smtp_server and self.config.alert_recipients:
                self._send_email_alert(alert)
            
            # Auto-resolve some alerts after timeout
            if alert.severity in [AlertSeverity.LOW, AlertSeverity.INFO]:
                # Auto-resolve low severity alerts after 5 minutes
                threading.Timer(300, lambda: self._resolve_alert(alert)).start()
            
        except Exception as e:
            self.logger.error(f"Error handling alert: {e}")
    
    def _send_email_alert(self, alert: Alert):
        """Send email alert notification"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg['From'] = self.config.smtp_username
            msg['To'] = ', '.join(self.config.alert_recipients)
            msg['Subject'] = f"AI Rules Alert [{alert.severity.value.upper()}] {alert.source}"
            
            body = f"""
AI Rules System Alert

Severity: {alert.severity.value.upper()}
Source: {alert.source}
Time: {alert.timestamp}
Message: {alert.message}

Details:
{json.dumps(alert.details, indent=2)}

---
AI Rules Monitoring System
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            server.starttls()
            server.login(self.config.smtp_username, self.config.smtp_password)
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email alert sent for {alert.source}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    def _resolve_alert(self, alert: Alert):
        """Resolve an alert"""
        alert.resolved = True
        alert.resolved_at = datetime.now()
        
        # Remove from active alerts
        alert_key = self._generate_alert_key(alert)
        if alert_key in self.active_alerts:
            del self.active_alerts[alert_key]
        
        self.logger.info(f"Alert resolved: {alert.message}")
    
    # =============================================================================
    # PUBLIC API
    # =============================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            'monitoring_active': self.monitoring_active,
            'active_alerts_count': len(self.active_alerts),
            'metrics_history_count': len(self.metrics_history),
            'threads_active': len([t for t in self.threads if t.is_alive()]),
            'last_health_check': self._get_last_health_check_time(),
            'configuration': {
                'health_check_interval': self.config.health_check_interval,
                'performance_check_interval': self.config.performance_check_interval,
                'log_monitoring_interval': self.config.log_monitoring_interval,
                'cpu_threshold': self.config.cpu_threshold,
                'memory_threshold': self.config.memory_threshold,
                'disk_threshold': self.config.disk_threshold
            }
        }
    
    def _get_last_health_check_time(self) -> Optional[str]:
        """Get timestamp of last health check"""
        for metrics in reversed(self.metrics_history):
            if metrics.get('type') == 'health_check':
                return metrics.get('timestamp')
        return None
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        return [alert.to_dict() for alert in self.active_alerts.values()]
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m['timestamp']) > cutoff_time
        ]
        
        summary = {
            'period_hours': hours,
            'total_metrics': len(recent_metrics),
            'metrics_by_type': {},
            'alerts_summary': {}
        }
        
        # Group by type
        for metrics in recent_metrics:
            metric_type = metrics.get('type', 'unknown')
            summary['metrics_by_type'][metric_type] = summary['metrics_by_type'].get(metric_type, 0) + 1
        
        return summary

# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI interface for the monitoring system"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Rules Monitoring System')
    parser.add_argument('command', choices=['start', 'stop', 'status', 'alerts', 'metrics'], 
                       help='Command to execute')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--hours', type=int, default=24, help='Hours for metrics summary')
    
    args = parser.parse_args()
    
    # Load configuration
    config = MonitoringConfig()
    if args.config and Path(args.config).exists():
        with open(args.config, 'r') as f:
            config_data = json.load(f)
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
    
    # Initialize monitor
    monitor = AIRulesMonitor(config)
    
    if args.command == 'start':
        print("Starting AI Rules monitoring...")
        monitor.start_monitoring()
        
        try:
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            monitor.stop_monitoring()
    
    elif args.command == 'status':
        status = monitor.get_status()
        print(json.dumps(status, indent=2))
    
    elif args.command == 'alerts':
        alerts = monitor.get_active_alerts()
        print(f"Active Alerts: {len(alerts)}")
        for alert in alerts:
            print(f"[{alert['severity'].upper()}] {alert['source']}: {alert['message']}")
    
    elif args.command == 'metrics':
        summary = monitor.get_metrics_summary(args.hours)
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()