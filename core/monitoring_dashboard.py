#!/usr/bin/env python3
"""
FreelanceX.AI Monitoring Dashboard
System health monitoring, agent performance tracking, and user interaction analytics
"""

import asyncio
import logging
import json
import time
import psutil
import sqlite3
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import aiosqlite
from enum import Enum
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64

class MetricType(Enum):
    """Types of metrics tracked by the monitoring system"""
    PERFORMANCE = "performance"
    HEALTH = "health"
    USAGE = "usage"
    ERROR = "error"
    SECURITY = "security"

@dataclass
class SystemMetric:
    """System metric data structure"""
    metric_id: str
    metric_type: MetricType
    name: str
    value: Union[float, int, str]
    unit: str
    timestamp: datetime
    tags: Dict[str, str]
    description: str

@dataclass
class AgentPerformance:
    """Agent performance metrics"""
    agent_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    last_activity: datetime
    status: str
    error_count: int
    uptime: float

@dataclass
class UserInteraction:
    """User interaction analytics"""
    user_id: str
    session_id: str
    interaction_count: int
    total_duration: float
    average_session_length: float
    most_used_agent: str
    last_activity: datetime
    satisfaction_score: Optional[float]

class MonitoringDashboard:
    """
    Comprehensive monitoring dashboard for FreelanceX.AI
    Tracks system health, agent performance, and user interactions
    """
    
    def __init__(self, db_path: str = "data/freelancex_monitoring.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("FreelanceX.MonitoringDashboard")
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        asyncio.create_task(self._initialize_database())
        
        # Metric collection
        self.metrics_buffer: List[SystemMetric] = []
        self.metrics_flush_interval = 60  # seconds
        self.last_flush = time.time()
        
        # Performance tracking
        self.agent_performance: Dict[str, AgentPerformance] = {}
        self.user_interactions: Dict[str, UserInteraction] = {}
        
        # System health monitoring
        self.health_checks = {
            'cpu_usage': self._check_cpu_usage,
            'memory_usage': self._check_memory_usage,
            'disk_usage': self._check_disk_usage,
            'network_status': self._check_network_status,
            'database_health': self._check_database_health
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'error_rate': 5.0,
            'response_time': 5.0
        }
        
        # Start monitoring tasks
        asyncio.create_task(self._start_monitoring_loop())
        asyncio.create_task(self._start_metrics_flush_loop())
        
        self.logger.info("Monitoring Dashboard initialized")
    
    async def _initialize_database(self):
        """Initialize monitoring database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # System metrics table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    metric_id TEXT PRIMARY KEY,
                    metric_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    value REAL,
                    unit TEXT,
                    timestamp TEXT NOT NULL,
                    tags TEXT,
                    description TEXT
                )
            """)
            
            # Agent performance table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS agent_performance (
                    agent_name TEXT PRIMARY KEY,
                    total_requests INTEGER DEFAULT 0,
                    successful_requests INTEGER DEFAULT 0,
                    failed_requests INTEGER DEFAULT 0,
                    average_response_time REAL DEFAULT 0.0,
                    last_activity TEXT,
                    status TEXT DEFAULT 'unknown',
                    error_count INTEGER DEFAULT 0,
                    uptime REAL DEFAULT 0.0,
                    last_updated TEXT
                )
            """)
            
            # User interactions table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_interactions (
                    user_id TEXT,
                    session_id TEXT,
                    interaction_count INTEGER DEFAULT 0,
                    total_duration REAL DEFAULT 0.0,
                    average_session_length REAL DEFAULT 0.0,
                    most_used_agent TEXT,
                    last_activity TEXT,
                    satisfaction_score REAL,
                    PRIMARY KEY (user_id, session_id)
                )
            """)
            
            # System alerts table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS system_alerts (
                    alert_id TEXT PRIMARY KEY,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT 0,
                    resolved_at TEXT
                )
            """)
            
            # Performance history table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS performance_history (
                    record_id TEXT PRIMARY KEY,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_name TEXT,
                    user_id TEXT
                )
            """)
            
            await db.commit()
            self.logger.info("Monitoring database tables initialized")
    
    async def _start_monitoring_loop(self):
        """Start the main monitoring loop"""
        while True:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Perform health checks
                await self._perform_health_checks()
                
                # Update agent performance
                await self._update_agent_performance()
                
                # Check for alerts
                await self._check_alerts()
                
                # Wait for next cycle
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _start_metrics_flush_loop(self):
        """Periodically flush metrics to database"""
        while True:
            try:
                await asyncio.sleep(self.metrics_flush_interval)
                await self._flush_metrics()
            except Exception as e:
                self.logger.error(f"Metrics flush error: {str(e)}")
    
    async def _collect_system_metrics(self):
        """Collect current system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            await self.record_metric(
                MetricType.PERFORMANCE,
                "cpu_usage",
                cpu_percent,
                "percentage",
                {"component": "system"}
            )
            
            # Memory usage
            memory = psutil.virtual_memory()
            await self.record_metric(
                MetricType.PERFORMANCE,
                "memory_usage",
                memory.percent,
                "percentage",
                {"component": "system"}
            )
            
            # Disk usage
            disk = psutil.disk_usage('/')
            await self.record_metric(
                MetricType.PERFORMANCE,
                "disk_usage",
                (disk.used / disk.total) * 100,
                "percentage",
                {"component": "system"}
            )
            
            # Network I/O
            network = psutil.net_io_counters()
            await self.record_metric(
                MetricType.PERFORMANCE,
                "network_bytes_sent",
                network.bytes_sent,
                "bytes",
                {"component": "network"}
            )
            await self.record_metric(
                MetricType.PERFORMANCE,
                "network_bytes_recv",
                network.bytes_recv,
                "bytes",
                {"component": "network"}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {str(e)}")
    
    async def _perform_health_checks(self):
        """Perform system health checks"""
        for check_name, check_func in self.health_checks.items():
            try:
                result = await check_func()
                await self.record_metric(
                    MetricType.HEALTH,
                    f"health_check_{check_name}",
                    1.0 if result else 0.0,
                    "boolean",
                    {"component": "health_check"}
                )
            except Exception as e:
                self.logger.error(f"Health check {check_name} failed: {str(e)}")
                await self.record_metric(
                    MetricType.HEALTH,
                    f"health_check_{check_name}",
                    0.0,
                    "boolean",
                    {"component": "health_check", "error": str(e)}
                )
    
    async def _check_cpu_usage(self) -> bool:
        """Check CPU usage health"""
        cpu_percent = psutil.cpu_percent(interval=1)
        return cpu_percent < self.alert_thresholds['cpu_usage']
    
    async def _check_memory_usage(self) -> bool:
        """Check memory usage health"""
        memory = psutil.virtual_memory()
        return memory.percent < self.alert_thresholds['memory_usage']
    
    async def _check_disk_usage(self) -> bool:
        """Check disk usage health"""
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        return disk_percent < self.alert_thresholds['disk_usage']
    
    async def _check_network_status(self) -> bool:
        """Check network connectivity"""
        try:
            # Simple ping test
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except:
            return False
    
    async def _check_database_health(self) -> bool:
        """Check database connectivity and health"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("SELECT 1")
                return True
        except:
            return False
    
    async def record_metric(self, metric_type: MetricType, name: str, value: Union[float, int, str], 
                          unit: str, tags: Dict[str, str] = None, description: str = ""):
        """Record a system metric"""
        metric = SystemMetric(
            metric_id=f"{name}_{int(time.time())}",
            metric_type=metric_type,
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            tags=tags or {},
            description=description
        )
        
        self.metrics_buffer.append(metric)
        
        # Flush if buffer is full
        if len(self.metrics_buffer) >= 100:
            await self._flush_metrics()
    
    async def _flush_metrics(self):
        """Flush metrics buffer to database"""
        if not self.metrics_buffer:
            return
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                for metric in self.metrics_buffer:
                    await db.execute("""
                        INSERT INTO system_metrics 
                        (metric_id, metric_type, name, value, unit, timestamp, tags, description)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        metric.metric_id,
                        metric.metric_type.value,
                        metric.name,
                        metric.value,
                        metric.unit,
                        metric.timestamp.isoformat(),
                        json.dumps(metric.tags),
                        metric.description
                    ))
                
                await db.commit()
                self.logger.info(f"Flushed {len(self.metrics_buffer)} metrics to database")
                self.metrics_buffer.clear()
                
        except Exception as e:
            self.logger.error(f"Failed to flush metrics: {str(e)}")
    
    async def update_agent_performance(self, agent_name: str, performance_data: Dict[str, Any]):
        """Update agent performance metrics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO agent_performance 
                    (agent_name, total_requests, successful_requests, failed_requests,
                     average_response_time, last_activity, status, error_count, uptime, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    agent_name,
                    performance_data.get('total_requests', 0),
                    performance_data.get('successful_requests', 0),
                    performance_data.get('failed_requests', 0),
                    performance_data.get('average_response_time', 0.0),
                    performance_data.get('last_activity', datetime.now().isoformat()),
                    performance_data.get('status', 'unknown'),
                    performance_data.get('error_count', 0),
                    performance_data.get('uptime', 0.0),
                    datetime.now().isoformat()
                ))
                
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to update agent performance: {str(e)}")
    
    async def record_user_interaction(self, user_id: str, session_id: str, interaction_data: Dict[str, Any]):
        """Record user interaction data"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO user_interactions 
                    (user_id, session_id, interaction_count, total_duration, average_session_length,
                     most_used_agent, last_activity, satisfaction_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    session_id,
                    interaction_data.get('interaction_count', 0),
                    interaction_data.get('total_duration', 0.0),
                    interaction_data.get('average_session_length', 0.0),
                    interaction_data.get('most_used_agent', ''),
                    interaction_data.get('last_activity', datetime.now().isoformat()),
                    interaction_data.get('satisfaction_score')
                ))
                
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to record user interaction: {str(e)}")
    
    async def _update_agent_performance(self):
        """Update agent performance from current state"""
        for agent_name, performance in self.agent_performance.items():
            await self.update_agent_performance(agent_name, asdict(performance))
    
    async def _check_alerts(self):
        """Check for system alerts based on thresholds"""
        try:
            # Get recent metrics
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT name, value FROM system_metrics 
                    WHERE timestamp > ? AND metric_type = 'performance'
                """, ((datetime.now() - timedelta(minutes=5)).isoformat(),)) as cursor:
                    recent_metrics = await cursor.fetchall()
            
            # Check thresholds
            for metric_name, value in recent_metrics:
                if metric_name in self.alert_thresholds:
                    threshold = self.alert_thresholds[metric_name]
                    if value > threshold:
                        await self._create_alert(
                            "threshold_exceeded",
                            "warning",
                            f"{metric_name} exceeded threshold: {value} > {threshold}"
                        )
                        
        except Exception as e:
            self.logger.error(f"Alert check failed: {str(e)}")
    
    async def _create_alert(self, alert_type: str, severity: str, message: str):
        """Create a system alert"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                alert_id = f"alert_{int(time.time())}"
                await db.execute("""
                    INSERT INTO system_alerts 
                    (alert_id, alert_type, severity, message, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    alert_id,
                    alert_type,
                    severity,
                    message,
                    datetime.now().isoformat()
                ))
                
                await db.commit()
                self.logger.warning(f"Alert created: {message}")
                
        except Exception as e:
            self.logger.error(f"Failed to create alert: {str(e)}")
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            # System health summary
            health_summary = await self._get_health_summary()
            
            # Agent performance summary
            agent_summary = await self._get_agent_summary()
            
            # User interaction summary
            user_summary = await self._get_user_summary()
            
            # Recent alerts
            recent_alerts = await self._get_recent_alerts()
            
            # Performance trends
            performance_trends = await self._get_performance_trends()
            
            return {
                'health_summary': health_summary,
                'agent_summary': agent_summary,
                'user_summary': user_summary,
                'recent_alerts': recent_alerts,
                'performance_trends': performance_trends,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get dashboard data: {str(e)}")
            return {}
    
    async def _get_health_summary(self) -> Dict[str, Any]:
        """Get system health summary"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get latest metrics
                async with db.execute("""
                    SELECT name, value FROM system_metrics 
                    WHERE metric_type = 'performance' 
                    AND timestamp > ?
                    ORDER BY timestamp DESC
                """, ((datetime.now() - timedelta(minutes=5)).isoformat(),)) as cursor:
                    metrics = await cursor.fetchall()
                
                health_data = {}
                for name, value in metrics:
                    if name not in health_data:
                        health_data[name] = value
                
                return {
                    'cpu_usage': health_data.get('cpu_usage', 0),
                    'memory_usage': health_data.get('memory_usage', 0),
                    'disk_usage': health_data.get('disk_usage', 0),
                    'network_status': health_data.get('network_bytes_sent', 0) > 0
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get health summary: {str(e)}")
            return {}
    
    async def _get_agent_summary(self) -> List[Dict[str, Any]]:
        """Get agent performance summary"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT * FROM agent_performance") as cursor:
                    rows = await cursor.fetchall()
                
                agents = []
                for row in rows:
                    agent_data = {
                        'agent_name': row[0],
                        'total_requests': row[1],
                        'successful_requests': row[2],
                        'failed_requests': row[3],
                        'average_response_time': row[4],
                        'last_activity': row[5],
                        'status': row[6],
                        'error_count': row[7],
                        'uptime': row[8]
                    }
                    agents.append(agent_data)
                
                return agents
                
        except Exception as e:
            self.logger.error(f"Failed to get agent summary: {str(e)}")
            return []
    
    async def _get_user_summary(self) -> Dict[str, Any]:
        """Get user interaction summary"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Total users
                async with db.execute("SELECT COUNT(DISTINCT user_id) FROM user_interactions") as cursor:
                    total_users = (await cursor.fetchone())[0]
                
                # Active sessions
                async with db.execute("""
                    SELECT COUNT(*) FROM user_interactions 
                    WHERE last_activity > ?
                """, ((datetime.now() - timedelta(hours=1)).isoformat(),)) as cursor:
                    active_sessions = (await cursor.fetchone())[0]
                
                # Average satisfaction
                async with db.execute("""
                    SELECT AVG(satisfaction_score) FROM user_interactions 
                    WHERE satisfaction_score IS NOT NULL
                """) as cursor:
                    avg_satisfaction = (await cursor.fetchone())[0] or 0.0
                
                return {
                    'total_users': total_users,
                    'active_sessions': active_sessions,
                    'average_satisfaction': avg_satisfaction
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get user summary: {str(e)}")
            return {}
    
    async def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent system alerts"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT * FROM system_alerts 
                    WHERE timestamp > ? 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                """, ((datetime.now() - timedelta(hours=24)).isoformat(),)) as cursor:
                    rows = await cursor.fetchall()
                
                alerts = []
                for row in rows:
                    alert_data = {
                        'alert_id': row[0],
                        'alert_type': row[1],
                        'severity': row[2],
                        'message': row[3],
                        'timestamp': row[4],
                        'resolved': bool(row[5])
                    }
                    alerts.append(alert_data)
                
                return alerts
                
        except Exception as e:
            self.logger.error(f"Failed to get recent alerts: {str(e)}")
            return []
    
    async def _get_performance_trends(self) -> Dict[str, List[float]]:
        """Get performance trends for the last 24 hours"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get hourly averages for key metrics
                metrics = ['cpu_usage', 'memory_usage', 'disk_usage']
                trends = {}
                
                for metric in metrics:
                    async with db.execute("""
                        SELECT AVG(value) FROM system_metrics 
                        WHERE name = ? AND timestamp > ?
                        GROUP BY strftime('%H', timestamp)
                        ORDER BY strftime('%H', timestamp)
                    """, (metric, (datetime.now() - timedelta(hours=24)).isoformat())) as cursor:
                        values = await cursor.fetchall()
                        trends[metric] = [row[0] for row in values]
                
                return trends
                
        except Exception as e:
            self.logger.error(f"Failed to get performance trends: {str(e)}")
            return {}
    
    async def generate_performance_chart(self, metric_name: str, hours: int = 24) -> str:
        """Generate a performance chart as base64 image"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT timestamp, value FROM system_metrics 
                    WHERE name = ? AND timestamp > ?
                    ORDER BY timestamp
                """, (metric_name, (datetime.now() - timedelta(hours=hours)).isoformat())) as cursor:
                    data = await cursor.fetchall()
            
            if not data:
                return ""
            
            # Parse data
            timestamps = [datetime.fromisoformat(row[0]) for row in data]
            values = [row[1] for row in data]
            
            # Create chart
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, values)
            plt.title(f'{metric_name.replace("_", " ").title()} - Last {hours} Hours')
            plt.xlabel('Time')
            plt.ylabel('Value')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convert to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance chart: {str(e)}")
            return ""
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        dashboard_data = await self.get_dashboard_data()
        
        # Determine overall status
        health_summary = dashboard_data.get('health_summary', {})
        cpu_ok = health_summary.get('cpu_usage', 0) < self.alert_thresholds['cpu_usage']
        memory_ok = health_summary.get('memory_usage', 0) < self.alert_thresholds['memory_usage']
        disk_ok = health_summary.get('disk_usage', 0) < self.alert_thresholds['disk_usage']
        
        if cpu_ok and memory_ok and disk_ok:
            overall_status = "healthy"
        elif any([cpu_ok, memory_ok, disk_ok]):
            overall_status = "degraded"
        else:
            overall_status = "critical"
        
        return {
            'status': overall_status,
            'timestamp': datetime.now().isoformat(),
            'metrics': dashboard_data
        }