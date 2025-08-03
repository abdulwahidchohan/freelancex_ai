"""
FreelanceX.AI Control Panel
System monitoring, health checks, and management tools
"""

import asyncio
import logging
import psutil
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class ControlPanel:
    """
    Control panel for FreelanceX.AI system monitoring and management
    Provides health checks, performance monitoring, and system controls
    """
    
    def __init__(self):
        self.agent_manager = None
        self.memory_manager = None
        self.config = None
        self.health_history = []
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time': 30.0,
            'error_rate': 0.1
        }
        self.is_monitoring = False
        
    async def initialize(self):
        """Initialize the control panel"""
        try:
            logger.info("🚀 Initializing Control Panel...")
            self.is_monitoring = True
            
            # Start background monitoring
            asyncio.create_task(self._background_monitoring())
            
            logger.info("✅ Control Panel initialized")
            
        except Exception as e:
            logger.error(f"❌ Control Panel initialization failed: {str(e)}")
            raise
    
    def set_dependencies(self, agent_manager, memory_manager, config):
        """Set system dependencies"""
        self.agent_manager = agent_manager
        self.memory_manager = memory_manager
        self.config = config
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        try:
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'healthy',
                'system_metrics': await self._get_system_metrics(),
                'agent_status': await self._get_agent_status(),
                'memory_status': await self._get_memory_status(),
                'performance_metrics': await self._get_performance_metrics(),
                'alerts': []
            }
            
            # Check for issues and generate alerts
            alerts = await self._check_alerts(health_status)
            health_status['alerts'] = alerts
            
            # Update overall status based on alerts
            if any(alert['severity'] == 'critical' for alert in alerts):
                health_status['overall_status'] = 'critical'
            elif any(alert['severity'] == 'warning' for alert in alerts):
                health_status['overall_status'] = 'degraded'
            
            # Store health history
            self.health_history.append(health_status)
            if len(self.health_history) > 100:  # Keep last 100 health checks
                self.health_history = self.health_history[-100:]
            
            logger.info(f"🏥 Health check completed: {health_status['overall_status']}")
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {str(e)}")
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'error',
                'error': str(e)
            }
    
    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available': memory.available / (1024**3),  # GB
                'disk_usage': disk.percent,
                'disk_free': disk.free / (1024**3),  # GB
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get system metrics: {str(e)}")
            return {}
    
    async def _get_agent_status(self) -> Dict[str, Any]:
        """Get agent system status"""
        if not self.agent_manager:
            return {}
        
        try:
            agent_statuses = await self.agent_manager.get_all_status()
            health_status = await self.agent_manager.health_check()
            
            return {
                'total_agents': len(agent_statuses),
                'active_agents': sum(1 for status in agent_statuses.values() if status.status == 'idle'),
                'busy_agents': sum(1 for status in agent_statuses.values() if status.status == 'busy'),
                'error_agents': sum(1 for status in agent_statuses.values() if status.status == 'error'),
                'disabled_agents': sum(1 for status in agent_statuses.values() if status.status == 'disabled'),
                'agent_details': agent_statuses,
                'health_status': health_status
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get agent status: {str(e)}")
            return {}
    
    async def _get_memory_status(self) -> Dict[str, Any]:
        """Get memory system status"""
        if not self.memory_manager:
            return {}
        
        try:
            # Get database size
            db_path = Path(self.memory_manager.db_path)
            db_size = db_path.stat().st_size / (1024**2) if db_path.exists() else 0  # MB
            
            # Get recent activity
            recent_interactions = await self.memory_manager.get_recent_interactions('default', limit=5)
            
            return {
                'database_size_mb': db_size,
                'recent_activity_count': len(recent_interactions),
                'last_activity': recent_interactions[0]['timestamp'] if recent_interactions else None
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get memory status: {str(e)}")
            return {}
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            # Get task statistics from dispatcher if available
            if hasattr(self.agent_manager, 'dispatcher'):
                task_stats = await self.agent_manager.dispatcher.get_task_statistics()
            else:
                task_stats = {}
            
            # Calculate response time trends
            recent_health_checks = self.health_history[-10:] if self.health_history else []
            avg_response_time = 0
            if recent_health_checks:
                response_times = [check.get('performance_metrics', {}).get('avg_response_time', 0) 
                                for check in recent_health_checks]
                avg_response_time = sum(response_times) / len(response_times)
            
            return {
                'task_statistics': task_stats,
                'avg_response_time': avg_response_time,
                'uptime_hours': self._get_uptime_hours()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get performance metrics: {str(e)}")
            return {}
    
    def _get_uptime_hours(self) -> float:
        """Get system uptime in hours"""
        try:
            uptime_seconds = psutil.boot_time()
            uptime_hours = (datetime.now().timestamp() - uptime_seconds) / 3600
            return round(uptime_hours, 2)
        except:
            return 0.0
    
    async def _check_alerts(self, health_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for system alerts based on thresholds"""
        alerts = []
        
        # System resource alerts
        system_metrics = health_status.get('system_metrics', {})
        
        if system_metrics.get('cpu_usage', 0) > self.alert_thresholds['cpu_usage']:
            alerts.append({
                'type': 'high_cpu_usage',
                'severity': 'warning',
                'message': f"CPU usage is high: {system_metrics['cpu_usage']:.1f}%",
                'value': system_metrics['cpu_usage']
            })
        
        if system_metrics.get('memory_usage', 0) > self.alert_thresholds['memory_usage']:
            alerts.append({
                'type': 'high_memory_usage',
                'severity': 'warning',
                'message': f"Memory usage is high: {system_metrics['memory_usage']:.1f}%",
                'value': system_metrics['memory_usage']
            })
        
        if system_metrics.get('disk_usage', 0) > self.alert_thresholds['disk_usage']:
            alerts.append({
                'type': 'high_disk_usage',
                'severity': 'critical',
                'message': f"Disk usage is critical: {system_metrics['disk_usage']:.1f}%",
                'value': system_metrics['disk_usage']
            })
        
        # Agent alerts
        agent_status = health_status.get('agent_status', {})
        if agent_status.get('error_agents', 0) > 0:
            alerts.append({
                'type': 'agent_errors',
                'severity': 'warning',
                'message': f"{agent_status['error_agents']} agents are in error state",
                'value': agent_status['error_agents']
            })
        
        # Performance alerts
        performance_metrics = health_status.get('performance_metrics', {})
        avg_response_time = performance_metrics.get('avg_response_time', 0)
        
        if avg_response_time > self.alert_thresholds['response_time']:
            alerts.append({
                'type': 'slow_response_time',
                'severity': 'warning',
                'message': f"Average response time is slow: {avg_response_time:.2f}s",
                'value': avg_response_time
            })
        
        return alerts
    
    async def _background_monitoring(self):
        """Background monitoring task"""
        while self.is_monitoring:
            try:
                # Perform health check every 5 minutes
                await self.health_check()
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Background monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status summary"""
        try:
            health_status = await self.health_check()
            
            return {
                'status': health_status['overall_status'],
                'timestamp': health_status['timestamp'],
                'alerts_count': len(health_status['alerts']),
                'system_metrics': health_status['system_metrics'],
                'agent_summary': {
                    'total': health_status['agent_status'].get('total_agents', 0),
                    'active': health_status['agent_status'].get('active_agents', 0),
                    'errors': health_status['agent_status'].get('error_agents', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get system status: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def restart_agent(self, agent_id: str) -> bool:
        """Restart a specific agent"""
        if not self.agent_manager:
            return False
        
        try:
            # Disable agent
            await self.agent_manager.disable_agent(agent_id)
            
            # Wait a moment
            await asyncio.sleep(2)
            
            # Re-enable agent
            success = await self.agent_manager.enable_agent(agent_id)
            
            if success:
                logger.info(f"🔄 Restarted agent: {agent_id}")
            else:
                logger.error(f"❌ Failed to restart agent: {agent_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Agent restart failed: {str(e)}")
            return False
    
    async def restart_all_agents(self) -> Dict[str, bool]:
        """Restart all agents"""
        if not self.agent_manager:
            return {}
        
        try:
            results = {}
            agent_statuses = await self.agent_manager.get_all_status()
            
            for agent_id in agent_statuses.keys():
                results[agent_id] = await self.restart_agent(agent_id)
            
            logger.info("🔄 Restart all agents completed")
            return results
            
        except Exception as e:
            logger.error(f"❌ Restart all agents failed: {str(e)}")
            return {}
    
    async def get_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance report for the last N hours"""
        try:
            since_time = datetime.now() - timedelta(hours=hours)
            
            # Filter health history
            relevant_checks = [
                check for check in self.health_history
                if datetime.fromisoformat(check['timestamp']) > since_time
            ]
            
            if not relevant_checks:
                return {'message': 'No data available for the specified time period'}
            
            # Calculate averages
            cpu_usage = [check['system_metrics'].get('cpu_usage', 0) for check in relevant_checks]
            memory_usage = [check['system_metrics'].get('memory_usage', 0) for check in relevant_checks]
            response_times = [check['performance_metrics'].get('avg_response_time', 0) for check in relevant_checks]
            
            report = {
                'period_hours': hours,
                'checks_count': len(relevant_checks),
                'avg_cpu_usage': sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0,
                'avg_memory_usage': sum(memory_usage) / len(memory_usage) if memory_usage else 0,
                'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
                'total_alerts': sum(len(check.get('alerts', [])) for check in relevant_checks),
                'status_distribution': self._get_status_distribution(relevant_checks)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate performance report: {str(e)}")
            return {'error': str(e)}
    
    def _get_status_distribution(self, health_checks: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of system statuses"""
        distribution = {'healthy': 0, 'degraded': 0, 'critical': 0, 'error': 0}
        
        for check in health_checks:
            status = check.get('overall_status', 'unknown')
            if status in distribution:
                distribution[status] += 1
        
        return distribution
    
    async def update_alert_thresholds(self, new_thresholds: Dict[str, float]):
        """Update alert thresholds"""
        try:
            self.alert_thresholds.update(new_thresholds)
            logger.info(f"⚙️ Updated alert thresholds: {new_thresholds}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update alert thresholds: {str(e)}")
            return False
    
    async def shutdown(self):
        """Shutdown the control panel"""
        try:
            self.is_monitoring = False
            logger.info("🛑 Control Panel shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Control Panel shutdown error: {str(e)}") 