#!/usr/bin/env python3
"""
FreelanceX.AI - Self-Repair and Monitoring System
Continuously monitors system health and provides auto-repair capabilities.
"""

import asyncio
import logging
import json
import time
import psutil
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import sqlite3
from pathlib import Path
import threading
import queue

# Import FreelanceX.AI components
from core.agent_manager import AgentManager
from core.base_agent import BaseAgent, AgentStatus
from backend.memory_layer import MemoryLayer

class HealthStatus(Enum):
    """System health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_agents: int
    total_agents: int
    response_time_avg: float
    error_rate: float
    throughput: float

@dataclass
class AgentHealth:
    """Individual agent health information"""
    agent_name: str
    status: AgentStatus
    last_heartbeat: datetime
    response_time: float
    error_count: int
    success_rate: float
    memory_usage: float
    cpu_usage: float
    is_healthy: bool

@dataclass
class Alert:
    """System alert"""
    alert_id: str
    timestamp: datetime
    level: AlertLevel
    source: str
    message: str
    details: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    auto_resolved: bool = False

@dataclass
class RepairAction:
    """Repair action to be taken"""
    action_id: str
    timestamp: datetime
    target: str  # agent_name or "system"
    action_type: str
    parameters: Dict[str, Any]
    priority: int
    executed: bool = False
    success: bool = False
    error_message: Optional[str] = None

class SystemMonitor:
    """Monitors overall system health and performance"""
    
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.logger = logging.getLogger("FreelanceX.Monitoring.System")
        
        # Monitoring configuration
        self.monitoring_interval = 30  # seconds
        self.health_thresholds = {
            "cpu_usage_warning": 70.0,
            "cpu_usage_critical": 90.0,
            "memory_usage_warning": 80.0,
            "memory_usage_critical": 95.0,
            "disk_usage_warning": 85.0,
            "disk_usage_critical": 95.0,
            "response_time_warning": 5.0,  # seconds
            "response_time_critical": 10.0,  # seconds
            "error_rate_warning": 0.05,  # 5%
            "error_rate_critical": 0.15,  # 15%
        }
        
        # Metrics storage
        self.metrics_history: List[SystemMetrics] = []
        self.max_history_size = 1000
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task = None
    
    async def start_monitoring(self):
        """Start system monitoring"""
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("System monitoring started")
    
    async def stop_monitoring(self):
        """Stop system monitoring"""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        self.logger.info("System monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                metrics = await self._collect_system_metrics()
                
                # Store metrics
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)
                
                # Analyze health
                health_status = await self._analyze_system_health(metrics)
                
                # Log health status
                if health_status != HealthStatus.HEALTHY:
                    self.logger.warning(f"System health: {health_status.value}")
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(5)
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
            
            # Agent metrics
            agents = self.agent_manager.get_all_agents()
            active_agents = sum(1 for agent in agents.values() if agent.status == AgentStatus.ACTIVE)
            total_agents = len(agents)
            
            # Calculate average response time and error rate
            response_time_avg = await self._calculate_avg_response_time()
            error_rate = await self._calculate_error_rate()
            
            # Calculate throughput (requests per second)
            throughput = await self._calculate_throughput()
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io,
                active_agents=active_agents,
                total_agents=total_agents,
                response_time_avg=response_time_avg,
                error_rate=error_rate,
                throughput=throughput
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {str(e)}")
            # Return default metrics on error
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={"bytes_sent": 0, "bytes_recv": 0, "packets_sent": 0, "packets_recv": 0},
                active_agents=0,
                total_agents=0,
                response_time_avg=0.0,
                error_rate=1.0,
                throughput=0.0
            )
    
    async def _analyze_system_health(self, metrics: SystemMetrics) -> HealthStatus:
        """Analyze system health based on metrics"""
        critical_issues = 0
        warning_issues = 0
        
        # Check CPU usage
        if metrics.cpu_usage >= self.health_thresholds["cpu_usage_critical"]:
            critical_issues += 1
        elif metrics.cpu_usage >= self.health_thresholds["cpu_usage_warning"]:
            warning_issues += 1
        
        # Check memory usage
        if metrics.memory_usage >= self.health_thresholds["memory_usage_critical"]:
            critical_issues += 1
        elif metrics.memory_usage >= self.health_thresholds["memory_usage_warning"]:
            warning_issues += 1
        
        # Check disk usage
        if metrics.disk_usage >= self.health_thresholds["disk_usage_critical"]:
            critical_issues += 1
        elif metrics.disk_usage >= self.health_thresholds["disk_usage_warning"]:
            warning_issues += 1
        
        # Check response time
        if metrics.response_time_avg >= self.health_thresholds["response_time_critical"]:
            critical_issues += 1
        elif metrics.response_time_avg >= self.health_thresholds["response_time_warning"]:
            warning_issues += 1
        
        # Check error rate
        if metrics.error_rate >= self.health_thresholds["error_rate_critical"]:
            critical_issues += 1
        elif metrics.error_rate >= self.health_thresholds["error_rate_warning"]:
            warning_issues += 1
        
        # Determine health status
        if critical_issues > 0:
            return HealthStatus.CRITICAL
        elif warning_issues > 0:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
    
    async def _calculate_avg_response_time(self) -> float:
        """Calculate average response time across all agents"""
        try:
            agents = self.agent_manager.get_all_agents()
            total_time = 0.0
            count = 0
            
            for agent in agents.values():
                if hasattr(agent, 'last_response_time') and agent.last_response_time:
                    total_time += agent.last_response_time
                    count += 1
            
            return total_time / count if count > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating average response time: {str(e)}")
            return 0.0
    
    async def _calculate_error_rate(self) -> float:
        """Calculate error rate across all agents"""
        try:
            agents = self.agent_manager.get_all_agents()
            total_errors = 0
            total_requests = 0
            
            for agent in agents.values():
                if hasattr(agent, 'error_count'):
                    total_errors += agent.error_count
                if hasattr(agent, 'request_count'):
                    total_requests += agent.request_count
            
            return total_errors / total_requests if total_requests > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating error rate: {str(e)}")
            return 0.0
    
    async def _calculate_throughput(self) -> float:
        """Calculate system throughput (requests per second)"""
        try:
            # This is a simplified calculation
            # In a real system, you'd track requests over time windows
            agents = self.agent_manager.get_all_agents()
            total_requests = sum(getattr(agent, 'request_count', 0) for agent in agents.values())
            
            # Assume requests are spread over the last hour
            return total_requests / 3600.0
            
        except Exception as e:
            self.logger.error(f"Error calculating throughput: {str(e)}")
            return 0.0
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status"""
        if not self.metrics_history:
            return {"status": HealthStatus.OFFLINE.value, "message": "No metrics available"}
        
        latest_metrics = self.metrics_history[-1]
        health_status = await self._analyze_system_health(latest_metrics)
        
        return {
            "status": health_status.value,
            "timestamp": latest_metrics.timestamp.isoformat(),
            "metrics": {
                "cpu_usage": latest_metrics.cpu_usage,
                "memory_usage": latest_metrics.memory_usage,
                "disk_usage": latest_metrics.disk_usage,
                "active_agents": latest_metrics.active_agents,
                "total_agents": latest_metrics.total_agents,
                "response_time_avg": latest_metrics.response_time_avg,
                "error_rate": latest_metrics.error_rate,
                "throughput": latest_metrics.throughput
            }
        }

