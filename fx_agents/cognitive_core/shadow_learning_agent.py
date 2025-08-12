"""FreelanceX.AI Shadow Learning Agent
Observes & improves without user asking
"""

from agents import Agent, function_tool as _function_tool
from functools import partial
tool = partial(_function_tool, strict_mode=False)
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LearningInsight(BaseModel):
    pattern: str = Field(..., description="Identified pattern or issue")
    suggestion: str = Field(..., description="Suggested improvement")
    expected_impact: str = Field(..., description="Expected impact of the improvement")
    confidence: float = Field(..., description="Confidence in the insight (0-1)")
    priority: str = Field(..., description="Priority level (low, medium, high, critical)")


class PerformanceMetric(BaseModel):
    metric_name: str = Field(..., description="Name of the performance metric")
    current_value: float = Field(..., description="Current metric value")
    target_value: float = Field(..., description="Target metric value")
    trend: str = Field(..., description="Trend direction (improving, declining, stable)")
    recommendation: str = Field(..., description="Recommendation for improvement")


class SystemOptimization(BaseModel):
    area: str = Field(..., description="Area of optimization")
    current_state: str = Field(..., description="Current system state")
    optimization_suggestions: List[str] = Field(..., description="Optimization suggestions")
    expected_benefits: List[str] = Field(..., description="Expected benefits")
    implementation_effort: str = Field(..., description="Implementation effort level")


@tool
def analyze_logs(log_lines: List[str], time_range: Optional[str] = None) -> List[LearningInsight]:
    """
    Analyze system logs to identify patterns and suggest improvements.
    
    Args:
        log_lines: List of log lines to analyze
        time_range: Optional time range for analysis
        
    Returns:
        List of LearningInsight with identified patterns and suggestions
    """
    try:
        logger.info("Analyzing system logs for patterns")
        
        insights = []
        log_text = " ".join(log_lines).lower()
        
        # Pattern detection with dynamic analysis
        patterns = {
            "timeout": {
                "keywords": ["timeout", "timed out", "connection timeout", "request timeout"],
                "suggestion": "Implement connection pooling, increase timeout values, or add retry logic",
                "impact": "Reduced request failures and improved user experience",
                "priority": "high"
            },
            "rate_limit": {
                "keywords": ["rate limit", "rate limited", "429", "too many requests"],
                "suggestion": "Implement exponential backoff, request batching, and rate limit monitoring",
                "impact": "Higher API reliability and better resource utilization",
                "priority": "high"
            },
            "error_500": {
                "keywords": ["500", "internal server error", "server error"],
                "suggestion": "Add error handling, implement circuit breakers, and improve error logging",
                "impact": "Reduced system failures and better error tracking",
                "priority": "critical"
            },
            "memory_usage": {
                "keywords": ["memory", "out of memory", "memory leak", "high memory usage"],
                "suggestion": "Implement memory monitoring, optimize data structures, and add garbage collection",
                "impact": "Improved system stability and performance",
                "priority": "high"
            },
            "slow_queries": {
                "keywords": ["slow query", "query timeout", "database slow", "long query"],
                "suggestion": "Optimize database queries, add indexes, and implement query caching",
                "impact": "Faster response times and better user experience",
                "priority": "medium"
            },
            "authentication_failures": {
                "keywords": ["auth failed", "authentication error", "invalid token", "unauthorized"],
                "suggestion": "Improve authentication flow, add token refresh logic, and enhance security logging",
                "impact": "Better security and reduced authentication issues",
                "priority": "high"
            }
        }
        
        # Analyze each pattern
        for pattern_name, pattern_info in patterns.items():
            if any(keyword in log_text for keyword in pattern_info["keywords"]):
                # Calculate confidence based on frequency
                frequency = sum(1 for keyword in pattern_info["keywords"] if keyword in log_text)
                confidence = min(1.0, frequency / len(pattern_info["keywords"]))
                
                insights.append(LearningInsight(
                    pattern=pattern_name,
                    suggestion=pattern_info["suggestion"],
                    expected_impact=pattern_info["impact"],
                    confidence=confidence,
                    priority=pattern_info["priority"]
                ))
        
        # Dynamic pattern detection for custom issues
        if "error" in log_text and len([line for line in log_lines if "error" in line.lower()]) > 5:
            insights.append(LearningInsight(
                pattern="high_error_rate",
                suggestion="Implement comprehensive error handling and monitoring",
                expected_impact="Reduced system failures and better error tracking",
                confidence=0.8,
                priority="high"
            ))
        
        if "warning" in log_text and len([line for line in log_lines if "warning" in line.lower()]) > 10:
            insights.append(LearningInsight(
                pattern="warning_accumulation",
                suggestion="Address warning conditions and improve logging levels",
                expected_impact="Cleaner logs and better system health monitoring",
                confidence=0.7,
                priority="medium"
            ))
        
        # Sort by priority and confidence
        insights.sort(key=lambda x: (x.priority == "critical", x.priority == "high", x.confidence), reverse=True)
        
        return insights
        
    except Exception as e:
        logger.error(f"Error analyzing logs: {e}")
        return [LearningInsight(
            pattern="analysis_error",
            suggestion="Review log format and analysis process",
            expected_impact="Improved log analysis capabilities",
            confidence=0.0,
            priority="low"
        )]


