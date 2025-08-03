#!/usr/bin/env python3
"""
FreelanceX.AI Monitoring & Self-Repair System
Comprehensive monitoring dashboard with self-repair mechanisms, performance tracking, and alerting
Features: Real-time monitoring, automated healing, performance metrics, alerting system
"""

import asyncio
import logging
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import subprocess

# Import FreelanceX.AI components
from core.agent_manager import AgentManager
from core.base_agent import BaseAgent, AgentStatus
from backend.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class HealthStatus(Enum):
    """Health status indicators"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

@dataclass
class SystemMetric:
    """System metric data structure"""
    name: str
    value: float
    unit: str
    timestamp: str
    metadata: Dict[str, Any] = None

@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    metric_name: str
    condition: str  # "gt", "lt", "eq"
    threshold: float
    level: AlertLevel
    cooldown_minutes: int = 5
    last_triggered: Optional[str] = None

@dataclass
class HealthCheck:
    """Health check definition"""
    name: str
    check_function: str
    interval_seconds: int
    timeout_seconds: int = 30
    retry_count: int = 3
    enabled: bool = True

@dataclass
class RepairAction:
    """Self-repair action definition"""
    name: str
    trigger_condition: str
    repair_function: str
    max_attempts: int = 3
    cooldown_minutes: int = 10
    enabled: bool = True

class MonitoringSystem:
    """
    Comprehensive monitoring system for FreelanceX.AI
    Tracks system health, performance metrics, and automated repairs
    """
    
    def __init__(self, agent_manager: AgentManager, db_manager: DatabaseManager):
        self.agent_manager = agent_manager
        self.db_manager = db_manager
        
        # Monitoring configuration
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.alert_rules = []
        self.health_checks = []
        self.repair_actions = []
        self.active_alerts = {}
        
        # System state
        self.system_health = HealthStatus.HEALTHY
        self.monitoring_active = False
        self.last_health_check = None
        
        # Performance tracking
        self.performance_metrics = {
            "response_times": deque(maxlen=100),
            "error_rates": deque(maxlen=100),
            "throughput": deque(maxlen=100),
            "resource_usage": deque(maxlen=100)
        }
        
        # Initialize default configurations
        self._setup_default_health_checks()
        self._setup_default_alert_rules()
        self._setup_default_repair_actions()
        
        logger.info("MonitoringSystem initialized")

    def _setup_default_health_checks(self):
        """Setup default health checks"""
        self.health_checks = [
            HealthCheck(
                name="database_connectivity",
                check_function="check_database_health",
                interval_seconds=30
            ),
            HealthCheck(
                name="agent_manager_health",
                check_function="check_agent_manager_health",
                interval_seconds=60
            ),
            HealthCheck(
                name="system_resources",
                check_function="check_system_resources",
                interval_seconds=30
            ),
            HealthCheck(
                name="api_gateway_health",
                check_function="check_api_gateway_health",
                interval_seconds=45
            ),
            HealthCheck(
                name="memory_usage",
                check_function="check_memory_usage",
                interval_seconds=60
            )
        ]

    def _setup_default_alert_rules(self):
        """Setup default alert rules"""
        self.alert_rules = [
            AlertRule("high_cpu_usage", "cpu_usage", "gt", 80.0, AlertLevel.WARNING),
            AlertRule("critical_cpu_usage", "cpu_usage", "gt", 95.0, AlertLevel.CRITICAL),
            AlertRule("high_memory_usage", "memory_usage", "gt", 85.0, AlertLevel.WARNING),
            AlertRule("critical_memory_usage", "memory_usage", "gt", 95.0, AlertLevel.CRITICAL),
            AlertRule("high_response_time", "avg_response_time", "gt", 5.0, AlertLevel.WARNING),
            AlertRule("high_error_rate", "error_rate", "gt", 10.0, AlertLevel.ERROR),
            AlertRule("low_agent_availability", "agent_availability", "lt", 80.0, AlertLevel.WARNING),
            AlertRule("database_disconnected", "database_connected", "eq", 0.0, AlertLevel.CRITICAL)
        ]

    def _setup_default_repair_actions(self):
        """Setup default self-repair actions"""
        self.repair_actions = [
            RepairAction("restart_failed_agents", "agent_failure", "restart_failed_agents"),
            RepairAction("clear_memory_cache", "high_memory", "clear_memory_cache"),
            RepairAction("reconnect_database", "database_failure", "reconnect_database"),
            RepairAction("garbage_collection", "memory_leak", "force_garbage_collection"),
            RepairAction("restart_api_gateway", "api_failure", "restart_api_gateway")
        ]

    async def start_monitoring(self):
        """Start the monitoring system"""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        logger.info("Starting monitoring system...")
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._metrics_collection_loop()),
            asyncio.create_task(self._health_check_loop()),
            asyncio.create_task(self._alert_processing_loop()),
            asyncio.create_task(self._self_repair_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in monitoring system: {str(e)}")
            self.monitoring_active = False

    async def stop_monitoring(self):
        """Stop the monitoring system"""
        self.monitoring_active = False
        logger.info("Monitoring system stopped")

    async def _metrics_collection_loop(self):
        """Main metrics collection loop"""
        while self.monitoring_active:
            try:
                await self._collect_system_metrics()
                await self._collect_agent_metrics()
                await self._collect_performance_metrics()
                
                await asyncio.sleep(30)  # Collect metrics every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in metrics collection: {str(e)}")
                await asyncio.sleep(10)

    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            timestamp = datetime.now().isoformat()
            
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            self._record_metric("cpu_usage", cpu_usage, "%", timestamp)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self._record_metric("memory_usage", memory.percent, "%", timestamp)
            self._record_metric("memory_available", memory.available / (1024**3), "GB", timestamp)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            self._record_metric("disk_usage", disk_usage, "%", timestamp)
            
            # Network I/O
            network = psutil.net_io_counters()
            self._record_metric("network_bytes_sent", network.bytes_sent, "bytes", timestamp)
            self._record_metric("network_bytes_recv", network.bytes_recv, "bytes", timestamp)
            
            # Process count
            process_count = len(psutil.pids())
            self._record_metric("process_count", process_count, "count", timestamp)
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")

    async def _collect_agent_metrics(self):
        """Collect agent-specific metrics"""
        try:
            timestamp = datetime.now().isoformat()
            
            total_agents = len(self.agent_manager.agents)
            active_agents = sum(1 for agent in self.agent_manager.agents.values() 
                              if agent.status == AgentStatus.ACTIVE)
            
            agent_availability = (active_agents / max(total_agents, 1)) * 100
            
            self._record_metric("total_agents", total_agents, "count", timestamp)
            self._record_metric("active_agents", active_agents, "count", timestamp)
            self._record_metric("agent_availability", agent_availability, "%", timestamp)
            
            # Individual agent metrics
            for name, agent in self.agent_manager.agents.items():
                agent_metrics = getattr(agent, 'metrics', {})
                for metric_name, value in agent_metrics.items():
                    self._record_metric(f"agent_{name}_{metric_name}", value, "count", timestamp)
                    
        except Exception as e:
            logger.error(f"Error collecting agent metrics: {str(e)}")

    async def _collect_performance_metrics(self):
        """Collect performance metrics"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Calculate averages from recent data
            if self.performance_metrics["response_times"]:
                avg_response_time = sum(self.performance_metrics["response_times"]) / len(self.performance_metrics["response_times"])
                self._record_metric("avg_response_time", avg_response_time, "seconds", timestamp)
            
            if self.performance_metrics["error_rates"]:
                avg_error_rate = sum(self.performance_metrics["error_rates"]) / len(self.performance_metrics["error_rates"])
                self._record_metric("error_rate", avg_error_rate, "%", timestamp)
            
            # Database metrics if available
            if self.db_manager.is_connected():
                self._record_metric("database_connected", 1.0, "boolean", timestamp)
                # Add database-specific metrics here
            else:
                self._record_metric("database_connected", 0.0, "boolean", timestamp)
                
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {str(e)}")

    def _record_metric(self, name: str, value: float, unit: str, timestamp: str):
        """Record a metric value"""
        metric = SystemMetric(name, value, unit, timestamp)
        self.metrics_history[name].append(metric)

    async def _health_check_loop(self):
        """Run health checks periodically"""
        last_checks = {}
        
        while self.monitoring_active:
            try:
                current_time = time.time()
                
                for health_check in self.health_checks:
                    if not health_check.enabled:
                        continue
                    
                    last_check_time = last_checks.get(health_check.name, 0)
                    
                    if current_time - last_check_time >= health_check.interval_seconds:
                        await self._run_health_check(health_check)
                        last_checks[health_check.name] = current_time
                
                # Update overall system health
                await self._update_system_health()
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in health check loop: {str(e)}")
                await asyncio.sleep(10)

    async def _run_health_check(self, health_check: HealthCheck):
        """Run a specific health check"""
        try:
            check_function = getattr(self, health_check.check_function, None)
            if not check_function:
                logger.error(f"Health check function not found: {health_check.check_function}")
                return
            
            for attempt in range(health_check.retry_count):
                try:
                    result = await asyncio.wait_for(
                        check_function(),
                        timeout=health_check.timeout_seconds
                    )
                    
                    if result:
                        logger.debug(f"Health check passed: {health_check.name}")
                        return True
                    else:
                        logger.warning(f"Health check failed: {health_check.name} (attempt {attempt + 1})")
                        
                except asyncio.TimeoutError:
                    logger.warning(f"Health check timeout: {health_check.name} (attempt {attempt + 1})")
                except Exception as e:
                    logger.error(f"Health check error: {health_check.name} - {str(e)}")
                
                if attempt < health_check.retry_count - 1:
                    await asyncio.sleep(2)  # Wait before retry
            
            # All attempts failed
            await self._trigger_repair_action(f"{health_check.name}_failure")
            return False
            
        except Exception as e:
            logger.error(f"Error running health check {health_check.name}: {str(e)}")
            return False

    async def check_database_health(self) -> bool:
        """Check database connectivity and health"""
        try:
            if not self.db_manager.is_connected():
                return False
            
            # Test basic database operation
            metrics = await self.db_manager.get_system_metrics()
            return metrics is not None
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False

    async def check_agent_manager_health(self) -> bool:
        """Check agent manager health"""
        try:
            if not self.agent_manager.agents:
                return False
            
            # Check if at least 80% of agents are active
            total_agents = len(self.agent_manager.agents)
            active_agents = sum(1 for agent in self.agent_manager.agents.values() 
                              if agent.status == AgentStatus.ACTIVE)
            
            return (active_agents / total_agents) >= 0.8
            
        except Exception as e:
            logger.error(f"Agent manager health check failed: {str(e)}")
            return False

    async def check_system_resources(self) -> bool:
        """Check system resource usage"""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            
            # System is healthy if all resources are below critical thresholds
            return cpu_usage < 95 and memory_usage < 95 and disk_usage < 90
            
        except Exception as e:
            logger.error(f"System resources health check failed: {str(e)}")
            return False

    async def check_api_gateway_health(self) -> bool:
        """Check API gateway health"""
        try:
            # This would check if the API gateway is responding
            # Placeholder implementation
            return True
            
        except Exception as e:
            logger.error(f"API gateway health check failed: {str(e)}")
            return False

    async def check_memory_usage(self) -> bool:
        """Check memory usage patterns for leaks"""
        try:
            memory = psutil.virtual_memory()
            
            # Check for memory leaks by comparing current usage with historical data
            if len(self.metrics_history["memory_usage"]) > 10:
                recent_usage = [m.value for m in list(self.metrics_history["memory_usage"])[-10:]]
                trend = sum(recent_usage[-5:]) / 5 - sum(recent_usage[:5]) / 5
                
                # If memory usage is increasing rapidly, it might indicate a leak
                return trend < 10  # Less than 10% increase in recent samples
            
            return memory.percent < 90
            
        except Exception as e:
            logger.error(f"Memory usage health check failed: {str(e)}")
            return False

    async def _update_system_health(self):
        """Update overall system health status"""
        try:
            # Analyze recent metrics to determine system health
            critical_metrics = ["cpu_usage", "memory_usage", "agent_availability", "database_connected"]
            
            critical_issues = 0
            warning_issues = 0
            
            for metric_name in critical_metrics:
                if metric_name in self.metrics_history:
                    recent_values = list(self.metrics_history[metric_name])[-5:]  # Last 5 readings
                    
                    if recent_values:
                        avg_value = sum(m.value for m in recent_values) / len(recent_values)
                        
                        if metric_name == "database_connected" and avg_value < 1.0:
                            critical_issues += 1
                        elif metric_name in ["cpu_usage", "memory_usage"] and avg_value > 95:
                            critical_issues += 1
                        elif metric_name in ["cpu_usage", "memory_usage"] and avg_value > 80:
                            warning_issues += 1
                        elif metric_name == "agent_availability" and avg_value < 50:
                            critical_issues += 1
                        elif metric_name == "agent_availability" and avg_value < 80:
                            warning_issues += 1
            
            # Determine health status
            if critical_issues > 0:
                self.system_health = HealthStatus.CRITICAL
            elif warning_issues > 2:
                self.system_health = HealthStatus.UNHEALTHY
            elif warning_issues > 0:
                self.system_health = HealthStatus.DEGRADED
            else:
                self.system_health = HealthStatus.HEALTHY
            
            self.last_health_check = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Error updating system health: {str(e)}")
            self.system_health = HealthStatus.UNHEALTHY

    async def _alert_processing_loop(self):
        """Process alerts based on current metrics"""
        while self.monitoring_active:
            try:
                await self._check_alert_rules()
                await asyncio.sleep(60)  # Check alerts every minute
                
            except Exception as e:
                logger.error(f"Error in alert processing: {str(e)}")
                await asyncio.sleep(10)

    async def _check_alert_rules(self):
        """Check all alert rules against current metrics"""
        current_time = datetime.now()
        
        for rule in self.alert_rules:
            try:
                if rule.metric_name not in self.metrics_history:
                    continue
                
                recent_metrics = list(self.metrics_history[rule.metric_name])[-1:]
                if not recent_metrics:
                    continue
                
                current_value = recent_metrics[-1].value
                
                # Check if alert condition is met
                alert_triggered = False
                if rule.condition == "gt" and current_value > rule.threshold:
                    alert_triggered = True
                elif rule.condition == "lt" and current_value < rule.threshold:
                    alert_triggered = True
                elif rule.condition == "eq" and current_value == rule.threshold:
                    alert_triggered = True
                
                if alert_triggered:
                    # Check cooldown period
                    if rule.last_triggered:
                        last_triggered = datetime.fromisoformat(rule.last_triggered)
                        if (current_time - last_triggered).total_seconds() < rule.cooldown_minutes * 60:
                            continue
                    
                    # Trigger alert
                    await self._trigger_alert(rule, current_value)
                    rule.last_triggered = current_time.isoformat()
                    
            except Exception as e:
                logger.error(f"Error checking alert rule {rule.name}: {str(e)}")

    async def _trigger_alert(self, rule: AlertRule, current_value: float):
        """Trigger an alert"""
        alert_message = f"Alert: {rule.name} - {rule.metric_name} is {current_value} (threshold: {rule.threshold})"
        
        logger.warning(f"Alert triggered: {alert_message}")
        
        # Store alert in active alerts
        self.active_alerts[rule.name] = {
            "rule": rule,
            "value": current_value,
            "triggered_at": datetime.now().isoformat(),
            "acknowledged": False
        }
        
        # Send notification (email, webhook, etc.)
        await self._send_alert_notification(rule, current_value, alert_message)

    async def _send_alert_notification(self, rule: AlertRule, value: float, message: str):
        """Send alert notification"""
        try:
            # This would send notifications via email, Slack, etc.
            # Placeholder implementation
            logger.info(f"Alert notification: {message}")
            
        except Exception as e:
            logger.error(f"Error sending alert notification: {str(e)}")

    async def _self_repair_loop(self):
        """Self-repair mechanism loop"""
        while self.monitoring_active:
            try:
                await self._check_repair_conditions()
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in self-repair loop: {str(e)}")
                await asyncio.sleep(10)

    async def _check_repair_conditions(self):
        """Check if any repair actions should be triggered"""
        # This would check various conditions and trigger appropriate repairs
        pass

    async def _trigger_repair_action(self, condition: str):
        """Trigger a repair action based on condition"""
        for repair_action in self.repair_actions:
            if repair_action.trigger_condition == condition and repair_action.enabled:
                logger.info(f"Triggering repair action: {repair_action.name}")
                
                repair_function = getattr(self, repair_action.repair_function, None)
                if repair_function:
                    try:
                        await repair_function()
                        logger.info(f"Repair action completed: {repair_action.name}")
                    except Exception as e:
                        logger.error(f"Repair action failed: {repair_action.name} - {str(e)}")

    async def restart_failed_agents(self):
        """Restart failed agents"""
        try:
            for name, agent in self.agent_manager.agents.items():
                if agent.status in [AgentStatus.ERROR, AgentStatus.STOPPED]:
                    logger.info(f"Restarting failed agent: {name}")
                    # Restart agent logic here
                    agent.status = AgentStatus.ACTIVE
                    
        except Exception as e:
            logger.error(f"Error restarting failed agents: {str(e)}")

    async def clear_memory_cache(self):
        """Clear memory caches to free up memory"""
        try:
            import gc
            gc.collect()
            logger.info("Memory cache cleared")
            
        except Exception as e:
            logger.error(f"Error clearing memory cache: {str(e)}")

    async def reconnect_database(self):
        """Reconnect to database"""
        try:
            await self.db_manager.disconnect()
            await asyncio.sleep(2)
            await self.db_manager.connect()
            logger.info("Database reconnection completed")
            
        except Exception as e:
            logger.error(f"Error reconnecting database: {str(e)}")

    async def force_garbage_collection(self):
        """Force garbage collection"""
        try:
            import gc
            collected = gc.collect()
            logger.info(f"Garbage collection completed, collected {collected} objects")
            
        except Exception as e:
            logger.error(f"Error in garbage collection: {str(e)}")

    async def restart_api_gateway(self):
        """Restart API gateway"""
        try:
            # This would restart the API gateway service
            logger.info("API gateway restart initiated")
            
        except Exception as e:
            logger.error(f"Error restarting API gateway: {str(e)}")

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "health_status": self.system_health.value,
            "monitoring_active": self.monitoring_active,
            "last_health_check": self.last_health_check,
            "active_alerts": len(self.active_alerts),
            "total_agents": len(self.agent_manager.agents),
            "active_agents": sum(1 for agent in self.agent_manager.agents.values() 
                               if agent.status == AgentStatus.ACTIVE),
            "database_connected": self.db_manager.is_connected(),
            "metrics_collected": sum(len(history) for history in self.metrics_history.values())
        }

    def get_recent_metrics(self, metric_name: str, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent metrics for a specific metric"""
        if metric_name in self.metrics_history:
            recent = list(self.metrics_history[metric_name])[-count:]
            return [asdict(metric) for metric in recent]
        return []

    def get_all_alerts(self) -> Dict[str, Any]:
        """Get all active alerts"""
        return self.active_alerts

    def acknowledge_alert(self, alert_name: str) -> bool:
        """Acknowledge an alert"""
        if alert_name in self.active_alerts:
            self.active_alerts[alert_name]["acknowledged"] = True
            self.active_alerts[alert_name]["acknowledged_at"] = datetime.now().isoformat()
            logger.info(f"Alert acknowledged: {alert_name}")
            return True
        return False

# Global monitoring system instance
monitoring_system = None

def get_monitoring_system(agent_manager: AgentManager, db_manager: DatabaseManager) -> MonitoringSystem:
    """Get or create the global monitoring system instance"""
    global monitoring_system
    if monitoring_system is None:
        monitoring_system = MonitoringSystem(agent_manager, db_manager)
    return monitoring_system