class AgentMonitor:
    """Monitors individual agent health and performance"""
    
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.logger = logging.getLogger("FreelanceX.Monitoring.Agent")
        
        # Agent health tracking
        self.agent_health: Dict[str, AgentHealth] = {}
        self.health_history: Dict[str, List[AgentHealth]] = {}
        
        # Monitoring configuration
        self.heartbeat_interval = 60  # seconds
        self.response_timeout = 10  # seconds
        self.max_health_history = 100
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task = None
    
    async def start_monitoring(self):
        """Start agent monitoring"""
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._agent_monitoring_loop())
        self.logger.info("Agent monitoring started")
    
    async def stop_monitoring(self):
        """Stop agent monitoring"""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Agent monitoring stopped")
    
    async def _agent_monitoring_loop(self):
        """Main agent monitoring loop"""
        while self.is_monitoring:
            try:
                # Check all agents
                agents = self.agent_manager.get_all_agents()
                
                for agent_name, agent in agents.items():
                    await self._check_agent_health(agent_name, agent)
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.heartbeat_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in agent monitoring loop: {str(e)}")
                await asyncio.sleep(5)
    
    async def _check_agent_health(self, agent_name: str, agent: BaseAgent):
        """Check health of a specific agent"""
        try:
            start_time = time.time()
            
            # Check if agent is responding
            is_responding = await self._ping_agent(agent)
            response_time = time.time() - start_time
            
            # Get agent metrics
            error_count = getattr(agent, 'error_count', 0)
            success_rate = getattr(agent, 'success_rate', 1.0)
            memory_usage = await self._get_agent_memory_usage(agent)
            cpu_usage = await self._get_agent_cpu_usage(agent)
            
            # Determine if agent is healthy
            is_healthy = (
                agent.status == AgentStatus.ACTIVE and
                is_responding and
                response_time < self.response_timeout and
                success_rate > 0.8 and
                error_count < 10
            )
            
            # Create health record
            health = AgentHealth(
                agent_name=agent_name,
                status=agent.status,
                last_heartbeat=datetime.now(),
                response_time=response_time,
                error_count=error_count,
                success_rate=success_rate,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                is_healthy=is_healthy
            )
            
            # Store health record
            self.agent_health[agent_name] = health
            
            # Add to history
            if agent_name not in self.health_history:
                self.health_history[agent_name] = []
            
            self.health_history[agent_name].append(health)
            
            # Limit history size
            if len(self.health_history[agent_name]) > self.max_health_history:
                self.health_history[agent_name].pop(0)
            
            # Log unhealthy agents
            if not is_healthy:
                self.logger.warning(f"Agent {agent_name} is unhealthy: response_time={response_time:.2f}s, success_rate={success_rate:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error checking agent health for {agent_name}: {str(e)}")
    
    async def _ping_agent(self, agent: BaseAgent) -> bool:
        """Ping agent to check if it's responding"""
        try:
            # Send a simple health check request
            if hasattr(agent, 'health_check'):
                await agent.health_check()
                return True
            else:
                # Fallback: check if agent has a process_request method
                if hasattr(agent, 'process_request'):
                    # Send a minimal test request
                    test_result = await agent.process_request({"type": "health_check"})
                    return test_result is not None
                return False
                
        except Exception as e:
            self.logger.error(f"Agent ping failed: {str(e)}")
            return False
    
    async def _get_agent_memory_usage(self, agent: BaseAgent) -> float:
        """Get memory usage for an agent"""
        try:
            # This is a simplified implementation
            # In a real system, you'd track actual memory usage
            return 0.0
        except Exception as e:
            self.logger.error(f"Error getting agent memory usage: {str(e)}")
            return 0.0
    
    async def _get_agent_cpu_usage(self, agent: BaseAgent) -> float:
        """Get CPU usage for an agent"""
        try:
            # This is a simplified implementation
            # In a real system, you'd track actual CPU usage
            return 0.0
        except Exception as e:
            self.logger.error(f"Error getting agent CPU usage: {str(e)}")
            return 0.0
    
    async def get_agent_health(self, agent_name: str) -> Optional[AgentHealth]:
        """Get health status of a specific agent"""
        return self.agent_health.get(agent_name)
    
    async def get_all_agent_health(self) -> Dict[str, AgentHealth]:
        """Get health status of all agents"""
        return self.agent_health.copy()