@tool
def analyze_performance_metrics(metrics_data: Dict[str, Any]) -> List[PerformanceMetric]:
    """
    Analyze performance metrics and provide optimization recommendations.
    
    Args:
        metrics_data: Dictionary containing performance metrics
        
    Returns:
        List of PerformanceMetric with analysis and recommendations
    """
    try:
        logger.info("Analyzing performance metrics")
        
        performance_metrics = []
        
        # Define target values and thresholds
        targets = {
            "response_time": {"target": 200.0, "unit": "ms"},
            "throughput": {"target": 1000.0, "unit": "requests/sec"},
            "error_rate": {"target": 0.01, "unit": "%"},
            "cpu_usage": {"target": 70.0, "unit": "%"},
            "memory_usage": {"target": 80.0, "unit": "%"},
            "database_connections": {"target": 50.0, "unit": "connections"}
        }
        
        for metric_name, current_value in metrics_data.items():
            if metric_name in targets:
                target_info = targets[metric_name]
                target_value = target_info["target"]
                
                # Determine trend (simplified - in real implementation, you'd have historical data)
                trend = "stable"
                if current_value > target_value * 1.2:
                    trend = "declining"
                elif current_value < target_value * 0.8:
                    trend = "improving"
                
                # Generate recommendations based on metric type
                recommendation = ""
                if metric_name == "response_time" and current_value > target_value:
                    recommendation = "Optimize database queries, implement caching, or scale horizontally"
                elif metric_name == "error_rate" and current_value > target_value:
                    recommendation = "Improve error handling, add monitoring, and implement circuit breakers"
                elif metric_name == "cpu_usage" and current_value > target_value:
                    recommendation = "Optimize algorithms, implement caching, or scale compute resources"
                elif metric_name == "memory_usage" and current_value > target_value:
                    recommendation = "Implement memory monitoring, optimize data structures, or scale memory"
                else:
                    recommendation = "Monitor and maintain current performance levels"
                
                performance_metrics.append(PerformanceMetric(
                    metric_name=metric_name,
                    current_value=current_value,
                    target_value=target_value,
                    trend=trend,
                    recommendation=recommendation
                ))
        
        return performance_metrics
        
    except Exception as e:
        logger.error(f"Error analyzing performance metrics: {e}")
        return [PerformanceMetric(
            metric_name="analysis_error",
            current_value=0.0,
            target_value=0.0,
            trend="unknown",
            recommendation="Review metrics data format and analysis process"
        )]


@tool
def suggest_system_optimizations(system_state: Dict[str, Any]) -> List[SystemOptimization]:
    """
    Suggest system optimizations based on current system state.
    
    Args:
        system_state: Current system state and configuration
        
    Returns:
        List of SystemOptimization with detailed suggestions
    """
    try:
        logger.info("Suggesting system optimizations")
        
        optimizations = []
        
        # Analyze different system areas
        areas = {
            "database": {
                "indicators": ["slow_queries", "high_connections", "index_missing"],
                "suggestions": [
                    "Implement database connection pooling",
                    "Add missing indexes for frequently queried columns",
                    "Optimize slow queries with query analysis",
                    "Implement read replicas for read-heavy workloads"
                ],
                "benefits": [
                    "Improved query performance",
                    "Reduced database load",
                    "Better scalability",
                    "Faster response times"
                ]
            },
            "caching": {
                "indicators": ["cache_misses", "repeated_queries", "slow_responses"],
                "suggestions": [
                    "Implement Redis caching for frequently accessed data",
                    "Add application-level caching",
                    "Implement CDN for static content",
                    "Use cache warming strategies"
                ],
                "benefits": [
                    "Reduced database load",
                    "Faster response times",
                    "Better user experience",
                    "Lower infrastructure costs"
                ]
            },
            "api_optimization": {
                "indicators": ["rate_limits", "timeouts", "high_latency"],
                "suggestions": [
                    "Implement API rate limiting and throttling",
                    "Add request/response compression",
                    "Implement API versioning",
                    "Add comprehensive API monitoring"
                ],
                "benefits": [
                    "Better API reliability",
                    "Improved performance",
                    "Enhanced security",
                    "Better monitoring and debugging"
                ]
            },
            "security": {
                "indicators": ["auth_failures", "security_warnings", "vulnerability_alerts"],
                "suggestions": [
                    "Implement comprehensive authentication and authorization",
                    "Add security headers and HTTPS enforcement",
                    "Implement rate limiting for security",
                    "Add security monitoring and alerting"
                ],
                "benefits": [
                    "Enhanced security posture",
                    "Reduced security risks",
                    "Compliance with security standards",
                    "Better incident response"
                ]
            }
        }
        
        # Analyze each area based on system state
        for area_name, area_info in areas.items():
            # Check if area needs optimization based on indicators
            needs_optimization = any(
                indicator in system_state.get("issues", [])
                for indicator in area_info["indicators"]
            )
            
            if needs_optimization:
                # Determine implementation effort based on complexity
                effort = "medium"
                if area_name in ["database", "security"]:
                    effort = "high"
                elif area_name == "caching":
                    effort = "low"
                
                optimizations.append(SystemOptimization(
                    area=area_name,
                    current_state=f"Requires optimization - {', '.join(area_info['indicators'])} detected",
                    optimization_suggestions=area_info["suggestions"],
                    expected_benefits=area_info["benefits"],
                    implementation_effort=effort
                ))
        
        # Add general optimization if no specific areas identified
        if not optimizations:
            optimizations.append(SystemOptimization(
                area="general",
                current_state="System performing well, monitoring recommended",
                optimization_suggestions=[
                    "Implement comprehensive monitoring",
                    "Add performance benchmarking",
                    "Regular security audits",
                    "Capacity planning and scaling preparation"
                ],
                expected_benefits=[
                    "Proactive issue detection",
                    "Better performance tracking",
                    "Enhanced security",
                    "Improved scalability"
                ],
                implementation_effort="low"
            ))
        
        return optimizations
        
    except Exception as e:
        logger.error(f"Error suggesting system optimizations: {e}")
        return [SystemOptimization(
            area="error",
            current_state="Error in analysis",
            optimization_suggestions=["Review system state data format"],
            expected_benefits=["Improved analysis capabilities"],
            implementation_effort="unknown"
        )]


