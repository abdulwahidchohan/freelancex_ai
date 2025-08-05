# Scans freelance platforms for jobs
class JobHunterAgent:
    def __init__(self):
        self.supported_platforms = ['Upwork', 'Freelancer', 'Fiverr']
        self.search_filters = {
            'keywords': [],
            'budget_range': {'min': 0, 'max': float('inf')},
            'job_type': 'All'
        }

    def set_search_filters(self, keywords=None, min_budget=0, max_budget=None, job_type='All'):
        """Set search filters for job hunting"""
        if keywords:
            self.search_filters['keywords'] = keywords
        self.search_filters['budget_range']['min'] = min_budget
        self.search_filters['budget_range']['max'] = max_budget if max_budget else float('inf')
        self.search_filters['job_type'] = job_type

    def find_jobs(self, platform=None):
        """
        Search for jobs across supported freelance platforms
        Args:
            platform (str, optional): Specific platform to search. If None, searches all platforms
        Returns:
            list: List of job opportunities
        """
        print(f"JobHunterAgent: Searching for new job opportunities...")
        if platform and platform not in self.supported_platforms:
            raise ValueError(f"Unsupported platform. Please choose from {self.supported_platforms}")

        # In a real scenario, this would involve scraping job boards or using job APIs
        sample_jobs = [
            {
                "title": "AI Engineer",
                "company": "Tech Corp",
                "platform": "Upwork",
                "budget": 5000,
                "description": "Looking for an AI engineer to develop ML models",
                "skills_required": ["Python", "Machine Learning", "TensorFlow"],
                "posted_date": "2024-03-20"
            },
            {
                "title": "Freelance Developer",
                "company": "Self-Employed",
                "platform": "Freelancer",
                "budget": 3000,
                "description": "Web application development project",
                "skills_required": ["JavaScript", "React", "Node.js"],
                "posted_date": "2024-03-19"
            }
        ]

        # Apply filters
        filtered_jobs = self._apply_filters(sample_jobs)
        
        return filtered_jobs

    def _apply_filters(self, jobs):
        """Apply search filters to job listings"""
        filtered = jobs
        
        # Filter by keywords
        if self.search_filters['keywords']:
            filtered = [
                job for job in filtered
                if any(keyword.lower() in job['title'].lower() or 
                      keyword.lower() in job['description'].lower()
                      for keyword in self.search_filters['keywords'])
            ]
        
        # Filter by budget range
        filtered = [
            job for job in filtered
            if self.search_filters['budget_range']['min'] <= job['budget'] <= self.search_filters['budget_range']['max']
        ]
        
        return filtered
