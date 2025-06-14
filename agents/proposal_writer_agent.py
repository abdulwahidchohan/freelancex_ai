# Writes tailored proposals
class ProposalWriterAgent:
    def __init__(self):
        self.proposal_templates = {
            'default': "I am excited to apply for this opportunity...",
            'technical': "With my strong technical background...",
            'creative': "As a creative professional..."
        }

    def analyze_job(self, job_description):
        """Analyzes the job description to determine key requirements and tone."""
        # Add logic to analyze job keywords, requirements, and preferred tone
        return {
            'keywords': [],
            'requirements': [],
            'tone': 'default'
        }

    def select_template(self, analysis):
        """Selects the most appropriate template based on job analysis."""
        return self.proposal_templates.get(analysis['tone'], self.proposal_templates['default'])

    def customize_proposal(self, template, job_description, analysis):
        """Customizes the selected template with job-specific details."""
        # Add logic to incorporate job details and requirements
        return template.replace("[JOB_DETAILS]", job_description)

    def write(self, job_description):
        """Generates a tailored proposal for the given job description."""
        print(f"ProposalWriterAgent: Writing proposal for job: {job_description}...")
        
        analysis = self.analyze_job(job_description)
        template = self.select_template(analysis)
        proposal = self.customize_proposal(template, job_description, analysis)
        
        return proposal