@tool
def generate_learning_report(insights: List[LearningInsight], metrics: List[PerformanceMetric], optimizations: List[SystemOptimization]) -> Dict[str, Any]:
    """
    Generate a comprehensive learning report from all analysis results.
    
    Args:
        insights: List of learning insights
        metrics: List of performance metrics
        optimizations: List of system optimizations
        
    Returns:
        Dictionary with comprehensive learning report
    """
    try:
        logger.info("Generating comprehensive learning report")
        
        # Calculate summary statistics
        total_insights = len(insights)
        critical_insights = len([i for i in insights if i.priority == "critical"])
        high_priority_insights = len([i for i in insights if i.priority == "high"])
        
        # Identify top recommendations
        top_recommendations = []
        for insight in insights[:3]:  # Top 3 insights
            top_recommendations.append({
                "pattern": insight.pattern,
                "suggestion": insight.suggestion,
                "priority": insight.priority,
                "confidence": insight.confidence
            })
        
        # Performance summary
        performance_summary = {
            "total_metrics": len(metrics),
            "metrics_needing_attention": len([m for m in metrics if m.current_value > m.target_value]),
            "improving_trends": len([m for m in metrics if m.trend == "improving"]),
            "declining_trends": len([m for m in metrics if m.trend == "declining"])
        }
        
        # Optimization summary
        optimization_summary = {
            "total_areas": len(optimizations),
            "high_effort_optimizations": len([o for o in optimizations if o.implementation_effort == "high"]),
            "low_effort_optimizations": len([o for o in optimizations if o.implementation_effort == "low"])
        }
        
        return {
            "report_generated": datetime.now().isoformat(),
            "summary": {
                "total_insights": total_insights,
                "critical_insights": critical_insights,
                "high_priority_insights": high_priority_insights,
                "performance_issues": performance_summary["metrics_needing_attention"],
                "optimization_areas": optimization_summary["total_areas"]
            },
            "top_recommendations": top_recommendations,
            "performance_summary": performance_summary,
            "optimization_summary": optimization_summary,
            "priority_actions": [
                "Address critical insights immediately",
                "Implement high-priority optimizations",
                "Monitor performance metrics closely",
                "Plan for long-term system improvements"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error generating learning report: {e}")
        return {
            "error": str(e),
            "report_generated": datetime.now().isoformat(),
            "summary": {},
            "top_recommendations": [],
            "performance_summary": {},
            "optimization_summary": {},
            "priority_actions": ["Review analysis process and data format"]
        }


shadow_learning_agent = Agent(
    name="Shadow Learning Agent",
    instructions="""You observe traces and logs to suggest improvements automatically in FreelanceX.AI.

Your responsibilities include:
- Analyzing system logs for patterns and issues
- Monitoring performance metrics and trends
- Suggesting system optimizations
- Generating comprehensive learning reports
- Providing proactive improvement recommendations

Always focus on actionable insights and measurable improvements.""",
    tools=[analyze_logs, analyze_performance_metrics, suggest_system_optimizations, generate_learning_report],
)


