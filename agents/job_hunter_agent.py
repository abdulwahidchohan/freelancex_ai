from core.base_agent import BaseAgent
import requests
import json

# Scans freelance platforms for jobs
class JobHunterAgent(BaseAgent):
    def __init__(self):
        super().__init__("JobHunterAgent")
        self.platforms = ["Fiverr", "Upwork", "Freelancer"]
        self.jobs_file = "data/jobs.json"

    def run(self):
        print(f'{self.agent_name} online.')
        print(f"System Prompt loaded: {self.system_prompt[:50]}...") # For verification
        self.find_jobs()

    def find_jobs(self):
        jobs = []
        for platform in self.platforms:
            try:
                # Simulate API call to platform
                response = requests.get(f"https://api.{platform.lower()}.com/jobs")
                if response.status_code == 200:
                    jobs.extend(response.json())
            except Exception as e:
                print(f"Error fetching jobs from {platform}: {e}")

        # Save jobs to file
        try:
            with open(self.jobs_file, 'w') as f:
                json.dump(jobs, f, indent=4)
            print(f"Jobs saved to {self.jobs_file}.")
        except Exception as e:
            print(f"Error saving jobs to file: {e}")
