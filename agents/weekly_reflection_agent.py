# Performance review
class WeeklyReflection:
    def __init__(self):
        self.activities = []
        self.achievements = []
        self.improvements = []

    def add_activity(self, activity):
        self.activities.append(activity)

    def add_achievement(self, achievement):
        self.achievements.append(achievement)

    def add_improvement_area(self, area):
        self.improvements.append(area)

    def generate_report(self):
        print("WeeklyReflection: Generating weekly reflection report...")
        
        report = "Weekly Reflection Report\n"
        report += "=" * 25 + "\n\n"
        
        report += "Activities:\n"
        for idx, activity in enumerate(self.activities, 1):
            report += f"{idx}. {activity}\n"
        
        report += "\nAchievements:\n"
        for idx, achievement in enumerate(self.achievements, 1):
            report += f"{idx}. {achievement}\n"
            
        report += "\nAreas for Improvement:\n"
        for idx, improvement in enumerate(self.improvements, 1):
            report += f"{idx}. {improvement}\n"
            
        report += "\nReport generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return report