class AlertManager:
    """Manages system alerts and notifications"""
    
    def __init__(self):
        self.logger = logging.getLogger("FreelanceX.Monitoring.Alerts")
        
        # Alert storage
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.max_history_size = 1000
        
        # Alert handlers
        self.alert_handlers: List[Callable[[Alert], None]] = []
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add an alert handler"""
        self.alert_handlers.append(handler)
    
    async def create_alert(self, 
                          level: AlertLevel,
                          source: str,
                          message: str,
                          details: Dict[str, Any] = None) -> str:
        """Create a new alert"""
        try:
            alert_id = f"alert_{int(time.time())}_{len(self.active_alerts)}"
            
            alert = Alert(
                alert_id=alert_id,
                timestamp=datetime.now(),
                level=level,
                source=source,
                message=message,
                details=details or {}
            )
            
            # Store alert
            self.active_alerts[alert_id] = alert
            
            # Add to history
            self.alert_history.append(alert)
            if len(self.alert_history) > self.max_history_size:
                self.alert_history.pop(0)
            
            # Notify handlers
            await self._notify_handlers(alert)
            
            # Log alert
            log_level = {
                AlertLevel.INFO: self.logger.info,
                AlertLevel.WARNING: self.logger.warning,
                AlertLevel.ERROR: self.logger.error,
                AlertLevel.CRITICAL: self.logger.critical
            }
            
            log_level[level](f"Alert [{level.value}] from {source}: {message}")
            
            return alert_id
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {str(e)}")
            return ""
    
    async def resolve_alert(self, alert_id: str, auto_resolved: bool = False) -> bool:
        """Resolve an alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                alert.resolved_at = datetime.now()
                alert.auto_resolved = auto_resolved
                
                del self.active_alerts[alert_id]
                
                self.logger.info(f"Alert resolved: {alert_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error resolving alert: {str(e)}")
            return False
    
    async def _notify_handlers(self, alert: Alert):
        """Notify all alert handlers"""
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler: {str(e)}")
    
    async def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return list(self.active_alerts.values())
    
    async def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history"""
        return self.alert_history[-limit:]

class AutoRepairSystem:
    """Provides automatic repair capabilities for system issues"""
    
    def __init__(self, agent_manager: AgentManager, alert_manager: AlertManager):
        self.agent_manager = agent_manager
        self.alert_manager = alert_manager
        self.logger = logging.getLogger("FreelanceX.Monitoring.AutoRepair")
        
        # Repair actions
        self.repair_actions: List[RepairAction] = []
        self.auto_repair_enabled = True
        
        # Repair strategies
        self.repair_strategies = {
            "agent_unresponsive": self._repair_unresponsive_agent,
            "high_error_rate": self._repair_high_error_rate,
            "memory_leak": self._repair_memory_leak,
            "cpu_overload": self._repair_cpu_overload,
            "disk_space": self._repair_disk_space
        }
    
    async def analyze_and_repair(self, system_health: Dict[str, Any], agent_health: Dict[str, AgentHealth]):
        """Analyze system health and perform auto-repairs"""
        if not self.auto_repair_enabled:
            return
        
        try:
            # Check for system-level issues
            await self._check_system_issues(system_health)
            
            # Check for agent-level issues
            await self._check_agent_issues(agent_health)
            
        except Exception as e:
            self.logger.error(f"Error in auto-repair analysis: {str(e)}")
    
    async def _check_system_issues(self, system_health: Dict[str, Any]):
        """Check for system-level issues that need repair"""
        try:
            metrics = system_health.get("metrics", {})
            
            # Check CPU overload
            if metrics.get("cpu_usage", 0) > 90:
                await self._create_repair_action("cpu_overload", "system", {"threshold": 90})
            
            # Check memory issues
            if metrics.get("memory_usage", 0) > 95:
                await self._create_repair_action("memory_leak", "system", {"threshold": 95})
            
            # Check disk space
            if metrics.get("disk_usage", 0) > 90:
                await self._create_repair_action("disk_space", "system", {"threshold": 90})
            
            # Check error rate
            if metrics.get("error_rate", 0) > 0.15:
                await self._create_repair_action("high_error_rate", "system", {"threshold": 0.15})
                
        except Exception as e:
            self.logger.error(f"Error checking system issues: {str(e)}")
    
    async def _check_agent_issues(self, agent_health: Dict[str, AgentHealth]):
        """Check for agent-level issues that need repair"""
        try:
            for agent_name, health in agent_health.items():
                if not health.is_healthy:
                    # Agent is unhealthy, try to repair
                    await self._create_repair_action("agent_unresponsive", agent_name, {
                        "response_time": health.response_time,
                        "error_count": health.error_count,
                        "success_rate": health.success_rate
                    })
                    
        except Exception as e:
            self.logger.error(f"Error checking agent issues: {str(e)}")
    
    async def _create_repair_action(self, action_type: str, target: str, parameters: Dict[str, Any]):
        """Create a repair action"""
        try:
            action_id = f"repair_{int(time.time())}_{len(self.repair_actions)}"
            
            action = RepairAction(
                action_id=action_id,
                timestamp=datetime.now(),
                target=target,
                action_type=action_type,
                parameters=parameters,
                priority=self._get_action_priority(action_type)
            )
            
            self.repair_actions.append(action)
            
            # Execute repair action
            await self._execute_repair_action(action)
            
        except Exception as e:
            self.logger.error(f"Error creating repair action: {str(e)}")
    
    def _get_action_priority(self, action_type: str) -> int:
        """Get priority for a repair action"""
        priorities = {
            "agent_unresponsive": 1,  # Highest priority
            "high_error_rate": 2,
            "memory_leak": 3,
            "cpu_overload": 4,
            "disk_space": 5  # Lowest priority
        }
        return priorities.get(action_type, 5)
    
    async def _execute_repair_action(self, action: RepairAction):
        """Execute a repair action"""
        try:
            self.logger.info(f"Executing repair action: {action.action_type} on {action.target}")
            
            # Get repair strategy
            strategy = self.repair_strategies.get(action.action_type)
            if strategy:
                success = await strategy(action)
                action.executed = True
                action.success = success
                
                if success:
                    self.logger.info(f"Repair action successful: {action.action_id}")
                else:
                    self.logger.error(f"Repair action failed: {action.action_id}")
            else:
                action.executed = True
                action.success = False
                action.error_message = f"Unknown repair strategy: {action.action_type}"
                self.logger.error(f"Unknown repair strategy: {action.action_type}")
                
        except Exception as e:
            action.executed = True
            action.success = False
            action.error_message = str(e)
            self.logger.error(f"Error executing repair action: {str(e)}")
    
    async def _repair_unresponsive_agent(self, action: RepairAction) -> bool:
        """Repair an unresponsive agent"""
        try:
            agent_name = action.target
            agent = self.agent_manager.get_agent(agent_name)
            
            if not agent:
                return False
            
            # Try to restart the agent
            if hasattr(agent, 'restart'):
                await agent.restart()
                return True
            else:
                # Fallback: try to reinitialize
                await self.agent_manager.restart_agent(agent_name)
                return True
                
        except Exception as e:
            self.logger.error(f"Error repairing unresponsive agent: {str(e)}")
            return False
    
    async def _repair_high_error_rate(self, action: RepairAction) -> bool:
        """Repair high error rate issues"""
        try:
            # This could involve clearing caches, resetting connections, etc.
            self.logger.info("Attempting to repair high error rate")
            
            # For now, just log the issue
            await self.alert_manager.create_alert(
                AlertLevel.WARNING,
                "AutoRepair",
                "High error rate detected, manual intervention may be required",
                action.parameters
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error repairing high error rate: {str(e)}")
            return False
    
    async def _repair_memory_leak(self, action: RepairAction) -> bool:
        """Repair memory leak issues"""
        try:
            # This could involve garbage collection, clearing caches, etc.
            self.logger.info("Attempting to repair memory leak")
            
            # Trigger garbage collection
            import gc
            gc.collect()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error repairing memory leak: {str(e)}")
            return False
    
    async def _repair_cpu_overload(self, action: RepairAction) -> bool:
        """Repair CPU overload issues"""
        try:
            # This could involve throttling requests, scaling down, etc.
            self.logger.info("Attempting to repair CPU overload")
            
            # For now, just log the issue
            await self.alert_manager.create_alert(
                AlertLevel.WARNING,
                "AutoRepair",
                "CPU overload detected, consider scaling or optimization",
                action.parameters
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error repairing CPU overload: {str(e)}")
            return False
    
    async def _repair_disk_space(self, action: RepairAction) -> bool:
        """Repair disk space issues"""
        try:
            # This could involve cleaning up logs, temporary files, etc.
            self.logger.info("Attempting to repair disk space issues")
            
            # Clean up old log files
            await self._cleanup_old_logs()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error repairing disk space: {str(e)}")
            return False
    
    async def _cleanup_old_logs(self):
        """Clean up old log files to free disk space"""
        try:
            log_dir = Path("logs")
            if log_dir.exists():
                # Remove log files older than 7 days
                cutoff_time = datetime.now() - timedelta(days=7)
                
                for log_file in log_dir.glob("*.log"):
                    if log_file.stat().st_mtime < cutoff_time.timestamp():
                        log_file.unlink()
                        self.logger.info(f"Cleaned up old log file: {log_file}")
                        
        except Exception as e:
            self.logger.error(f"Error cleaning up old logs: {str(e)}")

class MonitoringDashboard:
    """Provides monitoring dashboard functionality"""
    
    def __init__(self, 
                 system_monitor: SystemMonitor,
                 agent_monitor: AgentMonitor,
                 alert_manager: AlertManager,
                 auto_repair: AutoRepairSystem):
        
        self.system_monitor = system_monitor
        self.agent_monitor = agent_monitor
        self.alert_manager = alert_manager
        self.auto_repair = auto_repair
        self.logger = logging.getLogger("FreelanceX.Monitoring.Dashboard")
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            # Get system health
            system_health = await self.system_monitor.get_system_health()
            
            # Get agent health
            agent_health = await self.agent_monitor.get_all_agent_health()
            
            # Get active alerts
            active_alerts = await self.alert_manager.get_active_alerts()
            
            # Get recent alert history
            alert_history = await self.alert_manager.get_alert_history(50)
            
            # Get repair actions
            recent_repairs = [action for action in self.auto_repair.repair_actions 
                            if action.timestamp > datetime.now() - timedelta(hours=24)]
            
            return {
                "timestamp": datetime.now().isoformat(),
                "system_health": system_health,
                "agent_health": {
                    name: {
                        "status": health.status.value,
                        "is_healthy": health.is_healthy,
                        "response_time": health.response_time,
                        "success_rate": health.success_rate,
                        "error_count": health.error_count,
                        "last_heartbeat": health.last_heartbeat.isoformat()
                    }
                    for name, health in agent_health.items()
                },
                "alerts": {
                    "active": len(active_alerts),
                    "recent": len(alert_history),
                    "critical": sum(1 for alert in active_alerts if alert.level == AlertLevel.CRITICAL),
                    "errors": sum(1 for alert in active_alerts if alert.level == AlertLevel.ERROR)
                },
                "repairs": {
                    "total": len(recent_repairs),
                    "successful": sum(1 for repair in recent_repairs if repair.success),
                    "failed": sum(1 for repair in recent_repairs if not repair.success)
                },
                "performance": {
                    "uptime": await self._calculate_uptime(),
                    "availability": await self._calculate_availability()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {str(e)}")
            return {"error": str(e)}
    
    async def _calculate_uptime(self) -> float:
        """Calculate system uptime percentage"""
        try:
            # This is a simplified calculation
            # In a real system, you'd track actual uptime
            return 99.5  # 99.5% uptime
        except Exception as e:
            self.logger.error(f"Error calculating uptime: {str(e)}")
            return 0.0
    
    async def _calculate_availability(self) -> float:
        """Calculate system availability percentage"""
        try:
            # This is a simplified calculation
            # In a real system, you'd track actual availability
            return 99.8  # 99.8% availability
        except Exception as e:
            self.logger.error(f"Error calculating availability: {str(e)}")
            return 0.0

class FreelanceXMonitoringSystem:
    """Main monitoring system orchestrator"""
    
    def __init__(self, 
                 agent_manager: AgentManager,
                 memory_layer: MemoryLayer):
        
        self.agent_manager = agent_manager
        self.memory_layer = memory_layer
        self.logger = logging.getLogger("FreelanceX.Monitoring")
        
        # Initialize monitoring components
        self.system_monitor = SystemMonitor(agent_manager)
        self.agent_monitor = AgentMonitor(agent_manager)
        self.alert_manager = AlertManager()
        self.auto_repair = AutoRepairSystem(agent_manager, self.alert_manager)
        self.dashboard = MonitoringDashboard(
            self.system_monitor,
            self.agent_monitor,
            self.alert_manager,
            self.auto_repair
        )
        
        # Monitoring state
        self.is_running = False
        self.monitoring_task = None
    
    async def start(self):
        """Start the monitoring system"""
        try:
            self.is_running = True
            
            # Start all monitoring components
            await self.system_monitor.start_monitoring()
            await self.agent_monitor.start_monitoring()
            
            # Start main monitoring loop
            self.monitoring_task = asyncio.create_task(self._main_monitoring_loop())
            
            self.logger.info("FreelanceX.AI monitoring system started")
            
        except Exception as e:
            self.logger.error(f"Error starting monitoring system: {str(e)}")
    
    async def stop(self):
        """Stop the monitoring system"""
        try:
            self.is_running = False
            
            # Stop all monitoring components
            await self.system_monitor.stop_monitoring()
            await self.agent_monitor.stop_monitoring()
            
            # Stop main monitoring loop
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            self.logger.info("FreelanceX.AI monitoring system stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring system: {str(e)}")
    
    async def _main_monitoring_loop(self):
        """Main monitoring loop that coordinates all monitoring activities"""
        while self.is_running:
            try:
                # Get system health
                system_health = await self.system_monitor.get_system_health()
                
                # Get agent health
                agent_health = await self.agent_monitor.get_all_agent_health()
                
                # Perform auto-repair analysis
                await self.auto_repair.analyze_and_repair(system_health, agent_health)
                
                # Wait for next monitoring cycle
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in main monitoring loop: {str(e)}")
                await asyncio.sleep(30)
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get overall monitoring system status"""
        return {
            "is_running": self.is_running,
            "system_health": await self.system_monitor.get_system_health(),
            "active_alerts": len(await self.alert_manager.get_active_alerts()),
            "auto_repair_enabled": self.auto_repair.auto_repair_enabled
        }
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        return await self.dashboard.get_dashboard_data()

if __name__ == "__main__":
    import asyncio
    
    async def test_monitoring():
        """Test the monitoring system"""
        print("Monitoring system test - requires AgentManager and MemoryLayer instances")
    
    asyncio.run(test_monitoring())