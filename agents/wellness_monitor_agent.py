# Health tracking
class WellnessMonitorAgent:
    def __init__(self):
        self.health_metrics = {
            "heart_rate": None,
            "sleep_hours": None,
            "steps": None,
            "stress_level": None,
            "water_intake": None
        }

    def update_metrics(self, metrics_dict):
        """Update health metrics with new data"""
        for metric, value in metrics_dict.items():
            if metric in self.health_metrics:
                self.health_metrics[metric] = value

    def analyze_metrics(self):
        """Analyze current health metrics and generate insights"""
        insights = []
        if all(v is None for v in self.health_metrics.values()):
            return "No health data available"

        # Example analysis logic
        if self.health_metrics["sleep_hours"] is not None:
            if self.health_metrics["sleep_hours"] < 7:
                insights.append("Consider getting more sleep")
            elif self.health_metrics["sleep_hours"] > 9:
                insights.append("You might be oversleeping")

        if self.health_metrics["steps"] is not None and self.health_metrics["steps"] < 5000:
            insights.append("Try to increase daily physical activity")

        return insights

    def check_health(self):
        """Check health metrics and provide personalized recommendations"""
        print("WellnessMonitorAgent: Analyzing health metrics...")
        
        insights = self.analyze_metrics()
        
        if not insights:
            status = "Good"
            recommendations = "Keep up the good work!"
        else:
            status = "Needs Attention"
            recommendations = " | ".join(insights)

        return {
            "status": status,
            "recommendations": recommendations,
            "metrics": self.health_metrics
        }

    def get_wellness_score(self):
        """Calculate an overall wellness score based on metrics"""
        if all(v is None for v in self.health_metrics.values()):
            return 0
            
        score = 0
        metrics_count = 0
        
        # Simple scoring example
        if self.health_metrics["sleep_hours"]:
            score += min(100, (self.health_metrics["sleep_hours"] / 8) * 100)
            metrics_count += 1
            
        if self.health_metrics["steps"]:
            score += min(100, (self.health_metrics["steps"] / 10000) * 100)
            metrics_count += 1
            
        return round(score / max(1, metrics_count))
